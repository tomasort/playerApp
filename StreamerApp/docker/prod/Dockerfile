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
    py3-greenlet \
    v4l-utils

RUN pip install --upgrade pip

# installing gevent takes way too long so I'm putting it here to cache it as a layer
RUN pip install gevent

COPY ./utils/remotes /remotes

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./docker/prod/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/local/worker.sh /worker.sh
RUN chmod +x /worker.sh

COPY ./docker/local/flower.sh /flower.sh
RUN chmod +x /flower.sh

COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

ENTRYPOINT [ "/entrypoint.sh" ]