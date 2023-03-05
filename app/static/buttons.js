function remote(button) {
    console.log("The button", button, "has been pressed!");
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the POST request to the /my-button route
    xhr.open('POST', '/button', true);

    // Set the content type of the request
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    // Send the POST request with any necessary data
    xhr.send(`button=${button}`);
}
function stream(action) {
    // Create a new XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // Define the POST request to the /my-button route
    xhr.open('POST', '/stream-control', true);

    // Set the content type of the request
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    // Send the POST request with any necessary data
    xhr.send(`action=${action}`);
}