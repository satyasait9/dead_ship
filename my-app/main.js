
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import {
    DragAndDrop,
    defaults as defaultInteractions,
} from 'ol/interaction.js';
import ImageLayer from 'ol/layer/Image';
import { GPX, GeoJSON, IGC, KML, TopoJSON } from 'ol/format.js';
import { ImageStatic, OSM, Vector as VectorSource } from 'ol/source.js';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer.js';
import Static from 'ol/source/ImageStatic.js';
import JSZip from 'jszip';
// import JSZip from 'jszip';
const zip = new JSZip();

let main_kml=undefined
let main_csv=undefined

function getKMLData(buffer) {
    let kmlData;
    zip.load(buffer);
    const kmlFile = zip.file(/\.kml$/i)[0];
    if (kmlFile) {
        kmlData = kmlFile.asText();
        // console.log(kmlData);
    }
    return kmlData;
}

function getKMLImage(href) {
    console.log(href)
    const index = window.location.href.lastIndexOf('/');
    if (index !== -1) {
        const kmlFile = zip.file(href.slice(index + 1));
        console.log(kmlFile);
        if (kmlFile) {
            
            return URL.createObjectURL(new Blob([kmlFile.asArrayBuffer()]));
            
        }
    }
    console.log(href);
    return href;
}

class KMZ extends KML {
    constructor(opt_options) {
        const options = opt_options || {};
        options.iconUrlFunction = getKMLImage;
        super(options);
    }
    
    getType() {
        return 'arraybuffer';
    }
    
    readFeature(source, options) {
        const kmlData = getKMLData(source);
        return super.readFeature(kmlData, options);
    }
    
    readFeatures(source, options) {
        const kmlData = getKMLData(source);
        console.log(kmlData);
        parseKML(kmlData);
        // kmlData.then(data => parseKML(data, event.file.name)).catch(error => console.error('Error parsing KML:', error));
        
        return super.readFeatures(kmlData, options);
    }
}

const fileInput = document.getElementById('fileInput');
const map = new Map({
    target: 'map',
    layers: [
        new TileLayer({
            source: new OSM(),
        }),
    ],
    view: new View({
        center: [0, 0],
        zoom: 2,
    }),
});
const csv_Input = document.getElementById('csv_Input');
csv_Input.addEventListener('change',function(event)
{
    const files = event.target.files[0];
    console.log(files);
    sendDataToServer(files)
    // const reader = new FileReader();

    // reader.onload = function(event) {
    //     const csvContent = event.target.result;
    //     const blob = new Blob([csvContent], { type: 'text/csv' });
    //     sendDataToServer(blob)
    // }
    // sendDataToServer(main_kml);
    // sendcsvDataToServer(main_csv
})
fileInput.addEventListener('change', function (event) {
    const files = event.target.files;
    sendForImages(files[0])
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log(file);
        const reader = new FileReader();
        reader.onload = function (event) {
            const buffer = event.target.result;
            JSZip.loadAsync(buffer).then(function (zip) {
                zip.file(/\.kml$/i)[0].async('text').then(function (kmlData) {
                    parseKML(kmlData);
                });
            });
        };
        reader.readAsArrayBuffer(file);
    }
});
function parseKML(kmlData) {
    // console.log(kmlData);
    sendXmlDataToServer(kmlData)
    main_kml=kmlData
    try {
        const parser = new DOMParser();
        const kmlDoc = parser.parseFromString(kmlData, 'text/xml');
        const groundOverlays = kmlDoc.querySelectorAll('GroundOverlay');
        
        groundOverlays.forEach(groundOverlay => {
            const imageUrl = groundOverlay.querySelector('Icon href').textContent;
            const latLonBox = groundOverlay.querySelector('LatLonBox');
            const north = parseFloat(latLonBox.querySelector('north').textContent);
            const south = parseFloat(latLonBox.querySelector('south').textContent);
            const east = parseFloat(latLonBox.querySelector('east').textContent);
            const west = parseFloat(latLonBox.querySelector('west').textContent);
            
            addImageOverlayFromHref(imageUrl, west, south, east, north);
        });
        
        const vectorSource = new VectorSource({
            features: new KML().readFeatures(kmlData, {
            dataProjection: 'EPSG:4326',  // Projection of the KML data
            featureProjection: 'EPSG:3857'  // Projection for the features
          })
        });
        const vectorLayer = new VectorLayer({
            source: vectorSource
        });
        map.addLayer(vectorLayer);
    } catch (error) {
        console.error('Error parsing KML and adding image overlay:', error);
    }
}

function addImageOverlayFromHref(href, west, south, east, north) {
    const url = "../";
    const newPath = url + href;
    const newPathUrl = newPath.replace(/\s/g, "");
    const imageOverlay = new ImageLayer({
        source: new ImageStatic({
            url: newPathUrl,
            projection: 'EPSG:4326',
            imageExtent: [west, south, east, north]
        })
    });
    map.addLayer(imageOverlay);
}
const sendXmlDataToServer = (file1) => {
    const endpointUrl = 'http://127.0.0.1:5000/process_xml';
    fetch(endpointUrl, {
        method: 'POST',
        body: file1,
        headers: {
            'Content-Type': 'application/xml'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.text(); // Assuming server responds with JSON
        }
        throw new Error('Failed to send KML data to server');
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
};

    
function sendDataToServer(main_csv) {
    const formData = new FormData();
    var post_data={}
    formData.append('csvData', main_csv);
    formData.append('xmldata', main_kml);
    formData.forEach(function (value, key) {
        post_data[key] = value;
      });
    console.log(post_data)
    // console.log(main_csv);
    const headers = new Headers();
    headers.append('Content-Type', 'text/csv','application/xml'); // for CSV
    // console.log(formData)
    fetch('http://127.0.0.1:5000/process_csv', {
        method: 'POST',
        body: post_data,
        headers:headers
    })
    .then(response => {
        if (response.ok) 
        {
            return response; // Assuming server responds with JSON
        }
        throw new Error('Failed to send data to server');
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
    


    
function sendForImages(file) {

    fetch('http://127.0.0.1:5000/images', {
        method: 'POST',
        body: file,
    })
    .then(response => {
        if (response.ok) 
        {
            return response; // Assuming server responds with JSON
        }
        throw new Error('Failed to send data to server');
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}