# YumCrawler - Multi-Restaurant Menu & Location Explorer

A web application that displays menu items and locations for KFC and Taco Bell restaurants across the United States. Features interactive mapping, menu browsing, and order calculation functionality. Will probably add Pizza Hut and Long John Silvers if site format is similar.


## Setup & Installation

### Prerequisites
- Python 3.x (for local development server)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Local Development

1. **Clone/Download the repository**
   ```bash
   git clone github.com/pointave/YumCrawler/
   cd YumCrawler
   ```

2. **Start local server**
   ```bash
   python -m http.server 8000
   ```

3. **Open in browser**
   ```
   http://localhost:8000
   ```

## File Structure

```
YumCrawler/
├── index.html              # Main application page
├── js/
│   ├── config.js           # Map configuration and settings
│   ├── csvParser.js        # CSV data parsing utilities
│   ├── menuManager.js      # Menu and order management
│   └── map.js            # Map functionality and markers
├── styles/
│   └── map.css           # Application styling
├── data/                 # Taco Bell data files
│   ├── menu.csv          # Taco Bell menu items and prices
│   └── locations.csv     # Taco Bell locations
├── KFC/                 # KFC data files
│   └── data/
│       ├── menu.csv      # KFC menu items and prices
│       └── locations.csv # KFC locations
└── images/               # Menu item images
    └── [category folders] # Organized by menu categories
```

## Technical Details

### Architecture
- **Modular Design**: Separate modules for map, menu, and data parsing
- **Event-Driven**: Reactive updates between components
- **Responsive Layout**: CSS Grid and Flexbox for adaptive design
- **Modern JavaScript**: ES6+ features with async/await

### Key Components

#### MenuManager
- Handles menu data loading and category management
- Manages order state and UI updates
- Implements restaurant switching logic
- Provides search and filtering capabilities

#### TacoBellMap
- Leaflet.js-based interactive mapping
- Dynamic marker creation and management
- Price-based visualization
- Popup content generation

#### CSVParser
- Handles both KFC and Taco Bell data formats
- Coordinate extraction from URLs (Taco Bell)
- Direct coordinate parsing (KFC)
- Error handling and data validation

## Data Source

- **Images**: High-quality product images from restaurant websites
- **Maps**: OpenStreetMap tiles via CartoDB

## Credits

- The creator of original project https://github.com/TheDevAtlas/Taco-Bell-Crawler


## License

This project is for educational and demonstration purposes. All restaurant data and images are property of their respective owners.


