
const socket = io();
socket.on('stream_status', function (data) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = `${data.status}`;
    if (data.status === 'Active') {
        statusDiv.style.color = 'green';
        $('#start_stream_button').prop('disabled', true);
    } else if (data.status === 'Stopped') {
        statusDiv.style.color = 'red';
        $('#start_stream_button').prop('disabled', false);
    } else {
        statusDiv.style.color = 'black';
    }
});

socket.on('status_update', function (data) {
    $('#status').text(data.status);

    if (data.status === 'Active') {
        $('#status').css('color', 'green');
        $('#start_stream_button').prop('disabled', true);
    } else if (data.status === 'Stopped') {
        $('#status').css('color', 'red');
        $('#start_stream_button').prop('disabled', false);
    } else {
        $('#status').css('color', 'black'); // Default color for unknown status
    }
});
