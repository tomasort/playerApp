FROM python:3.9-alpine3.19

WORKDIR /app

# Enable the 'edge' repository for newer packages
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories && apk update

# Install GStreamer and its plugins (including WebRTC and Python bindings)
RUN apk add --no-cache \
    gstreamer \
    gst-plugins-base \
    gst-plugins-good \
    gst-plugins-bad \
    gst-plugins-ugly \
    gst-rtsp-server \
    gst-libav \
    musl-dev \
    cairo-dev \
    pkgconf \
    gcc \
    gst-plugins-rs \
    python3-dev \
    gobject-introspection-dev \
    gstreamer-tools \
    gstreamer-dev \
    g++ \
    libffi-dev \
    libnice-gstreamer \
    postgresql15 \
    build-base \
    linux-headers \
    libpq-dev \
    jpeg-dev \
    zlib-dev \
    py3-greenlet

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .