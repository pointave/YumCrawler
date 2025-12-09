// Initialize the map focused on Mainland US
// Coordinates exclude Alaska and Hawaii to focus on continental US
const map = L.map('map', {
    zoomControl: false, // Remove zoom controls
    attributionControl: false, // Remove Leaflet attribution
    scrollWheelZoom: true, // Enable mouse wheel zoom
    dragging: true, // Enable mouse drag panning
    doubleClickZoom: true // Enable double-click zoom
}).setView([39.8283, -98.5795], 5);

// Add satellite imagery tile layer
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '', // Remove attribution text
    maxZoom: 18
}).addTo(map);

// Set bounds to focus on Mainland US (excluding Alaska and Hawaii)
const mainlandBounds = L.latLngBounds(
    [24.396308, -125.0], // Southwest corner
    [49.384358, -66.93457] // Northeast corner
);

// Fit the map to Mainland US bounds
map.fitBounds(mainlandBounds);

// Removed setMaxBounds to allow free panning worldwide

// Create a canvas renderer for better performance with many markers
const canvasRenderer = L.canvas({ padding: 0.5 });

// Custom circle marker style for Taco Bell locations
const markerStyle = {
    renderer: canvasRenderer,
    radius: 6,
    fillColor: '#7B3F94',
    color: '#FFFFFF',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.9
};

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
        console.error('Error loading locations:', error);
    }
}

// Start loading stores
loadAllStores();
