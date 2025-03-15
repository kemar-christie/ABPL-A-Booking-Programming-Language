import requests
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AmadeusAPI:
    def __init__(self, client_id=None, client_secret=None, is_test=None, output_dir=None):
        """Initialize the Amadeus API client.
        
        Args:
            client_id (str, optional): Your Amadeus API key. If None, will try to get from environment
            client_secret (str, optional): Your Amadeus API secret. If None, will try to get from environment
            is_test (bool, optional): Whether to use test environment. If None, will try to get from environment
            output_dir (str, optional): Base directory for output files. If None, will try to get from environment
        """
        # Get credentials from parameters or environment variables
        self.client_id = client_id or os.environ.get('AMADEUS_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('AMADEUS_CLIENT_SECRET')
        
        # Get is_test from parameter or environment variable (default to True if not specified)
        if is_test is None:
            is_test_env = os.environ.get('AMADEUS_IS_TEST', 'true').lower()
            self.is_test = is_test_env in ('true', 'yes', '1', 't')
        else:
            self.is_test = is_test
            
        # Get output directory from parameter or environment variable (default if not specified)
        self.output_dir = output_dir or os.environ.get('OUTPUT_DIR', 'neural-booker-output')
        
        # Validate credentials exist
        if not self.client_id or not self.client_secret:
            raise ValueError("Amadeus API credentials not provided. Set them as parameters or environment variables.")
            
        self.base_url = "test.api.amadeus.com" if self.is_test else "api.amadeus.com"
        self.token = None
        self.token_expiry = None
        
        # Create base output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create Json subdirectory
        self.json_dir = os.path.join(self.output_dir, "Json")
        os.makedirs(self.json_dir, exist_ok=True)
        
    def _get_auth_token(self):
        """Get an authentication token from the Amadeus API."""
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
            
        url = f"https://{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            # Set expiry time (subtract 5 minutes to be safe)
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 300)
            return self.token
        else:
            raise Exception(f"Authentication failed: {response.text}")

    # Rest of the AmadeusAPI class methods remain unchanged
    def _make_request(self, method, endpoint, params=None, data=None, max_retries=3):
        """Make a request to the Amadeus API with automatic retries."""
        token = self._get_auth_token()
        url = f"https://{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        
        retries = 0
        while retries < max_retries:
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Check if we need to handle rate limiting
                if response.status_code == 429:  # Too Many Requests
                    retry_after = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                    
                # For server errors, retry
                elif 500 <= response.status_code < 600:
                    retries += 1
                    wait_time = 2 ** retries  # Exponential backoff
                    print(f"Server error (status {response.status_code}). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                # For successful responses or client errors that aren't rate limiting
                else:
                    response.raise_for_status()  # Raise exception for 4xx (except 429) and 5xx
                    return response.json()
                    
            except requests.exceptions.RequestException as e:
                # For network errors, retry
                retries += 1
                if retries < max_retries:
                    wait_time = 2 ** retries
                    print(f"Request error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {e}")
                    
        # If we've exhausted retries
        raise Exception(f"Failed after {max_retries} attempts")
    
    def search_city_code(self, city_name):
        """Search for a city's IATA code.
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            str: IATA city code
        """
        params = {
            "keyword": city_name,
            "subType": "CITY"
        }
        
        response = self._make_request("GET", "/v1/reference-data/locations", params=params)
        
        if not response.get("data") or len(response["data"]) == 0:
            print(f"No city found for '{city_name}'")
            return None
            
        # Return the IATA code of the first (best) match
        return response["data"][0]["iataCode"]
    
    def search_hotels(self, city_code, check_in_date, check_out_date, adults=1, rooms=1, currency="JMD", hotel_rating=None):
        """Search for hotels in a specific city."""
        params = {
            "cityCode": city_code,
            "checkInDate": check_in_date,
            "checkOutDate": check_out_date,
            "adults": adults,
            "roomQuantity": rooms,
            "currency": currency,
            "bestRateOnly": "true",
            "view": "FULL"  # Get full details
        }
        
        # Add hotel rating filter if specified
        if hotel_rating:
            params["ratings"] = ",".join(str(rating) for rating in hotel_rating)
        
        return self._make_request("GET", "/v2/shopping/hotel-offers", params=params)
    
    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, travel_class="ECONOMY", non_stop=False, currency="JMD"):
        """Search for flights between two cities."""
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": currency,
            "travelClass": travel_class,
            "nonStop": "true" if non_stop else "false",
            "max": 20  # Number of results
        }
        
        # Add return date for round trips
        if return_date:
            params["returnDate"] = return_date
        
        return self._make_request("GET", "/v2/shopping/flight-offers", params=params)
    
    def get_hotel_offer_details(self, offer_id):
        """Get detailed information about a specific hotel offer."""
        return self._make_request("GET", f"/v2/shopping/hotel-offers/{offer_id}")
    
    def sort_hotels_by_price(self, hotel_results):
        """Sort hotel offers by price (low to high)."""
        if not hotel_results.get("data"):
            return []
        
        return sorted(hotel_results["data"], 
                      key=lambda x: float(x["offers"][0]["price"]["total"]))
    
    def sort_flights_by_price(self, flight_results):
        """Sort flight offers by price (low to high)."""
        if not flight_results.get("data"):
            return []
        
        return sorted(flight_results["data"], 
                      key=lambda x: float(x["price"]["total"]))

    def save_results_to_json(self, data, filename):
        """Save results to a JSON file in the output directory."""
        # Combine the Json directory with the filename
        output_path = os.path.join(self.json_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, indent=2, fp=f)
        print(f"Data saved to {output_path}")


