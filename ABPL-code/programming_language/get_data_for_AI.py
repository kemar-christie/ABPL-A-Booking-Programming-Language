# Copyright (c) 2025 Kemar Christie & Roberto James
# Authors: Kemar Christie & Roberto James

import json
import os

def getKnutsfordDetails():
    """
    Fetches Knutsford Express data from a JSON file.

    Returns:
        str: A JSON string containing the Knutsford Express data, or None if an error occurs.
    """
    file_path = "neural-booker-output/json/knutsford_data.json"  # Corrected path

    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)  # Return JSON string with indentation for readability
    except FileNotFoundError:
        print(f"Error: JSON data file not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == '__main__':
    knutsford_data = getKnutsfordDetails()
    if knutsford_data:
        print("Knutsford Express Data:")
        print(knutsford_data)
    else:
        print("Failed to retrieve Knutsford Express data.")