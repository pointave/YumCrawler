import json
import requests

# Census API - American Community Survey 5-Year Data (2022)
# You can get a free API key at: https://api.census.gov/data/key_signup.html
# For now, we'll use the public access (limited)

# Florida FIPS code is 12
FLORIDA_FIPS = "12"

def fetch_florida_poverty_data():
    """
    Fetch poverty data for Florida counties from Census API
    S1701_C03_001E: Percent below poverty level; Estimate; Total
    """
    
    # Census API endpoint for ACS 5-Year Subject Tables
    url = "https://api.census.gov/data/2022/acs/acs5/subject"
    
    params = {
        "get": "NAME,S1701_C03_001E",  # County name and poverty percentage
        "for": "county:*",
        "in": f"state:{FLORIDA_FIPS}"
    }
    
    try:
        print("Fetching poverty data from Census API...")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # First row is headers
        headers = data[0]
        rows = data[1:]
        
        poverty_data = []
        
        for row in rows:
            county_name = row[0].replace(" County, Florida", "")
            poverty_rate = float(row[1]) if row[1] not in [None, "null", ""] else None
            county_fips = row[2]
            
            if poverty_rate is not None:
                poverty_data.append({
                    "county": county_name,
                    "fips": f"{FLORIDA_FIPS}{county_fips}",
                    "poverty_rate": poverty_rate
                })
                print(f"{county_name}: {poverty_rate}%")
        
        return poverty_data
        
    except Exception as e:
        print(f"Error fetching Census data: {e}")
        print("\nNote: Census API may require an API key for full access.")
        print("Get one at: https://api.census.gov/data/key_signup.html")
        return None

def fetch_florida_county_geojson():
    """
    Fetch Florida county boundaries GeoJSON
    """
    print("\nFetching Florida county boundaries...")
    
    # Use Census Cartographic Boundary Files
    url = f"https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        all_counties = response.json()
        
        # Filter for Florida counties only (FIPS codes starting with 12)
        florida_features = [
            feature for feature in all_counties['features']
            if feature['id'].startswith('12')
        ]
        
        florida_geojson = {
            "type": "FeatureCollection",
            "features": florida_features
        }
        
        print(f"Found {len(florida_features)} Florida counties")
        return florida_geojson
        
    except Exception as e:
        print(f"Error fetching GeoJSON: {e}")
        return None

def main():
    # Fetch poverty data
    poverty_data = fetch_florida_poverty_data()
    
    if poverty_data:
        # Save poverty data
        with open('Data/florida_poverty.json', 'w', encoding='utf-8') as f:
            json.dump(poverty_data, f, indent=2)
        print(f"\nSaved poverty data to Data/florida_poverty.json")
        print(f"Total counties: {len(poverty_data)}")
        
        # Calculate statistics
        rates = [d['poverty_rate'] for d in poverty_data]
        print(f"Poverty rate range: {min(rates):.1f}% - {max(rates):.1f}%")
    
    # Fetch county boundaries
    geojson = fetch_florida_county_geojson()
    
    if geojson:
        # Save GeoJSON
        with open('Data/florida_counties.geojson', 'w', encoding='utf-8') as f:
            json.dump(geojson, f, indent=2)
        print(f"\nSaved county boundaries to Data/florida_counties.geojson")

if __name__ == "__main__":
    main()
