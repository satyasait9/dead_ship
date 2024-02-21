const AdmZip = require('adm-zip');
const fs = require('fs');
const path = require('path');
const kmzFilePath = './RB1SX020716Sv033255_0000_020725_21092023DIP_VV_11_000_DQ_tar.kmz';
const extractionDir = './kmzImages';
if (!fs.existsSync(extractionDir)) {
    fs.mkdirSync(extractionDir);
}
// Read the KMZ file
const zip = new AdmZip(kmzFilePath);

zip.getEntries().forEach(entry => {
    if (!entry.isDirectory) {
        const entryFilePath = path.join(extractionDir, entry.entryName);
        const entryDir = path.dirname(entryFilePath);
        if (!fs.existsSync(entryDir)) {
            fs.mkdirSync(entryDir, { recursive: true });
        } 
        zip.extractEntryTo(entry, entryDir, false, true);
        console.log(`Extracted: ${entryFilePath}`);
    }
});

console.log('Extraction complete.');
