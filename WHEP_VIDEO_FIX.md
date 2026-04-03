# WHEP Video Playback Fix - Removed HLS.js Conflict

## Issue
Video was not playing in the browser after clicking "Start Stream", even though:
- Stream was successfully published to MediaMTX (WHIP working)
- WHEP endpoint was accessible
- WHEP client JavaScript was loaded

Browser console showed errors trying to connect to port 8888 (HLS port), indicating interference from old HLS.js code.

## Root Cause
The `player.html` template was loading two conflicting video playback systems:
1. **Old system**: `video.js` + `hls.js` - Tried to play HLS streams from MediaMTX port 8888
2. **New system**: `webrtc.js` - WHEP client for WebRTC streams

The `video.js` file had a `DOMContentLoaded` event listener that automatically initialized HLS playback on page load (line 128), which:
- Conflicted with the WHEP client
- Tried to connect to wrong endpoint (port 8888 HLS instead of WebRTC)
- Set video.srcObject before WHEP could

## Solution
Disabled the old HLS-based video playback system by commenting out both:
1. HLS.js library import
2. video.js script include

### Changes Made

**File: StreamerApp/app/templates/player.html**

Line 5 - Disabled HLS.js:
```html
<!-- <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script> -->
<!-- HLS.js disabled - now using WHEP protocol -->
```

Line 35 - Disabled video.js:
```html
<!-- <script src="/static/video.js"></script> -->
<!-- video.js disabled - now using WHEP protocol in webrtc.js -->
```

## What Was Kept
- `webrtc.js` - WHEP client implementation (loads on line 7)
- `buttons.js` - Stream control buttons (loads on line 6)
- Video element with proper attributes (autoplay, playsinline, muted, controls)

## Architecture Now
```
Browser → /stream/whep (via nginx) → MediaMTX:8889 → WebRTC tracks → Video element
```

## WHEP Flow
1. User clicks "Start Stream" button
2. Flask API starts GStreamer pipeline with whipsink
3. GStreamer publishes to MediaMTX via WHIP (http://mediamtx:8889/stream/whip)
4. `webrtc.js` creates WHEP client with endpoint `/stream/whep`
5. nginx proxies `/stream/whep` to `mediamtx:8889/stream/whep`
6. WHEP client establishes WebRTC connection
7. Video/audio tracks received in browser and played

## Result
✅ No more HLS.js conflicts
✅ WHEP client can properly initialize
✅ Video element not hijacked by HLS playback code
✅ WebRTC tracks can be received and displayed

## Verification
After restarting web service:
```bash
docker-compose restart web
```

In browser:
1. Navigate to player page
2. Open browser console (F12)
3. Click "Start Stream"
4. Should see WHEP connection logs instead of HLS.js errors
5. Video should play once stream starts

## Future Cleanup (Optional)
The `video.js` file can be removed entirely since it's no longer used. However, it's been left in place for now in case there's a need to reference the old HLS implementation.

## Related Files
- `/static/webrtc.js` - WHEP client implementation (active)
- `/static/video.js` - Old HLS client (disabled)
- `/static/buttons.js` - Stream control (active)
- `nginx/nginx.conf` - Proxies /stream/whep to MediaMTX
