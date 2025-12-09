"""
Combine all Taco Bell store locations from state JSON files into a single locations.json file.
This improves map loading performance by reducing HTTP requests and file parsing.
"""

import json
import os
import re
from pathlib import Path

def extract_coordinates(url):
    """Extract latitude and longitude from Google Maps URL."""
    match = re.search(r'destination=([-\d.]+),([-\d.]+)', url)
    if match:
        return {
            'lat': float(match.group(1)),
            'lng': float(match.group(2))
        }
    return None

def combine_all_locations():
    """Read all state JSON files and combine into a single locations file."""
    data_dir = Path('Data')
    all_locations = []
    
    # Get all state county JSON files
    state_files = sorted(data_dir.glob('*_counties.json'))
    
    print(f"Found {len(state_files)} state files to process...")
    
    for state_file in state_files:
        state_abbr = state_file.stem.replace('_counties', '').upper()
        print(f"Processing {state_abbr}...")
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                counties = json.load(f)
            
            for county in counties:
                county_name = county.get('county_name', '')
                
                for store in county.get('stores', []):
                    coords = extract_coordinates(store.get('store_location', ''))
                    
                    if coords:
                        location = {
                            'store_number': store.get('store_number'),
                            'state': state_abbr,
                            'county': county_name,
                            'lat': coords['lat'],
                            'lng': coords['lng'],
                            'url': store.get('store_page_url', '')
                        }
                        all_locations.append(location)
        
        except Exception as e:
            print(f"Error processing {state_file}: {e}")
    
    # Write combined locations to file
    output_file = data_dir / 'locations.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_locations, f, indent=2)
    
    print(f"\n✓ Successfully combined {len(all_locations)} locations into {output_file}")
    print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
    
    # Print some statistics
    states_count = len(set(loc['state'] for loc in all_locations))
    print(f"\n Statistics:")
    print(f"  - Total stores: {len(all_locations)}")
    print(f"  - States/territories: {states_count}")
    print(f"  - Average stores per state: {len(all_locations) / states_count:.1f}")

if __name__ == '__main__':
    combine_all_locations()
