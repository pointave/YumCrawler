// Initialize the map focused on Mainland US
// Coordinates exclude Alaska and Hawaii to focus on continental US
const map = L.map('map', {
    zoomControl: false, // Remove zoom controls
    attributionControl: false, // Remove Leaflet attribution
    scrollWheelZoom: true, // Enable mouse wheel zoom
    dragging: true, // Enable mouse drag panning
    doubleClickZoom: true // Enable double-click zoom
}).setView([39.8283, -98.5795], 5);

// Add a blue tile layer (no satellite imagery)
L.tileLayer('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPj/HwADBwIAMCbHYQAAAABJRU5ErkJggg==', {
    attribution: '',
    maxZoom: 18
}).addTo(map);

// Set map background to blue
map.getContainer().style.background = '#4A90E2';

// Set bounds to focus on Mainland US (excluding Alaska and Hawaii)
const mainlandBounds = L.latLngBounds(
    [24.396308, -125.0], // Southwest corner
    [49.384358, -66.93457] // Northeast corner
);

// Fit the map to Mainland US bounds
map.fitBounds(mainlandBounds);

// Create custom panes for layer ordering
map.createPane('statesPane');
map.getPane('statesPane').style.zIndex = 400;

map.createPane('markersPane');
map.getPane('markersPane').style.zIndex = 450;

// Create a canvas renderer for better performance with many markers
const canvasRenderer = L.canvas({ padding: 0.5, pane: 'markersPane' });

// Custom circle marker style for Taco Bell locations
const markerStyle = {
    renderer: canvasRenderer,
    radius: 6,
    fillColor: '#7B3F94',
    color: '#FFFFFF',
    weight: 2,
    opacity: 1,    fillOpacity: 0.9
};

// Load US states boundaries
async function loadUSBoundaries() {
    try {
        // Using publicly available GeoJSON for US states
        const response = await fetch('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json');
        const statesData = await response.json();
          // Style for US states - green fill with black outline
        const stateStyle = {
            fillColor: '#90EE90', // Light green
            weight: 2, // Thinner outline for states
            opacity: 1,
            color: 'black',
            fillOpacity: 1,
            pane: 'statesPane' // Ensure states are on the correct pane
        };
        
        // Add states layer
        L.geoJSON(statesData, {
            style: stateStyle,
            pane: 'statesPane'
        }).addTo(map);
        
        // Add thick US boundary outline on top
        const usOutlineStyle = {
            fillColor: 'transparent',
            weight: 4, // Thick outline for US border
            opacity: 1,
            color: 'black',
            fillOpacity: 0,
            pane: 'statesPane' // Keep outline with states
        };
        
        L.geoJSON(statesData, {
            style: usOutlineStyle,
            pane: 'statesPane'
        }).addTo(map);
        
    } catch (error) {
        console.error('Error loading US boundaries:', error);
    }
}

// Load and plot all stores from the combined locations file
async function loadAllStores() {
    console.time('Loading locations');
    console.log('Loading Taco Bell locations...');
    
    try {
        const response = await fetch('Data/locations.json');
        const locations = await response.json();
        
        console.log(`Found ${locations.length} locations. Creating markers...`);
        
        // Create circle markers for each location (much faster than custom icons)
        locations.forEach(location => {
            L.circleMarker([location.lat, location.lng], markerStyle)
                .bindPopup(`
                    <strong>Store #${location.store_number}</strong><br>
                    ${location.county}<br>
                    ${location.state}<br>
                    <a href="${location.url}" target="_blank">View Details</a>
                `)
                .addTo(map);
        });
        
        console.log('All locations loaded!');
        console.timeEnd('Loading locations');
    } catch (error) {
        console.error('Error loading locations:', error);    }
}

// Load boundaries first, then stores
loadUSBoundaries().then(() => loadAllStores());
