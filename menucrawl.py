# Menu Crawler for Taco Bell
# 
# This script crawls the menu for each Taco Bell store and saves the data to JSON files
# organized by state and county.
#
# Usage:
#   python menucrawl.py                 - Process all stores (skip already done)
#   python menucrawl.py 5               - Process only 5 stores for testing  
#   python menucrawl.py 10 3 5          - Process 10 stores with 3 parallel browsers, 5 category workers each

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import os
import sys
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def setup_driver():
    """Set up and return a Chrome WebDriver instance"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def get_item_customizations(driver):
    """
    Extract customizations from the popup modal
    Returns a list of customization dictionaries
    """
    customizations = []
    
    try:
        # Wait briefly for popup content to load
        time.sleep(1)
        
        # Find all ingredient cards in the popup
        ingredient_cards = driver.find_elements(By.CSS_SELECTOR, ".styles_ingredient-card__IqQVq.styles_interactive-ingredient-card__md6_v")
        
        for card in ingredient_cards:
            try:
                customization = {
                    "name": None,
                    "price": None,
                    "calories": None
                }
                
                # Get the name of the customization (usually in a label or heading)
                try:
                    # Try to find the name - could be in various elements
                    name_element = card.find_element(By.CSS_SELECTOR, "label, h3, h4, span")
                    customization["name"] = name_element.text.strip()
                except:
                    pass
                
                # Get price and calories from styles_price-and-calories__hRaAE
                try:
                    price_calories_element = card.find_element(By.CSS_SELECTOR, ".styles_price-and-calories__hRaAE")
                    spans = price_calories_element.find_elements(By.TAG_NAME, "span")
                    
                    if len(spans) >= 2:
                        # First span is price, last span is calories
                        customization["price"] = spans[0].text.strip()
                        customization["calories"] = spans[-1].text.strip()
                    elif len(spans) == 1:
                        # Only one span, it's calories (no price)
                        customization["calories"] = spans[0].text.strip()
                        customization["price"] = "$0.00"
                        
                except:
                    # No price-and-calories element found
                    pass
                
                # Only add if we got at least a name
                if customization["name"]:
                    customizations.append(customization)
                    
            except Exception as e:
                continue
        
    except Exception as e:
        pass
    
    return customizations

def get_menu_categories(driver, store_number):
    """
    Get all menu category buttons from the menu grid
    Returns a list of dictionaries with category name and URL
    """
    try:
        # Navigate to the store menu page
        menu_url = f"https://www.tacobell.com/food?store={store_number}"
        driver.get(menu_url)
        
        # Wait for the menu grid to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".styles_menu-grid__3jFvm"))
        )
        
        # Give it extra time to fully render
        time.sleep(2)
        
        # Find all article elements (category cards) within the menu grid
        category_articles = driver.find_elements(By.CSS_SELECTOR, ".styles_menu-grid__3jFvm article")
        
        categories = []
        for article in category_articles:
            try:
                # Find the link within the article
                link = article.find_element(By.TAG_NAME, "a")
                category_url = link.get_attribute("href")
                category_label = link.get_attribute("aria-label")
                
                if category_url and category_label:
                    # Extract clean category name from aria-label
                    # e.g., "Navigate to Breakfast category" -> "Breakfast"
                    category_name = category_label.replace("Navigate to ", "").replace(" category", "").strip()
                    
                    categories.append({
                        "name": category_name,
                        "url": category_url
                    })
            except Exception as e:
                continue
        
        return categories
        
    except Exception as e:
        print(f"      Error getting menu categories: {str(e)}")
        return []

def get_menu_items(driver, category_url, store_number):
    """
    Get all menu items from a category page
    Returns a list of dictionaries with item details
    """
    try:
        # Navigate to the category page with store parameter
        if "store=" not in category_url:
            if "?" in category_url:
                category_url += f"&store={store_number}"
            else:
                category_url += f"?store={store_number}"
        
        driver.get(category_url)
        
        # Wait for the products grid to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".styles_products__hhyHx"))
        )
        
        # Give it time to fully render
        time.sleep(2)
          # Find all product cards using the correct class combination
        product_cards = driver.find_elements(By.CSS_SELECTOR, ".styles_card__3a_SE.styles_product-card__ogDyA")
        
        items = []
        for card in product_cards:
            try:
                item_data = {
                    "name": None,
                    "price": None,
                    "calories": None,
                    "url": None,
                    "customizations": []
                }
                
                # Get the product link (the entire card is usually wrapped in an <a> tag)
                try:
                    link = card.find_element(By.TAG_NAME, "a")
                    item_data["url"] = link.get_attribute("href")
                except:
                    pass
                
                # Get item name from the styles_product-title__NOX3k class
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, ".styles_product-title__NOX3k")
                    name_h4 = title_element.find_element(By.TAG_NAME, "h4")
                    item_data["name"] = name_h4.text.strip()
                except Exception as e:
                    # Fallback: try to find h4 directly
                    try:
                        name_h4 = card.find_element(By.TAG_NAME, "h4")
                        item_data["name"] = name_h4.text.strip()
                    except:
                        pass
                
                # Get price and calories from styles_product-details__r3wqo
                try:
                    details_element = card.find_element(By.CSS_SELECTOR, ".styles_product-details__r3wqo")
                    spans = details_element.find_elements(By.TAG_NAME, "span")
                    
                    # First span is price, second span is calories
                    if len(spans) >= 1:
                        item_data["price"] = spans[0].text.strip()
                    
                    if len(spans) >= 2:
                        item_data["calories"] = spans[1].text.strip()
                        
                except Exception as e:
                    pass
                  # Check for customize button and get customizations
                try:
                    customize_button = card.find_element(By.CSS_SELECTOR, ".styles_button__EjlEU.styles_button__MrNUN.styles_inverse__OXgLI.styles_brand__rBdC0.styles_customize-button__3sTRk")
                    
                    # Click the customize button to open the popup
                    driver.execute_script("arguments[0].scrollIntoView(true);", customize_button)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", customize_button)
                    
                    # Wait for the popup to appear (shorter timeout)
                    time.sleep(1.5)
                    
                    # Get customizations from the popup
                    item_data["customizations"] = get_item_customizations(driver)
                    
                    # Close the popup (try multiple methods)
                    try:
                        # Try ESC key first (fastest)
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        time.sleep(0.3)
                    except:
                        try:
                            # Try to find and click close button
                            close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
                            close_button.click()
                            time.sleep(0.3)
                        except:
                            pass
                        
                except:
                    # No customize button or error clicking it
                    item_data["customizations"] = []
                
                # Only add item if we at least got a name
                if item_data["name"]:
                    items.append(item_data)
                    
            except Exception as e:
                continue
        
        return items
        
    except Exception as e:
        print(f"      Error getting menu items: {str(e)}")
        return []

def scrape_single_category(category, store_number):
    """
    Scrape a single category (designed to be run in parallel)
    Returns (category_name, items)
    """
    # Create a new driver for this thread
    driver = setup_driver()
    
    try:
        category_name = category["name"]
        category_url = category["url"]
        
        # Get all items in this category (includes customizations)
        items = get_menu_items(driver, category_url, store_number)
        
        return (category_name, items)
        
    except Exception as e:
        return (category.get("name", "Unknown"), [])
        
    finally:
        driver.quit()

def scrape_store_menu(store_number, category_workers=5):
    """
    Scrape the full menu for a specific store with parallel category processing
    
    Args:
        store_number: The store number to scrape
        category_workers: Number of parallel workers for categories (default: 5)
    
    Returns a dictionary with all categories and their items
    """
    # Create a driver just to get the categories list
    driver = setup_driver()
    
    try:
        # Get all menu categories
        categories = get_menu_categories(driver, store_number)
        
        if not categories:
            return None
        
        menu_data = {
            "store_number": store_number,
            "categories": {}
        }
        
        # Process categories in parallel
        with ThreadPoolExecutor(max_workers=category_workers) as executor:
            futures = [executor.submit(scrape_single_category, category, store_number) for category in categories]
            
            for future in as_completed(futures):
                category_name, items = future.result()
                menu_data["categories"][category_name] = items
        
        return menu_data
        
    except Exception as e:
        print(f"      Error scraping store menu: {str(e)}")
        return None
        
    finally:
        driver.quit()

# Thread-safe lock for progress bar updates
progress_lock = threading.Lock()

def process_single_store(store_info, pbar=None, category_workers=5):
    """
    Process a single store (designed to be run in parallel)
    
    Args:
        store_info: Dictionary with store information
        pbar: Progress bar instance for updates
        category_workers: Number of parallel workers for categories within this store (default: 5)
    
    Returns (success, store_info, error_message)
    """
    state = store_info["state"].upper()
    county = store_info["county"]
    store_number = store_info["store_number"]
    menu_file = store_info["menu_file"]
    
    try:
        # Log start
        with progress_lock:
            if pbar:
                tqdm.write(f"[{state}] Store #{store_number} - Starting with {category_workers} category workers...")
        
        # Scrape the menu for this store (with parallel category processing)
        menu_data = scrape_store_menu(store_number, category_workers)
        
        if menu_data:
            # Add metadata
            menu_data["state"] = state
            menu_data["county"] = county
              # Save to JSON file
            with open(menu_file, "w", encoding="utf-8") as f:
                json.dump(menu_data, f, indent=2, ensure_ascii=False)
            
            category_count = len(menu_data.get("categories", {}))
            total_items = sum(len(items) for items in menu_data.get("categories", {}).values())
            
            # Log success
            with progress_lock:
                if pbar:
                    tqdm.write(f"[{state}] Store #{store_number} - ✓ Saved: {category_count} categories, {total_items} items")
            
            return (True, store_info, None)
        else:
            with progress_lock:
                if pbar:
                    tqdm.write(f"[{state}] Store #{store_number} - ✗ Failed to scrape menu")
            return (False, store_info, "Failed to scrape menu")
        
    except Exception as e:
        error_msg = str(e)
        with progress_lock:
            if pbar:
                tqdm.write(f"[{state}] Store #{store_number} - ✗ Error: {error_msg}")
        return (False, store_info, error_msg)
        
    finally:
        if pbar:
            with progress_lock:
                pbar.update(1)

def process_all_stores(max_stores=None, num_workers=3, category_workers=5):
    """
    Process all stores from county JSON files
    
    Args:
        max_stores: Maximum number of stores to process (None = all stores)
        num_workers: Number of parallel workers (default: 3)
    """
    # Create Menu folder if it doesn't exist
    os.makedirs("Menu", exist_ok=True)
    
    # Get all county JSON files from Data folder
    data_folder = "Data"
    county_files = [f for f in os.listdir(data_folder) if f.endswith("_counties.json")]
    
    if not county_files:
        print("No county files found in Data folder. Please run tacobellcrawl.py first.")
        return
    
    print(f"Found {len(county_files)} county files to process...")
    
    # Count total stores and identify which need processing
    print("Scanning for stores to process...")
    stores_to_process = []
    
    for county_file in county_files:
        state_initials = county_file.replace("_counties.json", "")
        county_path = os.path.join(data_folder, county_file)
        
        with open(county_path, "r", encoding="utf-8") as f:
            counties_data = json.load(f)
        
        for county in counties_data:
            county_name = county.get("county_name", "Unknown")
            stores = county.get("stores", [])
            
            for store in stores:
                store_number = store.get("store_number")
                if not store_number:
                    continue
                
                # Check if menu file already exists
                menu_file = os.path.join("Menu", f"{state_initials}_{store_number}_menu.json")
                
                if not os.path.exists(menu_file):
                    stores_to_process.append({
                        "state": state_initials,
                        "county": county_name,
                        "store_number": store_number,
                        "menu_file": menu_file
                    })
    
    if not stores_to_process:
        print("All stores already have menu data. Nothing to process!")
        return
    
    total_stores = len(stores_to_process)
    print(f"Found {total_stores} stores that need menu data")
    
    # Limit to max_stores if specified
    if max_stores is not None:
        stores_to_process = stores_to_process[:max_stores]
        print(f"Limiting to {max_stores} stores for this run")
      # Process stores in parallel with progress bar
    with tqdm(total=len(stores_to_process), desc="Scraping menus", unit="store") as pbar:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(process_single_store, store_info, pbar, category_workers) for store_info in stores_to_process]
            
            for future in as_completed(futures):
                success, store_info, error_message = future.result()
                if not success:
                    tqdm.write(f"Error processing store {store_info['store_number']}: {error_message}")
    
    print(f"\n✓ Menu scraping completed! Processed {len(stores_to_process)} stores")
    print(f"Menu files saved to: Menu/")

if __name__ == "__main__":
    # Check for command line arguments
    max_stores = None
    num_workers = 3
    category_workers = 5
    
    if len(sys.argv) > 1:
        try:
            max_stores = int(sys.argv[1])
            print(f"Processing {max_stores} stores (test mode)")
        except ValueError:
            print("Invalid argument. Usage: python menucrawl.py [number_of_stores] [num_workers] [category_workers]")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            num_workers = int(sys.argv[2])
            print(f"Using {num_workers} parallel store workers")
        except ValueError:
            print("Invalid argument. Usage: python menucrawl.py [number_of_stores] [num_workers] [category_workers]")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        try:
            category_workers = int(sys.argv[3])
            print(f"Using {category_workers} parallel category workers per store")
        except ValueError:
            print("Invalid argument. Usage: python menucrawl.py [number_of_stores] [num_workers] [category_workers]")
            sys.exit(1)
    
    if max_stores is None:
        print("Processing all stores (full mode)")
    
    process_all_stores(max_stores, num_workers, category_workers)