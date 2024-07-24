FROM rust:latest

WORKDIR /usr/src/app

# Copy only the necessary directories
COPY ./signalling signalling
COPY ./protocol protocol

# Build and install the signalling server
WORKDIR /usr/src/app/signalling

RUN cargo build 

CMD ["cargo", "run", "--bin", "gst-webrtc-signalling-server"]