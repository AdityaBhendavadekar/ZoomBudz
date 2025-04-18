const axios = require('axios');

const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const transcriptionsContainer = document.getElementById('transcriptions');

startButton.addEventListener('click', async () => {
    try {
        const response = await axios.post('http://localhost:5000/start');
        alert(response.data.status);
        startButton.disabled = true;
        stopButton.disabled = false;
    } catch (error) {
        console.error(error);
        alert('Failed to start recording.');
    }
});

stopButton.addEventListener('click', async () => {
    try {
        const response = await axios.post('http://localhost:5000/stop');
        alert(response.data.status);
        startButton.disabled = false;
        stopButton.disabled = true;
    } catch (error) {
        console.error(error);
        alert('Failed to stop recording.');
    }
});

async function fetchTranscriptions() {
    try {
        const response = await axios.get('http://localhost:5000/transcribe');
        const transcriptions = response.data;
        transcriptionsContainer.innerHTML = ''; // Clear previous content
        if (Object.keys(transcriptions).length === 0) {
            transcriptionsContainer.innerHTML = '<p>No transcriptions yet...</p>';
        } else {
            for (const [filename, text] of Object.entries(transcriptions)) {
                const p = document.createElement('p');
                p.innerHTML = `<strong>${filename}:</strong> ${text}`;
                transcriptionsContainer.appendChild(p);
            }
        }
    } catch (error) {
        console.error(error);
    }
}

// Fetch transcriptions every 10 seconds
setInterval(fetchTranscriptions, 10000);