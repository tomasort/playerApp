var xhr = new XMLHttpRequest();
var colors_active = new Map();
colors_active.set("#C5C1C1", "#964A4A");
colors_active.set("#B0B0B0", "#858282");
var colors_passive = new Map();
// Extract inverted entries
for (let [key, value] of colors_active.entries()) {
    colors_passive.set(value, key);
}

function remote(button) {
    console.log("The button", button, "has been pressed!");
    xhr.open('POST', '/button', true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send(`button=${button}`);

    var group = document.getElementById(button);
    if (group) {
        var elements = group.getElementsByTagName('*');
        
        for (let i = 0; i < elements.length; i++) {
            let fillAttribute = elements[i].getAttribute('fill');
            let strokeAttribute = elements[i].getAttribute('stroke');

            if (fillAttribute !== null && colors_active.has(fillAttribute)) {
                elements[i].setAttribute('fill', colors_active.get(fillAttribute));
            }

            if (strokeAttribute !== null && colors_active.has(strokeAttribute)) {
                elements[i].setAttribute('stroke', colors_active.get(strokeAttribute));
            }
        }

        setTimeout(function() {
            for (let i = 0; i < elements.length; i++) {
                let fillAttribute = elements[i].getAttribute('fill');
                let strokeAttribute = elements[i].getAttribute('stroke');

                if (fillAttribute !== null && colors_passive.has(fillAttribute)) {
                    elements[i].setAttribute('fill', colors_passive.get(fillAttribute));
                }

                if (strokeAttribute !== null && colors_passive.has(strokeAttribute)) {
                    elements[i].setAttribute('stroke', colors_passive.get(strokeAttribute));
                }
            }
        }, 200); // Change 200 to the desired delay in milliseconds
    } else {
        console.log("Group not found");
    }
}

function stream(action) {
    const endpoints = {
        'start': '/stream/start',
        'stop': '/stream/stop', 
        'restart': '/stream/restart'
    };
    
    const endpoint = endpoints[action];
    if (!endpoint) {
        console.error('Invalid stream action:', action);
        return;
    }
    
    // Disable button during request
    const button = document.getElementById(`${action}_stream_button`);
    if (button) {
        button.disabled = true;
        const originalText = button.textContent;
        button.textContent = `${action.charAt(0).toUpperCase() + action.slice(1)}ing...`;
        
        // Re-enable after delay regardless of outcome
        setTimeout(() => {
            button.disabled = false;
            button.textContent = originalText;
        }, 2000);
    }
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Stream action successful:', data.message);
            if (data.task_id) {
                console.log('Task ID:', data.task_id);
            }
            // Update stream status after successful action
            updateStreamStatus();
        } else {
            console.error('Stream action failed:', data.error);
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Stream request failed:', error);
        alert('Request failed: ' + error.message);
    });
}

function updateStreamStatus() {
    fetch('/stream/status')
    .then(response => response.json())
    .then(status => {
        console.log('Stream status:', status);
        
        // Update button states based on status
        const startBtn = document.getElementById('start_stream_button');
        const stopBtn = document.getElementById('stop_stream_button');
        const restartBtn = document.getElementById('restart_stream_button');
        
        if (status.is_running) {
            if (startBtn) startBtn.disabled = true;
            if (stopBtn) stopBtn.disabled = false;
            if (restartBtn) restartBtn.disabled = false;
        } else {
            if (startBtn) startBtn.disabled = false;
            if (stopBtn) stopBtn.disabled = true;
            if (restartBtn) restartBtn.disabled = true;
        }
        
        // Could add status indicator to UI
        // Example: document.getElementById('status-indicator').textContent = 
        //          status.is_running ? 'Running' : 'Stopped';
    })
    .catch(error => {
        console.error('Failed to get stream status:', error);
    });
}

// Update status when page loads
document.addEventListener('DOMContentLoaded', function() {
    updateStreamStatus();
});
