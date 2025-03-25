# Copyright (c) 2025 Kemar Christie, Roberto james, Dwayne Gibbs, Tyoni Davis, Danielle Jones
# All rights reserved. Unauthorised use, copying, or distribution is prohibited.
# Contact kemar.christie@yahoo.com, robertojames91@gmail.com, dwaynelgibbs@gmail.com, davistyo384@gmail.com & Jonesdanielle236@yahoo.com for licensing inquiries.
# Authors: Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones

import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class KnutsfordFaresScraper:
    def __init__(self, output_dir=os.path.join("neural-booker-output", "json")):
        """
        Initialize the scraper with output directory.
        
        Args:
            output_dir (str): Path to the JSON output directory
        """
        # Construct the full path relative to the script's location
        self.json_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), output_dir))
        
        # Ensure output directory exists
        os.makedirs(self.json_dir, exist_ok=True)
        print(f"Output directory set to: {self.json_dir}")

    def setup_webdriver(self):
        """
        Setup and configure Chrome WebDriver in headless mode.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("Starting browser...")
        return webdriver.Chrome(options=chrome_options)

    def scrape_fares(self):
        """
        Scrape fare information from Knutsford Express website.
        
        Returns:
            list: Extracted fare data or None if scraping fails
        """
        driver = self.setup_webdriver()
        
        try:
            # Navigate to the fare table page
            url = 'https://www.knutsfordexpress.com/fare-schedule/fare-table/'
            print(f"Navigating to {url}...")
            driver.get(url)
            
            # Wait for the page to load completely
            print("Waiting for page to load completely...")
            time.sleep(5)  # Initial wait to ensure page loads

            # Wait for the div with class="table" and id="results"
            print("Looking for div-based table...")
            wait = WebDriverWait(driver, 15)
            table_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.table#results')))
            print("Found div-based table!")
            
            # Get table rows (div elements with class="table_row")
            rows = driver.find_elements(By.CSS_SELECTOR, 'div.table_row')
            print(f"Found {len(rows)} table rows.")
            
            if len(rows) == 0:
                print("No table rows found. Waiting longer...")
                time.sleep(5)  # Wait longer for JavaScript to finish
                rows = driver.find_elements(By.CSS_SELECTOR, 'div.table_row')
                print(f"After waiting: Found {len(rows)} table rows.")
                
                if len(rows) == 0:
                    # Try JavaScript to get rows
                    print("Trying to get rows via JavaScript...")
                    try:
                        js_rows = driver.execute_script("return document.querySelectorAll('div.table_row');")
                        print(f"Found {len(js_rows)} rows via JavaScript.")
                        rows = js_rows
                    except Exception as e:
                        print(f"Error getting rows via JavaScript: {e}")
            
            if len(rows) == 0:
                print("Still no rows found. Taking screenshot for debugging...")
                driver.save_screenshot("debug_screenshot.png")
                print("Screenshot saved as debug_screenshot.png")
                return None
                
            # Extract data from rows
            fare_data = []
            
            # Identify the header row to determine column indices
            header_cells = rows[0].find_elements(By.CSS_SELECTOR, 'div.table_cell')
            header_texts = [cell.text.strip().lower() for cell in header_cells]
            print(f"Header texts: {header_texts}")
            
            # Define expected column positions (with fallbacks)
            try:
                route_idx = next((i for i, text in enumerate(header_texts) if 'route' in text), 0)
                discount_idx = next((i for i, text in enumerate(header_texts) if 'discount' in text), 1)
                adult_idx = next((i for i, text in enumerate(header_texts) if 'adult' in text), 2)
                child_idx = next((i for i, text in enumerate(header_texts) if 'child' in text), 3)
                senior_idx = next((i for i, text in enumerate(header_texts) if 'senior' in text), 4)
                student_idx = next((i for i, text in enumerate(header_texts) if 'student' in text), 5)
                
                print(f"Column indices - Route: {route_idx}, Discount: {discount_idx}, Adult: {adult_idx}, "
                     f"Child: {child_idx}, Senior: {senior_idx}, Student: {student_idx}")
            except Exception as e:
                print(f"Error identifying column indices: {e}")
                # Default to sequential indices if header detection fails
                route_idx, discount_idx, adult_idx, child_idx, senior_idx, student_idx = 0, 1, 2, 3, 4, 5
            
            # Skip the header row
            for row in rows[1:]:
                cells = row.find_elements(By.CSS_SELECTOR, 'div.table_cell')
                
                if len(cells) >= max(route_idx, discount_idx, adult_idx, child_idx, senior_idx, student_idx) + 1:
                    # Debug each row
                    cell_texts = [cell.text.strip() for cell in cells]
                    print(f"Row data: {cell_texts}")
                    
                    # Get values using identified indices, with safety checks
                    route = cells[route_idx].text.strip() if route_idx < len(cells) else ""
                    discount = cells[discount_idx].text.strip() if discount_idx < len(cells) else ""
                    adult = cells[adult_idx].text.strip() if adult_idx < len(cells) else ""
                    child = cells[child_idx].text.strip() if child_idx < len(cells) else ""
                    senior = cells[senior_idx].text.strip() if senior_idx < len(cells) else ""
                    student = cells[student_idx].text.strip() if student_idx < len(cells) else ""
                    
                    # Skip rows with empty route
                    if not route:
                        print("Skipping row with empty route")
                        continue
                    
                    # Additional validation - if route doesn't have a $ sign but discount does,
                    # they might be swapped
                    if '$' not in route and '$' in discount:
                        print(f"Potential column swap detected in row: {route} / {discount}")
                        # Check if we have a consistent pattern of columns being shifted
                        if len(fare_data) > 0:
                            # Don't auto-correct; just warn
                            print("WARNING: Data might be misaligned. Please verify column mapping.")
                    
                    fare_data.append({
                        'Route': route,
                        'Online_Discount': discount,
                        'Adult': adult,
                        'Child': child,
                        'Senior': senior,
                        'Student': student
                    })
                    print(f"Added route: {route}")
            
            if not fare_data:
                print("No route data extracted from the rows.")
                return None
            
            print(f"Successfully scraped {len(fare_data)} routes.")
            return fare_data
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # Close the browser
            driver.quit()
            print("Browser closed.")

    def save_results_to_json(self, data, filename):
        """
        Save results to a JSON file in the output directory.
        
        Args:
            data (list): The data to be saved to JSON
            filename (str): Name of the JSON file to be created
        """
        # Use the full path directly
        output_path = os.path.join(self.json_dir, filename)
       
        try:
            # Save the JSON file with indentation
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"Data saved to {output_path}")
            
            # Verify file exists and print its size
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"File size: {file_size} bytes")
            
            return True
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False

def main():
    # Print Python version for debugging
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Create scraper instance with relative path
    scraper = KnutsfordFaresScraper()
    
    # Scrape the fare data
    fare_data = scraper.scrape_fares()
    
    if fare_data is not None:
        # Display the number of routes found
        print(f"\nTotal routes scraped: {len(fare_data)}")
        
        # Display the first few entries
        print("\nSample of the scraped data:")
        for i, route in enumerate(fare_data[:3]):
            print(f"{i+1}. {route['Route']}: Adult: {route['Adult']}, Child: {route['Child']}")
        
        # Validate data before saving
        print("\nValidating data...")
        issues_found = False
        for i, item in enumerate(fare_data):
            route = item['Route']
            if not route or '$' in route:
                print(f"Potential issue in entry {i+1}: Route '{route}' may be incorrect")
                issues_found = True
        
        if issues_found:
            print("\nWARNING: Potential data quality issues detected. You may need to manually verify the results.")
        
        # Save the results
        scraper.save_results_to_json(fare_data, "knutsford_fares.json")
        print("Saved")
    else:
        print("No fare data could be scraped.")


if __name__ == "__main__":
    main()