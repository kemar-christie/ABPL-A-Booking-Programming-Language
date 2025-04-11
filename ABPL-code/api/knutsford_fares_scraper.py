# Copyright (c) 2025 Kemar Christie, Roberto James, Dwayne Gibbs, Tyoni Davis, Danielle Jones
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
    
    def __init__(self, output_dir=os.path.join("../../ABPL-output", "json")):
        """
        Initialize the scraper with output directory.
        
        Args:
            output_dir (str): Path to the JSON output directory
        """
        # Construct the full path relative to the script's location
        self.json_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), output_dir))
        
        # Ensure output directory exists
        os.makedirs(self.json_dir, exist_ok=True)
        #print(f"Output directory set to: {self.json_dir}")

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
        chrome_options.add_argument("--remote-debugging-options=0")  # Suppress DevTools message
        

        chrome_options.add_argument("--log-level=3")  # 3 = LOG_FATAL. 0 = LOG_INFO, 1 = LOG_WARNING, 2 = LOG_ERROR, 3 = LOG_FATAL

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
            #print(f"Navigating to {url}...")
            driver.get(url)

            # Wait for the page to load completely
            #print("Waiting for page to load completely...")
            time.sleep(5)  # Initial wait to ensure page loads

            # Get table rows (div elements with class="table_row")
            rows = driver.find_elements(By.CSS_SELECTOR, 'div.table_row')
            #print(f"Found {len(rows)} table rows.")
            
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
                
            
            # Identify the header row to determine column indices
            header_cells = rows[0].find_elements(By.CSS_SELECTOR, 'div.table_cell')
            header_texts = [cell.text.strip().lower() for cell in header_cells]
            #print(f"Header texts: {header_texts}")
            
            # Define expected column positions (with fallbacks)
            try:
                route = next((i for i, text in enumerate(header_texts) if 'route' in text), 0)
                discount_idx = next((i for i, text in enumerate(header_texts) if 'discount' in text), 1)
                adult_idx = next((i for i, text in enumerate(header_texts) if 'adult' in text), 2)
                child_idx = next((i for i, text in enumerate(header_texts) if 'child' in text), 3)
                senior_idx = next((i for i, text in enumerate(header_texts) if 'senior' in text), 4)
                student_idx = next((i for i, text in enumerate(header_texts) if 'student' in text), 5)
                
                #print(f"Column indices - Route: {route}, Discount: {discount_idx}, Adult: {adult_idx}, "f"Child: {child_idx}, Senior: {senior_idx}, Student: {student_idx}")
            except Exception as e:
                print(f"Error identifying column indices: {e}")
                # Default to sequential indices if header detection fails
                route, discount_idx, adult_idx, child_idx, senior_idx, student_idx = 0, 1, 2, 3, 4, 5
            
            # Skip the header row
            print("Scraping Knutsford Express...")

            
            num=1
            routeID="RTE"
            all_data = []
            for row in rows[1:]:
                cells = row.find_elements(By.CSS_SELECTOR, 'div.table_cell')
                

                if len(cells) >= max(route, discount_idx, adult_idx, child_idx, senior_idx, student_idx) + 1:
                    
                    # Debug each row
                    cell_texts = [cell.text.strip() for cell in cells if cell.text.strip() != '']
                    

                    json_file_path = os.path.join(self.json_dir, "knutsford_data.json")
                    
                    # Create the route ID
                    formatted_num = str(num).zfill(3)  # Pad with leading zeros
                    full_route_id = routeID + formatted_num
                    # Prepare data to be appended
                    data_to_append = {
                        "RouteID": full_route_id,
                        "Route": cell_texts[0] if len(cell_texts) > 0 else "",
                        "Online Discount": cell_texts[1] if len(cell_texts) > 1 else "",
                        "Adult": cell_texts[2] if len(cell_texts) > 2 else "",
                        "Child": cell_texts[3] if len(cell_texts) > 3 else "",
                        "Senior": cell_texts[4] if len(cell_texts) > 4 else "",
                        "Student": cell_texts[5] if len(cell_texts) > 5 else "",
                    }
                    
                    all_data.append(data_to_append) # Append the data to the list
                    num += 1  # Increment the counter for the next RouteID

                # Write all data to the JSON file *after* the loop is finished
                with open(json_file_path, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=4, ensure_ascii=False)
    
            return None
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        finally:
            # Close the browser
            driver.quit()
            print("Done.....")

def main():

    # Create scraper instance with relative path
    scraper = KnutsfordFaresScraper()
    
    # Scrape the fare data
    scraper.scrape_fares()
    

if __name__ == "__main__":
    main()