FROM rust:1.80.1-alpine3.20

WORKDIR /app

RUN apk add --no-cache \
    build-base \
    libressl-dev

# Copy only the necessary directories
COPY . .

# Build and install the signalling server
WORKDIR /app/signalling

RUN cargo build 

CMD ["cargo", "run", "--bin", "gst-webrtc-signalling-server"]