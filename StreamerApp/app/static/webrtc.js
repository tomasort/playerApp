function initStream(api) {
    const playerElement = document.getElementById("player");
    const videoElement = document.getElementById("video");
    const listener = {
        producerAdded: (producer) => {
            console.log("A producer was added");
            producerId = producer.id
            playerElement.insertAdjacentHTML("beforeend", `<div id="${producerId}"></div>`);
            const entryElement = document.getElementById(producerId); // This needs to be refactored into a map or something. 

            if (entryElement.classList.contains("has-session")) {
                entryElement.classList.add("streaming");
            }

            if (entryElement._consumerSession) {
                entryElement._consumerSession.close();
            } else {
                const session = api.createConsumerSession(producerId);
                console.log("Created a consumer session for producer: " + producer.meta.name)
                if (session) {
                    entryElement._consumerSession = session;

                    session.addEventListener("error", (event) => {
                        if (entryElement._consumerSession === session) {
                            console.error(event.message, event.error);
                        }
                    });

                    session.addEventListener("closed", () => {
                        if (entryElement._consumerSession === session) {
                            videoElement.pause();
                            videoElement.srcObject = null;
                            entryElement.classList.remove("has-session", "streaming");
                            delete entryElement._consumerSession;
                        }
                    });

                    session.addEventListener("streamsChanged", () => {
                        if (entryElement._consumerSession === session) {
                            const streams = session.streams;
                            if (streams.length > 0) {
                                videoElement.srcObject = streams[0];
                                videoElement.play().catch(() => { });
                            }
                        }
                    });

                    entryElement.classList.add("has-session");
                    session.connect();
                }
            }

        },
        producerRemoved: (producer) => {
            console.log("A producer was removed");
            const element = document.getElementById(producer.id);
            if (element) {
                if (element._consumerSession) {
                    element._consumerSession.close();
                }
                element.remove();
            }
        }
    };
    api.registerProducersListener(listener);
    for (const producer of api.getAvailableProducers()) {
        listener.producerAdded(producer);
    }
}
window.addEventListener("DOMContentLoaded", () => {
    const signalingProtocol = window.location.protocol.startsWith("https") ? "wss" : "ws";
    const gstWebRTCConfig = {
        meta: { name: `WebClient-${Date.now()}` },
        signalingServerUrl: `${signalingProtocol}://192.168.1.50:8443/webrtc`,
    };

    const api = new GstWebRTCAPI(gstWebRTCConfig);
    initStream(api);
});
