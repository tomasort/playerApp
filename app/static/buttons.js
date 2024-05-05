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
    var xhr_stream = new XMLHttpRequest(); // Renamed to avoid conflict
    xhr_stream.open('POST', '/stream-control', true);
    xhr_stream.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr_stream.send(`action=${action}`);
}
