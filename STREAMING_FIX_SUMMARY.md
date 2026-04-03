# Video Streaming Fix Summary

## Issue
Video not playing after starting the stream - browser couldn't connect to WHEP endpoint.

## Root Cause
The WHEP endpoint was on port 8889 which wasn't accessible from the browser. The JavaScript was trying to connect directly to `http://hostname:8889/stream/whep`, bypassing nginx.

## Solution
Added nginx proxy configuration for MediaMTX WHIP/WHEP endpoints and updated JavaScript to use the proxied endpoint.

### Changes Made:

#### 1. Updated nginx.conf
Added proxy configuration for `/stream/` paths to forward to MediaMTX:

```nginx
# Proxy WHIP/WHEP endpoints to MediaMTX
location /stream/ {
    proxy_pass http://mediamtx:8889/stream/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS headers for WebRTC
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PATCH, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;
    add_header Access-Control-Expose-Headers "Location, ETag, Accept-Patch, Link" always;
    
    # Handle OPTIONS preflight
    if ($request_method = OPTIONS) {
        return 204;
    }
}
```

#### 2. Updated webrtc.js
Changed WHEP endpoint to use the same origin (proxied through nginx):

```javascript
// BEFORE:
const whepEndpoint = `${protocol}://${window.location.hostname}:8889/stream/whep`;

// AFTER:
const whepEndpoint = `${window.location.origin}/stream/whep`;
```

## How It Works Now

### Complete Data Flow:

```
Browser → nginx (port 80) → MediaMTX (port 8889) → WHEP Stream
                                ↑
                                |
GStreamer → whipsink → WHIP → MediaMTX
```

### URL Paths:
- **Web Interface**: `http://odroid.local/` (nginx port 80)
- **WHEP Playback**: `http://odroid.local/stream/whep` (proxied to MediaMTX)
- **WHIP Ingestion**: `http://mediamtx:8889/stream/whip` (direct, internal only)

## Testing
After these changes, refresh your browser page and the video should start playing automatically when you click "Start Stream".

## Next Steps to Verify
1. Click "Start Stream" button
2. Open browser developer console (F12)
3. You should see: `Connecting to WHEP endpoint: http://odroid.local/stream/whep`
4. Video should start playing within 1-2 seconds

## Troubleshooting

### If video still doesn't play:

1. **Check browser console for errors**:
   - Press F12 → Console tab
   - Look for WebRTC errors

2. **Verify stream is running**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs worker | grep "Pipeline started"
   ```

3. **Check MediaMTX has active stream**:
   ```bash
   curl http://localhost:9997/v3/paths/list
   ```

4. **Test WHEP endpoint directly**:
   ```bash
   curl -I http://localhost/stream/whep
   ```

5. **Check nginx logs**:
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs nginx
   ```

## Architecture Benefits

✅ **Single Port Access**: Everything through port 80
✅ **No CORS Issues**: All same-origin requests
✅ **Secure**: No direct access to MediaMTX from browser
✅ **Production Ready**: Can add SSL/TLS to nginx easily
✅ **Flexible**: Can add authentication at nginx level

