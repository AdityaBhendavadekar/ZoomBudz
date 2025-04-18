const axios = require('axios');

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const transcriptionsContainer = document.getElementById('transcriptions');

    startButton.addEventListener('click', async () => {
        try {
            const response = await axios.post('http://127.0.0.1:5000/start');
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
            const response = await axios.post('http://127.0.0.1:5000/stop');
            alert(response.data.status);
            startButton.disabled = false;
            stopButton.disabled = true;
        } catch (error) {
            console.error(error);
            alert('Failed to stop recording.');
        }
    });
});