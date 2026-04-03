// WHEP (WebRTC-HTTP Egress Protocol) Client
// This replaces the old GstWebRTCAPI with standard WHEP protocol

class WHEPClient {
    constructor(whepEndpoint) {
        this.whepEndpoint = whepEndpoint;
        this.peerConnection = null;
        this.resourceUrl = null;
    }

    async connect(videoElement) {
        try {
            console.log('WHEPClient: Starting connection to', this.whepEndpoint);
            
            // Create a new RTCPeerConnection
            this.peerConnection = new RTCPeerConnection({
                iceServers: [
                    { urls: 'stun:stun.l.google.com:19302' }
                ]
            });

            console.log('WHEPClient: RTCPeerConnection created');

            // Set up event handlers
            this.peerConnection.ontrack = (event) => {
                console.log('WHEPClient: Received track:', event.track.kind, 'readyState:', event.track.readyState);
                console.log('WHEPClient: Stream:', event.streams[0]);
                
                if (videoElement.srcObject !== event.streams[0]) {
                    videoElement.srcObject = event.streams[0];
                    console.log('WHEPClient: Video element srcObject set');
                    
                    videoElement.play()
                        .then(() => console.log('WHEPClient: Video playing successfully'))
                        .catch(e => console.error('WHEPClient: Error playing video:', e));
                } else {
                    console.log('WHEPClient: Stream already set');
                }
            };

            this.peerConnection.oniceconnectionstatechange = () => {
                console.log('WHEPClient: ICE connection state:', this.peerConnection.iceConnectionState);
                if (this.peerConnection.iceConnectionState === 'failed' || 
                    this.peerConnection.iceConnectionState === 'disconnected') {
                    console.error('WHEPClient: Connection lost, attempting to reconnect...');
                }
            };
            
            this.peerConnection.onconnectionstatechange = () => {
                console.log('WHEPClient: Connection state:', this.peerConnection.connectionState);
            };

            // Add transceivers for receiving video and audio
            console.log('WHEPClient: Adding transceivers');
            this.peerConnection.addTransceiver('video', { direction: 'recvonly' });
            this.peerConnection.addTransceiver('audio', { direction: 'recvonly' });

            // Create an offer
            console.log('WHEPClient: Creating offer');
            const offer = await this.peerConnection.createOffer();
            await this.peerConnection.setLocalDescription(offer);
            console.log('WHEPClient: Local description set');

            // Wait for ICE gathering to complete
            console.log('WHEPClient: Waiting for ICE gathering');
            await this.waitForIceGathering();
            console.log('WHEPClient: ICE gathering complete');

            // Send the offer to the WHEP endpoint
            console.log('WHEPClient: Sending offer to', this.whepEndpoint);
            const response = await fetch(this.whepEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/sdp'
                },
                body: this.peerConnection.localDescription.sdp
            });

            console.log('WHEPClient: Response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('WHEPClient: WHEP request failed:', response.status, errorText);
                throw new Error(`WHEP request failed: ${response.status} ${response.statusText}`);
            }

            // Get the resource URL for later cleanup
            this.resourceUrl = response.headers.get('Location');
            console.log('WHEPClient: Resource URL:', this.resourceUrl);

            // Set the answer from the server
            const answerSdp = await response.text();
            console.log('WHEPClient: Received answer SDP');
            
            await this.peerConnection.setRemoteDescription({
                type: 'answer',
                sdp: answerSdp
            });
            console.log('WHEPClient: Remote description set');

            console.log('WHEPClient: Connection established successfully');
            return true;
        } catch (error) {
            console.error('WHEPClient: Error connecting:', error);
            this.close();
            return false;
        }
    }

    async waitForIceGathering() {
        return new Promise((resolve) => {
            if (this.peerConnection.iceGatheringState === 'complete') {
                resolve();
            } else {
                const checkState = () => {
                    if (this.peerConnection.iceGatheringState === 'complete') {
                        this.peerConnection.removeEventListener('icegatheringstatechange', checkState);
                        resolve();
                    }
                };
                this.peerConnection.addEventListener('icegatheringstatechange', checkState);
            }
        });
    }

    async close() {
        // Delete the resource on the server if we have a resource URL
        if (this.resourceUrl) {
            try {
                await fetch(this.resourceUrl, { method: 'DELETE' });
            } catch (error) {
                console.error('Error deleting WHEP resource:', error);
            }
            this.resourceUrl = null;
        }

        // Close the peer connection
        if (this.peerConnection) {
            this.peerConnection.close();
            this.peerConnection = null;
        }
    }
}

// Initialize the WHEP client when DOM is ready
let whepClient = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds

async function startWHEPStream() {
    const videoElement = document.getElementById("video");
    
    // Use same origin as web interface (proxied through nginx)
    const whepEndpoint = `${window.location.origin}/stream/whep`;
    
    console.log('Connecting to WHEP endpoint:', whepEndpoint);
    
    // Clean up existing connection
    if (whepClient) {
        await whepClient.close();
    }
    
    // Create new WHEP client and connect
    whepClient = new WHEPClient(whepEndpoint);
    const success = await whepClient.connect(videoElement);
    
    if (success) {
        reconnectAttempts = 0;
    } else if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        console.log(`Reconnection attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS} in ${RECONNECT_DELAY/1000}s...`);
        setTimeout(startWHEPStream, RECONNECT_DELAY);
    } else {
        console.error('Max reconnection attempts reached');
    }
}

async function stopWHEPStream() {
    if (whepClient) {
        await whepClient.close();
        whepClient = null;
    }
    
    const videoElement = document.getElementById("video");
    videoElement.srcObject = null;
    videoElement.pause();
}

// Check stream status and auto-connect when stream is running
async function checkStreamStatus() {
    try {
        const response = await fetch('/stream/status');  // Removed trailing slash
        const data = await response.json();
        
        console.log('Stream status check:', data);
        
        if (data.is_running && !whepClient) {
            // Stream is running but we're not connected, so connect
            console.log('Stream running, connecting to WHEP...');
            setTimeout(startWHEPStream, 1000); // Small delay to ensure stream is ready
        } else if (!data.is_running && whepClient) {
            // Stream stopped, disconnect
            console.log('Stream stopped, disconnecting WHEP...');
            await stopWHEPStream();
        }
    } catch (error) {
        console.error('Error checking stream status:', error);
    }
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
    console.log('WHEP client initialized');
    
    // Check stream status immediately
    checkStreamStatus();
    
    // Poll for stream status every 5 seconds
    setInterval(checkStreamStatus, 5000);
});

// Clean up on page unload
window.addEventListener("beforeunload", () => {
    if (whepClient) {
        whepClient.close();
    }
});
