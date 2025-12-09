# --- #

# Step 1 - State List
# https://locations.tacobell.com/
# state -> all hrefs from the class "Link DirLinks"

# Step 2 - County List
# https://locations.tacobell.com/ak.html
# county -> all hrefs from the class "Link DirLinks"

# Step 3 - Store List
# https://locations.tacobell.com/ak/anchorage.html
# store # -> href from the "View Store Page" button 

# Step 4 - Store List Details
# https://locations.tacobell.com/ak/anchorage/8825-old-seward-hwy.html
# store link -> link above
# store # -> get href from the "Start Your Order" button
# store location -> get href from the "Get Directions" button

# --- #

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
from tqdm import tqdm

def scrape_states():
    """
    Step 1: Scrape all state links from Taco Bell locations page
    """
    # Create Data folder if it doesn't exist
    os.makedirs("Data", exist_ok=True)
    
    # Check if states.json already exists
    if os.path.exists("Data/states.json"):
        print("states.json already exists. Loading existing data...")
        with open("Data/states.json", "r", encoding="utf-8") as f:
            states_data = json.load(f)
        print(f"Loaded {len(states_data)} states from existing file")
        return states_data
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Navigating to Taco Bell locations page...")
        driver.get("https://locations.tacobell.com/")
        
        # Wait for the page to load and find all links with class "Link DirLinks"
        print("Waiting for page to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "DirLinks"))
        )
        
        # Give it a moment to fully render
        time.sleep(2)
        
        # Find all links with the class "Link DirLinks"
        print("Finding state links...")
        state_links = driver.find_elements(By.CSS_SELECTOR, "a.Link.DirLinks")
        
        # Extract href and text from each link
        states_data = []
        for link in state_links:
            href = link.get_attribute("href")
            text = link.text.strip()
            if href:  # Only add if href exists
                states_data.append({
                    "state_name": text,
                    "state_url": href
                })
        
        print(f"Found {len(states_data)} states")
        
        # Save to JSON file
        with open("Data/states.json", "w", encoding="utf-8") as f:
            json.dump(states_data, f, indent=2, ensure_ascii=False)
        
        print("States data saved to Data/states.json")
        
        return states_data
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        driver.quit()
        print("Browser closed")

