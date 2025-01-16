const dataDiv = document.getElementById('data');
const ws = new WebSocket(`ws://${window.location.host}/ws`);

// Function to get the current datetime in Pacific Time
function getPacificTime() {
    const options = {
        timeZone: 'America/Los_Angeles',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    };
    const formatter = new Intl.DateTimeFormat('en-US', options);
    const parts = formatter.formatToParts(new Date());
    return `${parts[0].value}-${parts[2].value}-${parts[4].value} ${parts[6].value}:${parts[8].value}:${parts[10].value}`;
}

ws.onmessage = (event) => {
    const timestamp = getPacificTime();
    const formattedData = `${timestamp} >> ${event.data}`;
    const newData = document.createElement('div');
    newData.textContent = formattedData;
    dataDiv.appendChild(newData);

    // Scroll to the bottom of the container to show the latest data
    dataDiv.scrollTop = dataDiv.scrollHeight;
};

ws.onopen = () => console.log("WebSocket connection established.");
ws.onclose = () => console.log("WebSocket connection closed.");