def pretty_print_hotels(hotels):
    """Format and print hotel information in a readable way."""
    print(f"\nFound {len(hotels)} hotels:")
    for i, hotel in enumerate(hotels[:10], 1):  # Show top 10
        name = hotel["hotel"]["name"]
        rating = hotel["hotel"].get("rating", "N/A")
        price = hotel["offers"][0]["price"]["total"]
        currency = hotel["offers"][0]["price"]["currency"]
        
        print(f"{i}. {name} ({rating}★) - {price} {currency}")
        if "description" in hotel["hotel"]:
            desc = hotel["hotel"]["description"]["text"]
            print(f"   {desc[:100]}..." if len(desc) > 100 else f"   {desc}")

def pretty_print_flights(flights):
    """Format and print flight information in a readable way."""
    print(f"\nFound {len(flights)} flights:")
    for i, flight in enumerate(flights[:10], 1):  # Show top 10
        price = flight["price"]["total"]
        currency = flight["price"]["currency"]
        
        print(f"{i}. Price: {price} {currency}")
        for j, itinerary in enumerate(flight["itineraries"]):
            flight_type = "Outbound" if j == 0 else "Return"
            print(f"   {flight_type} - Duration: {itinerary['duration']}")
            
            for k, segment in enumerate(itinerary["segments"], 1):
                dep = segment["departure"]
                arr = segment["arrival"]
                print(f"      Segment {k}: {dep['iataCode']} ({dep['at']}) → {arr['iataCode']} ({arr['at']})")


# Example usage
if __name__ == "__main__":
    # Initialize API client using environment variables
    api = AmadeusAPI()

    """
    # Search for IATA code example
    iata_code = api.search_city_code("KIN")
    # Prin the result
    print(f"IATA code: {iata_code}")
    """
    
    # Search for flights 
    flights = api.search_flights(
        origin="MBJ",  # City IATA code
        destination="NYC",  # City IATA code
        departure_date="2025-07-30",  # Outbound flight date
        return_date="2025-10-05",  # Return flight date
        adults=1,  # Number of passengers
    )

    # Sort flights by price
    sorted_flights = api.sort_flights_by_price(flights)

    # Print results in a readable format
    pretty_print_flights(sorted_flights)

    # Save results to the neural-booker-output/Json folder
    api.save_results_to_json(sorted_flights, "flights.json")
    