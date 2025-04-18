const { app, BrowserWindow } = require('electron');
const path = require('path');

let mainWindow;

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            preload: path.join(__dirname, 'renderer.js'), // Correct path to renderer.js
            nodeIntegration: true, // Enable Node.js integration
            contextIsolation: false // Disable context isolation for simplicity
        }
    });

    mainWindow.loadFile('index.html');
});