# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# All rights reserved. Unauthorised use, copying, or distribution is prohibited.
# Contact kemar.christie@yahoo.com, robertojames91@gmail.com, dwaynelgibbs@gmail.com, davistyo384@gmail.com & Jonesdanielle236@yahoo.com for licensing inquiries.
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import requests
import json
from datetime import datetime, timedelta
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AmadeusAPI:
    """
    A client for the Amadeus Travel API that provides methods to search for flights
    and related travel information.
    
    This class handles authentication, API requests with retry logic, and storing results
    to JSON files. It can work with both test and production Amadeus environments.
    """
    def __init__(self, client_id=None, client_secret=None, is_test=None, output_dir=None):
        """
        Initialize the Amadeus API client.
        
        Args:
            client_id (str, optional): Amadeus API client ID. If None, reads from environment variable.
            client_secret (str, optional): Amadeus API client secret. If None, reads from environment variable.
            is_test (bool, optional): Whether to use test API endpoints. If None, reads from environment variable.
            output_dir (str, optional): Directory to store output files. If None, reads from environment variable.
        
        Raises:
            ValueError: If client_id or client_secret are not provided and not in environment variables.
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
            
        # Set base URL based on whether we're using test or production environment
        self.base_url = "test.api.amadeus.com" if self.is_test else "api.amadeus.com"
        
        # Initialize authentication token variables
        self.token = None
        self.token_expiry = None
        
        # Create base output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create Json subdirectory for storing results
        self.json_dir = os.path.join(self.output_dir, "Json")
        os.makedirs(self.json_dir, exist_ok=True)
        
    def _get_auth_token(self):
        """
        Get an authentication token from the Amadeus API.
        
        Returns:
            str: The valid OAuth2 access token.
            
        Raises:
            Exception: If authentication fails.
            
        Notes:
            - Automatically reuses existing token if still valid
            - Sets token expiry with a 5-minute safety buffer
        """
        # Return existing token if it's still valid
        if self.token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.token
            
        # Otherwise, request a new token
        url = f"https://{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        # Make the authentication request
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data["access_token"]
            # Set expiry time (subtract 5 minutes to be safe)
            self.token_expiry = datetime.now() + timedelta(seconds=token_data["expires_in"] - 300)
            return self.token
        else:
            raise Exception(f"Authentication failed: {response.text}")

    def _make_request(self, method, endpoint, params=None, data=None, max_retries=3):
        """
        Make a request to the Amadeus API with automatic retries for failures.
        
        Args:
            method (str): HTTP method to use (GET or POST)
            endpoint (str): API endpoint (starting with /)
            params (dict, optional): Query parameters for GET requests
            data (dict, optional): JSON body for POST requests
            max_retries (int, optional): Maximum number of retry attempts. Defaults to 3.
            
        Returns:
            dict: JSON response from the API
            
        Raises:
            ValueError: If an unsupported HTTP method is provided
            Exception: If all retry attempts fail
            
        Notes:
            - Implements exponential backoff for retries
            - Handles rate limiting with Retry-After header
            - Automatically refreshes authentication token when needed
        """
        # Get a valid authentication token
        token = self._get_auth_token()
        url = f"https://{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {token}"}
        
        retries = 0
        while retries < max_retries:
            try:
                # Make the appropriate type of request
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    headers["Content-Type"] = "application/json"
                    response = requests.post(url, headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle rate limiting (429 Too Many Requests)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                    
                # Handle server errors (5xx) with exponential backoff
                elif 500 <= response.status_code < 600:
                    retries += 1
                    wait_time = 2 ** retries  # Exponential backoff: 2, 4, 8... seconds
                    print(f"Server error (status {response.status_code}). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                    
                # For successful responses or client errors that aren't rate limiting
                else:
                    response.raise_for_status()  # Raise exception for 4xx (except 429) and 5xx
                    return response.json()
                    
            except requests.exceptions.RequestException as e:
                # Handle network errors with retry logic
                retries += 1
                if retries < max_retries:
                    wait_time = 2 ** retries
                    print(f"Request error: {e}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed after {max_retries} attempts: {e}")
                    
        # If we've exhausted all retries
        raise Exception(f"Failed after {max_retries} attempts")
    
    def search_city_code(self, city_name):
        """
        Search for the IATA city code by city name.
        
        Args:
            city_name (str): Name of the city to search for
            
        Returns:
            str or None: IATA code for the city if found, None otherwise
            
        Notes:
            - Uses the locations API to find the best matching city
            - Filters results to CITY subtype only
        """
        # Set up parameters for city search
        params = {
            "keyword": city_name,
            "subType": "CITY"  # Only return cities, not airports or other location types
        }
        
        # Make the API request
        response = self._make_request("GET", "/v1/reference-data/locations", params=params)
        
        # Check if we got any results
        if not response.get("data") or len(response["data"]) == 0:
            print(f"No city found for '{city_name}'")
            return None
            
        # Return the IATA code of the first (best) match
        return response["data"][0]["iataCode"]
    
    def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, travel_class="ECONOMY", non_stop=False, currency="JMD"):
        """
        Search for flights between two locations.
        
        Args:
            origin (str): IATA code of the origin location
            destination (str): IATA code of the destination location
            departure_date (str): Departure date in YYYY-MM-DD format
            return_date (str, optional): Return date in YYYY-MM-DD format. If provided, searches for round-trip flights.
            adults (int, optional): Number of adult passengers. Defaults to 1.
            travel_class (str, optional): Travel class. Defaults to "ECONOMY".
            non_stop (bool, optional): Whether to only return non-stop flights. Defaults to False.
            currency (str, optional): Currency code for prices. Defaults to "JMD".
            
        Returns:
            dict: JSON response containing flight offers
        """
        # Set up parameters for flight search
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": adults,
            "currencyCode": currency,
            "travelClass": travel_class,
            "nonStop": "true" if non_stop else "false",
            "max": 20  # Number of results to return
        }
        
        # Add return date for round trips
        if return_date:
            params["returnDate"] = return_date
        
        # Make the API request and return results
        return self._make_request("GET", "/v2/shopping/flight-offers", params=params)
    
    def sort_flights_by_price(self, flight_results):
        """
        Sort flight offers by total price from lowest to highest.
        
        Args:
            flight_results (dict): Flight search results from search_flights()
            
        Returns:
            list: Sorted list of flight offers, or empty list if no results
        """
        # Check if we have any flight offers
        if not flight_results.get("data"):
            return []
        
        # Sort flights by total price (converting string to float)
        return sorted(flight_results["data"], 
                      key=lambda x: float(x["price"]["total"]))

    def save_results_to_json(self, data, filename):
        """
        Save data to a JSON file in the output directory.
        
        Args:
            data: Data to save (must be JSON serializable)
            filename (str): Name of the file to save the data to
            
        Notes:
            - Files are saved to the Json subdirectory in the output directory
            - Prints confirmation message with the output path
        """
        # Combine the Json directory with the filename
        output_path = os.path.join(self.json_dir, filename)
        
        # Write the data to the file with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, indent=2, fp=f)
        print(f"Data saved to {output_path}")

def pretty_print_flights(flights):
    """
    Format and print flight information in a human-readable way.
    
    Args:
        flights (list): List of flight offers from the API
        
    Notes:
        - Displays price and currency
        - Shows outbound and return flight details
        - Includes duration and segment information
        - Limited to showing the top 10 results
    """
    print(f"\nFound {len(flights)} flights:")
    for i, flight in enumerate(flights[:10], 1):  # Show top 10 flights only
        # Print price information
        price = flight["price"]["total"]
        currency = flight["price"]["currency"]
        
        print(f"{i}. Price: {price} {currency}")
        
        # Loop through itineraries (outbound and potentially return)
        for j, itinerary in enumerate(flight["itineraries"]):
            flight_type = "Outbound" if j == 0 else "Return"
            print(f"   {flight_type} - Duration: {itinerary['duration']}")
            
            # Loop through flight segments within each itinerary
            for k, segment in enumerate(itinerary["segments"], 1):
                dep = segment["departure"]
                arr = segment["arrival"]
                print(f"      Segment {k}: {dep['iataCode']} ({dep['at']}) → {arr['iataCode']} ({arr['at']})")


# Example usage demonstration
if __name__ == "__main__":
    # Initialize API client using environment variables from .env file
    api = AmadeusAPI()

    """
    # Example of searching for a city's IATA code
    # Uncomment to test this functionality
    iata_code = api.search_city_code("New York")
    print(f"IATA code: {iata_code}")
    """
    
    # Example of searching for flights
    flights = api.search_flights(
        origin="MBJ",  # Montego Bay, Jamaica
        destination="MIA",  # Miami, Florida
        departure_date="2025-07-30",  # Outbound flight date
        return_date="2025-10-05",  # Return flight date
        adults=1,  # Number of passengers
    )

    # Sort the flights by price (lowest to highest)
    sorted_flights = api.sort_flights_by_price(flights)

    # Print the results in a readable format
    pretty_print_flights(sorted_flights)

    # Save the results to the neural-booker-output/Json folder
    api.save_results_to_json(sorted_flights, "flights.json")