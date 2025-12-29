import requests
import csv
import os
import json
import re
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_first_location():
    """Load the first store from locations.csv"""
    if not os.path.exists('data/locations.csv'):
        print("Error: data/locations.csv not found!")
        return None
    
    with open('data/locations.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Get the first row
        for row in reader:
            return row
    
    return None

def load_all_locations():
    """Load all stores from locations.csv"""
    if not os.path.exists('data/locations.csv'):
        print("Error: data/locations.csv not found!")
        return []
    
    locations = []
    with open('data/locations.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            locations.append(row)
    
    return locations

def load_processed_store_ids():
    """Load the list of store IDs that have already been processed"""
    csv_path = 'data/menu.csv'
    
    if not os.path.exists(csv_path):
        return set()
    
    processed_ids = set()
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'store_id' in row:
                    processed_ids.add(row['store_id'])
        
        return processed_ids
    except Exception as e:
        print(f"Warning: Could not read existing CSV: {e}")
        return set()

def load_existing_menu_data():
    """Load existing menu data from CSV if it exists"""
    csv_path = 'data/menu.csv'
    
    if not os.path.exists(csv_path):
        return [], set()
    
    try:
        existing_rows = []
        all_menu_items = set()
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            if fieldnames and len(fieldnames) > 1:
                # All columns except store_id are menu items
                all_menu_items = set(fieldnames[1:])
            
            for row in reader:
                existing_rows.append(row)
        
        return existing_rows, all_menu_items
    except Exception as e:
        print(f"Warning: Could not read existing CSV: {e}")
        return [], set()

def fetch_menu_page(store_id):
    """Fetch the menu page for a given store ID"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    url = f"https://www.tacobell.com/food?store={store_id}"
    print(f"Fetching menu from: {url}")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page: {e}")
        return None

def parse_categories(html_content, store_id):
    """Parse the category data from the HTML content"""
    try:
        # Find the __NEXT_DATA__ script tag which contains all the menu data
        soup = BeautifulSoup(html_content, 'html.parser')
        next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
        
        if not next_data_script:
            print("Error: Could not find __NEXT_DATA__ script tag")
            return None
        
        # Parse the JSON data
        data = json.loads(next_data_script.string)
        
        # Navigate to the product categories
        product_categories = data.get('props', {}).get('pageProps', {}).get('productCategories', [])
        
        categories = []
        for category in product_categories:
            label = category.get('label', 'Unknown')
            slug = category.get('slug', '')
            subtitle = category.get('subtitle', '')
            
            # Build the full URL with store parameter
            if slug:
                url = f"https://www.tacobell.com{slug}?store={store_id}"
            else:
                url = ''
            
            categories.append({
                'name': label,
                'url': url,
                'description': subtitle
            })
        
        return categories
        
    except Exception as e:
        print(f"Error parsing category data: {e}")
        return None

def display_categories(categories):
    """Display all categories with their links"""
    if not categories:
        print("No categories found")
        return
    
    print("\n" + "="*80)
    print("TACO BELL MENU CATEGORIES")
    print("="*80 + "\n")
    
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category['name']}")
        print(f"   Description: {category['description']}")
        print(f"   URL: {category['url']}")
        print()
    
    print("="*80)
    print(f"Total categories: {len(categories)}")
    print("="*80 + "\n")

def fetch_category_page(category):
    """Fetch the HTML content for a single category page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    category_name = category['name']
    category_url = category['url']
    
    try:
        response = requests.get(category_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return {
            'category': category,
            'html': response.text,
            'success': True,
            'error': None
        }
        
    except requests.exceptions.HTTPError as e:
        return {
            'category': category,
            'html': None,
            'success': False,
            'error': str(e)
        }
    except requests.exceptions.Timeout:
        return {
            'category': category,
            'html': None,
            'success': False,
            'error': 'Timeout'
        }
    except Exception as e:
        return {
            'category': category,
            'html': None,
            'success': False,
            'error': str(e)
        }

def fetch_all_categories_parallel(categories, max_workers=5):
    """Fetch all category pages in parallel"""
    results = []
    
    # Use ThreadPoolExecutor to fetch pages in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all fetch tasks
        future_to_category = {
            executor.submit(fetch_category_page, category): category 
            for category in categories
        }
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_category):
            result = future.result()
            results.append(result)
    
    # Count successes and failures
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    print(f"  Fetched {successful}/{len(results)} categories")
    
    return results

def parse_menu_items(html_content):
    """Parse menu items and prices from HTML content"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
        
        if not next_data_script:
            return []
        
        data = json.loads(next_data_script.string)
        
        # Navigate to products in the page data
        products = data.get('props', {}).get('pageProps', {}).get('products', [])
        
        menu_items = []
        for product in products:
            name = product.get('name', '')
            # Price is in the price object
            price_obj = product.get('price', {})
            
            if name and price_obj and isinstance(price_obj, dict):
                price = price_obj.get('value')
                if price is not None:
                    menu_items.append({
                        'name': name,
                        'price': float(price)
                    })
        
        return menu_items
        
    except Exception as e:
        print(f"Error parsing menu items: {e}")
        return []

def parse_all_menu_items_parallel(category_results):
    """Parse menu items from all category results in parallel"""
    all_items = {}
    
    def parse_result(result):
        if not result['success'] or not result['html']:
            return []
        
        items = parse_menu_items(result['html'])
        return items
    
    # Parse all results in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(parse_result, result) for result in category_results]
        
        for future in as_completed(futures):
            items = future.result()
            # Add items to dictionary (item name -> price)
            for item in items:
                # If item already exists, keep the first price we found
                if item['name'] not in all_items:
                    all_items[item['name']] = item['price']
    
    print(f"  Parsed {len(all_items)} unique menu items")
    
    return all_items

def write_menu_csv(store_id, menu_items):
    """Write menu items to CSV file"""
    if not menu_items:
        print("No menu items to write")
        return
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    csv_path = 'data/menu.csv'
    
    # Sort items by name for consistent ordering
    sorted_items = sorted(menu_items.items())
    
    # Prepare headers and data row
    headers = ['store_id'] + [item_name for item_name, _ in sorted_items]
    data_row = [store_id] + [price for _, price in sorted_items]
    
    print("\n" + "="*80)
    print("WRITING MENU CSV")
    print("="*80)
    print(f"Output file: {csv_path}")
    print(f"Total columns: {len(headers)}")
    print(f"Store ID: {store_id}")
    print(f"Menu items: {len(menu_items)}")
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(data_row)
        
        print(f"✓ Successfully wrote menu data to {csv_path}")
        print("="*80 + "\n")
        
        # Display sample of items
        print("Sample menu items (first 10):")
        for i, (item_name, price) in enumerate(sorted_items[:10], 1):
            print(f"  {i}. {item_name}: ${price:.2f}")
        
        if len(sorted_items) > 10:
            print(f"  ... and {len(sorted_items) - 10} more items")
        print()
        
    except Exception as e:
        print(f"✗ Error writing CSV: {e}")
        print("="*80 + "\n")

def fetch_and_parse_store(location):
    """Fetch and parse the main menu page for a store"""
    store_id = location['store_id']
    location_name = location['location']
    
    try:
        html_content = fetch_menu_page(store_id)
        if not html_content:
            return {
                'store_id': store_id,
                'location': location_name,
                'success': False
            }
        
        categories = parse_categories(html_content, store_id)
        if not categories:
            return {
                'store_id': store_id,
                'location': location_name,
                'success': False
            }
        
        return {
            'store_id': store_id,
            'location': location_name,
            'categories': categories,
            'success': True
        }
        
    except Exception as e:
        print(f"✗ Error fetching store {store_id}: {e}")
        return {
            'store_id': store_id,
            'location': location_name,
            'success': False
        }

def process_batch_fully_parallel(batch):
    """Process a batch of stores with fully parallel category fetching"""
    all_store_categories = {}
    
    # Step 1: Fetch main menu pages for all stores in parallel
    print("  Fetching main menu pages...")
    with ThreadPoolExecutor(max_workers=len(batch)) as executor:
        future_to_store = {
            executor.submit(fetch_and_parse_store, location): location
            for location in batch
        }
        
        for future in as_completed(future_to_store):
            location = future_to_store[future]
            result = future.result()
            if result['success']:
                all_store_categories[result['store_id']] = result
    
    # Step 2: Collect all category URLs from all stores
    all_category_tasks = []
    for store_id, store_data in all_store_categories.items():
        for category in store_data['categories']:
            all_category_tasks.append({
                'store_id': store_id,
                'category': category
            })
    
    print(f"  Fetching {len(all_category_tasks)} category pages across {len(batch)} stores in parallel...")
    
    # Step 3: Fetch ALL category pages in parallel (across all stores)
    category_results = {}
    with ThreadPoolExecutor(max_workers=20) as executor:  # Increased workers for all categories
        future_to_task = {
            executor.submit(fetch_category_page, task['category']): task
            for task in all_category_tasks
        }
        
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            result = future.result()
            store_id = task['store_id']
            
            if store_id not in category_results:
                category_results[store_id] = []
            category_results[store_id].append(result)
    
    # Step 4: Parse menu items for each store
    print(f"  Parsing menu items...")
    batch_results = []
    for store_id, store_data in all_store_categories.items():
        store_category_results = category_results.get(store_id, [])
        menu_items = parse_all_menu_items_parallel(store_category_results)
        
        batch_results.append({
            'store_id': store_id,
            'location': store_data['location'],
            'menu_items': menu_items,
            'success': True
        })
        
        print(f"    ✓ {store_id}: {len(menu_items)} unique items")
    
    return batch_results

def process_single_store(location):
    """Process a single store and return its menu items"""
    store_id = location['store_id']
    location_name = location['location']
    
    print(f"\n{'='*80}")
    print(f"Processing: {location_name} (Store ID: {store_id})")
    print(f"{'='*80}")
    
    try:
        # Fetch the menu page
        html_content = fetch_menu_page(store_id)
        if not html_content:
            print(f"✗ Failed to fetch menu page for {store_id}")
            return {
                'store_id': store_id,
                'location': location_name,
                'menu_items': {},
                'success': False
            }
        
        # Parse the categories
        categories = parse_categories(html_content, store_id)
        if not categories:
            print(f"✗ Failed to parse categories for {store_id}")
            return {
                'store_id': store_id,
                'location': location_name,
                'menu_items': {},
                'success': False
            }
        
        print(f"Found {len(categories)} categories")
        
        # Fetch all category pages in parallel
        category_results = fetch_all_categories_parallel(categories, max_workers=5)
        
        # Parse all menu items in parallel
        menu_items = parse_all_menu_items_parallel(category_results)
        
        print(f"✓ Successfully processed {store_id}: {len(menu_items)} unique items")
        
        return {
            'store_id': store_id,
            'location': location_name,
            'menu_items': menu_items,
            'success': True
        }
        
    except Exception as e:
        print(f"✗ Error processing store {store_id}: {e}")
        return {
            'store_id': store_id,
            'location': location_name,
            'menu_items': {},
            'success': False
        }

def process_stores_in_batches(locations, batch_size=5):
    """Process all stores in batches, saving after each batch"""
    print("\n" + "="*80)
    print(f"PROCESSING {len(locations)} STORES IN BATCHES OF {batch_size}")
    print("="*80 + "\n")
    
    # Load existing data
    existing_rows, existing_items = load_existing_menu_data()
    current_menu_items = existing_items
    
    # Process stores in batches
    for i in range(0, len(locations), batch_size):
        batch = locations[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(locations) + batch_size - 1) // batch_size
        
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num}/{total_batches} - Processing {len(batch)} stores")
        print(f"{'='*80}")
        
        # Process batch with fully parallelized category fetching
        batch_results = process_batch_fully_parallel(batch)
        
        print(f"\n✓ Completed batch {batch_num}/{total_batches}")
        
        # Save CSV after each batch
        print(f"\n💾 Saving progress after batch {batch_num}...")
        current_menu_items = write_comprehensive_menu_csv(batch_results, existing_rows, current_menu_items)
        
        # Update existing_rows to include the batch we just processed
        if current_menu_items:
            # Reload the CSV to get updated existing_rows
            existing_rows, current_menu_items = load_existing_menu_data()

def write_comprehensive_menu_csv(store_results, existing_rows=None, existing_items=None):
    """Write comprehensive CSV with all stores and all menu items"""
    if not store_results and not existing_rows:
        print("No store results to write")
        return
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    csv_path = 'data/menu.csv'
    
    print("\n" + "="*80)
    print("UPDATING COMPREHENSIVE MENU CSV")
    print("="*80)
    
    # Start with existing menu items if any
    all_menu_items = set(existing_items) if existing_items else set()
    
    # Add new menu items from current batch
    for result in store_results:
        if result['success']:
            all_menu_items.update(result['menu_items'].keys())
    
    # Sort menu items alphabetically for consistent ordering
    sorted_menu_items = sorted(all_menu_items)
    
    print(f"Total unique menu items: {len(sorted_menu_items)}")
    print(f"New stores in this batch: {len(store_results)}")
    
    # Prepare headers
    headers = ['store_id'] + sorted_menu_items
    
    # Start with existing rows, updated with new columns if needed
    rows = []
    if existing_rows:
        for existing_row in existing_rows:
            row = [existing_row['store_id']]
            for item_name in sorted_menu_items:
                # Use existing value or empty string for new items
                price = existing_row.get(item_name, '')
                row.append(price)
            rows.append(row)
    
    # Add new rows from current batch
    successful_stores = 0
    failed_stores = 0
    
    for result in store_results:
        if result['success']:
            successful_stores += 1
            # Build row with prices or empty string for missing items
            row = [result['store_id']]
            for item_name in sorted_menu_items:
                price = result['menu_items'].get(item_name)
                row.append(price if price is not None else '')
            rows.append(row)
        else:
            failed_stores += 1
            print(f"  Skipping failed store: {result['store_id']}")
    
    print(f"Successfully processed stores in batch: {successful_stores}")
    print(f"Failed stores in batch: {failed_stores}")
    print(f"Total stores in CSV: {len(rows)}")
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        print(f"\n✓ Successfully wrote comprehensive menu data to {csv_path}")
        print(f"  - {len(rows)} store rows")
        print(f"  - {len(sorted_menu_items)} menu item columns")
        print(f"  - {len(headers)} total columns (including store_id)")
        print("="*80 + "\n")
        
        return sorted_menu_items
        
    except Exception as e:
        print(f"✗ Error writing CSV: {e}")
        print("="*80 + "\n")
        return None

def main():
    """Main function to fetch and display the menu categories"""
    # Load all locations
    all_locations = load_all_locations()
    
    if not all_locations:
        print("No locations found in data/locations.csv")
        return
    
    print(f"\nFound {len(all_locations)} total locations")
    
    # Check for already processed stores
    processed_store_ids = load_processed_store_ids()
    
    if processed_store_ids:
        print(f"Found {len(processed_store_ids)} already processed stores")
        print(f"Resuming from where we left off...\n")
        
        # Filter out already processed stores
        locations_to_process = [loc for loc in all_locations if loc['store_id'] not in processed_store_ids]
        
        print(f"Remaining stores to process: {len(locations_to_process)}")
        
        if not locations_to_process:
            print("\nAll stores have already been processed!")
            return
    else:
        print("Starting fresh - no existing data found\n")
        locations_to_process = all_locations
    
    # Process remaining stores in batches
    process_stores_in_batches(locations_to_process, batch_size=5)
    
    print("\n" + "="*80)
    print("PROCESSING COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()