def scrape_counties():
    """
    Step 2: Scrape all county links for each state
    """
    # Create Data folder if it doesn't exist
    os.makedirs("Data", exist_ok=True)
      # Load states data
    if not os.path.exists("Data/states.json"):
        print("states.json not found. Running Step 1 first...")
        scrape_states()
    
    with open("Data/states.json", "r", encoding="utf-8") as f:
        states_data = json.load(f)
    
    # Count states that need scraping
    states_to_scrape = []
    for state in states_data:
        state_url = state["state_url"]
        state_initials = state_url.rstrip('/').split('/')[-1].replace('.html', '')
        county_file = f"Data/{state_initials}_counties.json"
        if not os.path.exists(county_file):
            states_to_scrape.append(state)
    
    if not states_to_scrape:
        print("All states already have county data. Skipping...")
        return
    
    print(f"Processing {len(states_to_scrape)} states that need county data...")
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        # Add progress bar for states
        for state in tqdm(states_to_scrape, desc="Scraping counties", unit="state"):
            state_name = state["state_name"]
            state_url = state["state_url"]
            
            # Extract state initials from URL (e.g., /ak.html -> ak)
            state_initials = state_url.rstrip('/').split('/')[-1].replace('.html', '')
              # Check if county file already exists
            county_file = f"Data/{state_initials}_counties.json"
            if os.path.exists(county_file):
                tqdm.write(f"[{state_initials.upper()}] Counties file already exists. Skipping...")
                continue
            
            tqdm.write(f"[{state_initials.upper()}] Scraping counties for {state_name}...")
            
            try:
                driver.get(state_url)
                
                # Wait for the page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "DirLinks"))
                )
                
                # Give it a moment to fully render
                time.sleep(1)
                
                # Find all links with the class "Link DirLinks"
                county_links = driver.find_elements(By.CSS_SELECTOR, "a.Link.DirLinks")
                  # Extract href and text from each link
                counties_data = []
                for link in county_links:
                    href = link.get_attribute("href")
                    text = link.text.strip()
                    if href:  # Only add if href exists
                        counties_data.append({
                            "county_name": text,
                            "county_url": href,
                            "stores": []  # Will be populated in Step 3
                        })
                
                tqdm.write(f"[{state_initials.upper()}] Found {len(counties_data)} counties")
                
                # Save to JSON file
                with open(county_file, "w", encoding="utf-8") as f:
                    json.dump(counties_data, f, indent=2, ensure_ascii=False)
                
                tqdm.write(f"[{state_initials.upper()}] Counties saved to {county_file}")
                
            except Exception as e:
                tqdm.write(f"[{state_initials.upper()}] Error scraping counties: {str(e)}")
                continue
        
        print("\nCounty scraping completed!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        driver.quit()
        print("Browser closed")

def scrape_stores():
    """
    Step 3 & 4: Scrape store information for each county
    """
    # Create Data folder if it doesn't exist
    os.makedirs("Data", exist_ok=True)
    
    # Get all county JSON files
    county_files = [f for f in os.listdir("Data") if f.endswith("_counties.json")]
    
    if not county_files:
        print("No county files found. Please run Step 2 first.")
        return
    
    # First pass: Count total counties that need processing
    print("Counting counties that need store data...")
    total_counties_to_process = 0
    counties_by_state = {}
    
    for county_file in county_files:
        state_initials = county_file.replace("_counties.json", "")
        county_path = f"Data/{county_file}"
        
        with open(county_path, "r", encoding="utf-8") as f:
            counties_data = json.load(f)
        
        counties_to_scrape = []
        for county in counties_data:
            if "stores" not in county or len(county["stores"]) == 0:
                counties_to_scrape.append(county)
        
        if counties_to_scrape:
            counties_by_state[state_initials] = {
                "file": county_path,
                "counties": counties_data,
                "to_scrape": counties_to_scrape
            }
            total_counties_to_process += len(counties_to_scrape)
    
    if total_counties_to_process == 0:
        print("All counties already have store data. Nothing to scrape!")
        return
    
    print(f"Found {total_counties_to_process} counties across {len(counties_by_state)} states that need store data.")
    
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:        # Single progress bar for all counties
        with tqdm(total=total_counties_to_process, desc="Scraping stores", unit="county") as pbar:
            for state_initials, state_data in counties_by_state.items():
                county_path = state_data["file"]
                counties_data = state_data["counties"]
                
                tqdm.write(f"\n[{state_initials.upper()}] Processing {len(state_data['to_scrape'])} counties...")
                
                for county in counties_data:
                    county_name = county["county_name"]
                    county_url = county["county_url"]
                    
                    # Skip if stores already exist
                    if "stores" in county and len(county["stores"]) > 0:
                        tqdm.write(f"  [{state_initials.upper()}] {county_name}: Already has store data. Skipping...")
                        continue
                    
                    tqdm.write(f"  [{state_initials.upper()}] Scraping stores for {county_name}...")
                    
                    try:
                        # Step 3: Go to county page and find "View Store Page" buttons
                        driver.get(county_url)
                        
                        # Wait for page to load
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "body"))
                        )
                        time.sleep(1)
                        
                        # Find all "View Store Page" links
                        store_page_links = []
                        try:
                            # Look for links/buttons that contain "View Store Page"
                            view_store_elements = driver.find_elements(By.XPATH, "//a[contains(text(), 'View Store Page')]")
                            store_page_links = [elem.get_attribute("href") for elem in view_store_elements if elem.get_attribute("href")]
                        except Exception as e:
                            tqdm.write(f"    Error finding store links: {str(e)}")                        
                        if not store_page_links:
                            tqdm.write(f"    No stores found for {county_name}")
                            county["stores"] = []
                            pbar.update(1)
                            continue
                        
                        tqdm.write(f"    Found {len(store_page_links)} stores")
                        
                        # Initialize stores array
                        county["stores"] = []
                        
                        # Step 4: Visit each store page and get details
                        for store_link in store_page_links:
                            try:
                                driver.get(store_link)
                                WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                                )
                                time.sleep(1)
                                
                                store_data = {
                                    "store_page_url": store_link,
                                    "store_number": None,
                                    "store_location": None
                                }
                                  # Get store number from "Start Your Order" button
                                try:
                                    start_order_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Start Your Order')]")
                                    start_order_href = start_order_button.get_attribute("href")
                                    if start_order_href and '=' in start_order_href:
                                        store_data["store_number"] = start_order_href.split('=')[-1]
                                except Exception as e:
                                    tqdm.write(f"      Could not find store number: {str(e)}")
                                
                                # Get store location from "Get Directions" button
                                try:
                                    get_directions_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Get Directions')]")
                                    store_data["store_location"] = get_directions_button.get_attribute("href")
                                except Exception as e:
                                    tqdm.write(f"      Could not find store location: {str(e)}")
                                
                                county["stores"].append(store_data)
                                
                            except Exception as e:
                                tqdm.write(f"      Error processing store {store_link}: {str(e)}")
                                continue
                        
                        tqdm.write(f"    Completed: {len(county['stores'])} stores processed")
                        
                    except Exception as e:
                        tqdm.write(f"    Error scraping stores for {county_name}: {str(e)}")
                        if "stores" not in county:
                            county["stores"] = []
                        continue
                    finally:
                        # Update progress bar after processing each county
                        pbar.update(1)
                
                # Save updated county data
                with open(county_path, "w", encoding="utf-8") as f:
                    json.dump(counties_data, f, indent=2, ensure_ascii=False)
                
                tqdm.write(f"[{state_initials.upper()}] Updated county file saved")
        
        print("\nStore scraping completed!")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    scrape_states()
    scrape_counties()
    scrape_stores()
 