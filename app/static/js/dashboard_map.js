document.addEventListener('DOMContentLoaded', function () {
    const mapElement = document.getElementById('global-risk-map');
    if (!mapElement) {
        console.error('Map container element #global-risk-map not found.');
        return;
    }

    // --- Configuration ---
    const mapCenter = [20, 0]; // Initial map center latitude/longitude
    const initialZoom = 2;
    const geoJsonUrl = '/static/data/world-countries.geojson'; // Path to your GeoJSON file
    const apiUrl = '/dashboard/api/global-risk-heatmap'; // Corrected API URL with blueprint prefix
    const noDataColor = '#CCCCCC'; // Grey for countries with no data
    const colorScale = [ // Example: Yellow to Red color scale
        { value: 0, color: '#FFFFE0' },   // Light Yellow for 0 events (or use noDataColor)
        { value: 1, color: '#FFFACD' },   // Lemon Chiffon
        { value: 10, color: '#FFD700' },  // Gold
        { value: 50, color: '#FFA500' },  // Orange
        { value: 100, color: '#FF4500' }, // OrangeRed
        { value: 500, color: '#FF0000' }, // Red
        { value: 1000, color: '#B22222'}  // Firebrick (for very high counts)
    ];

    // --- Map Initialization ---
    // Check if map is already initialized on this element
    if (mapElement._leaflet_id) {
        console.warn("Map container #global-risk-map already initialized. Skipping re-initialization.");
        return;
    }
    mapElement.innerHTML = ''; // Clear the loading text *before* initializing map
    const map = L.map(mapElement).setView(mapCenter, initialZoom);

    // Add a base tile layer (e.g., OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let geoJsonLayer;
    let legend;

    // --- Helper Functions ---
    function getColor(eventCount) {
        if (eventCount === null || eventCount === undefined) {
            return noDataColor;
        }
        // Find the appropriate color from the scale
        let color = colorScale[0].color; // Default to the lowest color
        for (let i = colorScale.length - 1; i >= 0; i--) {
            if (eventCount >= colorScale[i].value) {
                color = colorScale[i].color;
                break;
            }
        }
        return color;
    }

    function styleFeature(feature, eventData) {
        // --- IMPORTANT: Adjust property name based on your GeoJSON ---
        const countryName = feature.properties.name || feature.properties.ADMIN || feature.properties. sovereignt; // Common property names for country name
        const countryCode = feature.properties.iso_a3 || feature.properties.ISO_A3; // Common property names for ISO A3 code

        // Try matching by name first, then potentially by code if needed and API provides it
        const count = eventData[countryName] !== undefined ? eventData[countryName] : null;

        return {
            fillColor: getColor(count),
            weight: 1,
            opacity: 1,
            color: 'white', // Border color
            dashArray: '3',
            fillOpacity: 0.7
        };
    }

    function onEachFeature(feature, layer, eventData) {
        // --- IMPORTANT: Adjust property name based on your GeoJSON ---
        const countryName = feature.properties.name || feature.properties.ADMIN || feature.properties.sovereignt;
        const count = eventData[countryName] !== undefined ? eventData[countryName] : null;

        let tooltipContent = `${countryName}<br/>Events (90 days): ${count !== null ? count : 'No data'}`;
        layer.bindTooltip(tooltipContent);

        // Optional: Highlight feature on hover
        layer.on({
            mouseover: function (e) {
                const layer = e.target;
                layer.setStyle({
                    weight: 2,
                    color: '#666',
                    dashArray: '',
                    fillOpacity: 0.9
                });
                if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                    layer.bringToFront();
                }
            },
            mouseout: function (e) {
                if (geoJsonLayer) {
                    geoJsonLayer.resetStyle(e.target);
                }
            },
            // click: function (e) {
            //     map.fitBounds(e.target.getBounds()); // Example: Zoom to country on click
            // }
        });
    }

    function addLegend() {
        legend = L.control({ position: 'bottomright' });

        legend.onAdd = function (map) {
            const div = L.DomUtil.create('div', 'info legend');
            div.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
            div.style.padding = '10px';
            div.style.borderRadius = '5px';
            div.style.boxShadow = '0 0 15px rgba(0,0,0,0.2)';

            const grades = colorScale.map(item => item.value);
            const labels = [];
            let from, to;

            labels.push('<h4 style="margin-top:0; margin-bottom: 5px; text-align: center;">Events (90 days)</h4>');

            // Loop through intervals and generate labels with colored squares
            for (let i = 0; i < grades.length; i++) {
                from = grades[i];
                to = grades[i + 1];

                labels.push(
                    '<i style="background:' + getColor(from) + '; width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7;"></i> ' +
                    from + (to ? '&ndash;' + (to - 1) : '+'));
            }
             labels.push('<br/><i style="background:' + noDataColor + '; width: 18px; height: 18px; float: left; margin-right: 8px; opacity: 0.7;"></i> No Data');


            div.innerHTML = labels.join('<br>');
            return div;
        };

        legend.addTo(map);
    }


    // --- Data Fetching and Map Population ---
    Promise.all([
        fetch(apiUrl).then(response => {
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        }),
        fetch(geoJsonUrl).then(response => {
            if (!response.ok) {
                throw new Error(`GeoJSON Error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
    ])
    .then(([eventData, geoJsonData]) => {
        console.log("Event Data:", eventData);
        console.log("GeoJSON Data:", geoJsonData);

        geoJsonLayer = L.geoJSON(geoJsonData, {
            style: feature => styleFeature(feature, eventData),
            onEachFeature: (feature, layer) => onEachFeature(feature, layer, eventData)
        }).addTo(map);

        addLegend();

    })
    .catch(error => {
        console.error('Failed to load map data:', error);
        mapElement.innerHTML = `<p class="text-red-500">Error loading map data: ${error.message}. Please check console.</p>`;
        // Display error message on the map container
        const errorDiv = document.createElement('div');
        errorDiv.className = 'p-4 text-red-600 bg-red-100 border border-red-400 rounded';
        errorDiv.textContent = `Failed to load map data: ${error.message}. Please ensure the API is running and the GeoJSON file exists at ${geoJsonUrl}.`;
        mapElement.appendChild(errorDiv);
    });

});