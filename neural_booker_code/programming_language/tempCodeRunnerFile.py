    # Special handling for known Jamaican cities
        if city_name == "Kingston":
            return "KGN"
        elif city_name == "Montego Bay":
            return "MBJ"
        
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