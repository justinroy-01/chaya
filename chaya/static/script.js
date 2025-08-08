// Tea Temperature Dashboard JavaScript
const tempValueElement = document.getElementById('temp-value');
const statusTextElement = document.getElementById('status-text');

// Variable to hold our interval timer
let fetchDataInterval;
let isStopped = false;

function updateUI(temp) {
    tempValueElement.innerText = temp;
    
    // Remove all temperature classes first
    tempValueElement.classList.remove('temp-cold', 'temp-perfect', 'temp-hot', 'temp-very-hot');
    
    let status = '';
    let colorClass = '';
    
    // Temperature-based status and color logic
    if (temp < 50) {
        status = 'Choodu Kuraiva'; // Less Hot
        colorClass = 'temp-cold';
    } else if (temp >= 50 && temp < 75) {
        status = 'Paakam Choodu'; // Perfect Temperature
        colorClass = 'temp-perfect';
    } else if (temp >= 75) {
        status = 'Nalla Choodu'; // Very Hot
        colorClass = 'temp-very-hot';
    }
    
    // Apply color class
    tempValueElement.classList.add(colorClass);
    
    // Only update status text if not stopped
    if (!isStopped) {
        statusTextElement.innerText = status;
    }
}

async function fetchData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/get_temp');
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        const temp = parseFloat(data.temperature);
        
        if (!isNaN(temp)) {
            updateUI(temp);
        } else {
            if (!isStopped) {
                statusTextElement.innerText = 'Waiting for valid data...';
            }
        }
    } catch (error) {
        console.error('Error fetching temperature:', error);
        if (!isStopped) {
            statusTextElement.innerText = 'Connection Error';
        }
    }
}

// Function to stop everything
function stopAll() {
    console.log("10 seconds are up. Stopping.");
    isStopped = true;
    
    // 1. Stop the frontend from asking for new data
    if (fetchDataInterval) {
        clearInterval(fetchDataInterval);
        fetchDataInterval = null;
    }
    
    // 2. Tell the backend to stop reading from Arduino
    fetch('http://127.0.0.1:5000/stop', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).catch(error => {
        console.error('Error sending stop request:', error);
    });
    
    // 3. Update the UI to show the final state
    statusTextElement.innerText = 'Final Reading';
}

// Main Execution on Page Load
window.onload = () => {
    console.log('Dashboard loaded. Starting temperature monitoring...');
    
    // Get the first reading immediately
    fetchData();
    
    // Start the refresh loop every 2 seconds
    fetchDataInterval = setInterval(fetchData, 2000);
    
    // Set a timer to stop everything after 10 seconds
    setTimeout(stopAll, 10000);
};
