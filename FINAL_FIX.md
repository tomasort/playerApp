# Final Fix - Nginx Dependency Issue

## Error
```
nginx: [emerg] host not found in upstream "mediamtx" in /etc/nginx/nginx.conf:38
```

## Root Cause
Nginx was starting before MediaMTX, so it couldn't resolve the `mediamtx` hostname in the docker network.

## Solution
Updated `docker-compose.yml` to:
1. Make nginx depend on mediamtx
2. Add nginx to webrtc-network so it can resolve mediamtx hostname
3. Fixed deprecated `webrtcAllowOrigin` → `webrtcAllowOrigins` in mediamtx.yml

### Changes:

**docker-compose.yml:**
```yaml
nginx:
  build:
    context: ./nginx
  ports:
    - 80:80
  depends_on:
    - web
    - mediamtx      # Added dependency
  networks:
    - proxy-server
    - webrtc-network  # Added network
```

**mediamtx.yml:**
```yaml
# Changed from:
webrtcAllowOrigin: "*"

# To:
webrtcAllowOrigins: ["*"]
```

## Verified Working
All 7 services now running successfully:
- ✅ nginx - accessible on port 80
- ✅ mediamtx - running on ports 8889, 8189
- ✅ web - Flask app on port 5000
- ✅ worker - Celery worker
- ✅ flower - monitoring on port 5555
- ✅ postgres - database
- ✅ rabbit - message broker

## Test It
```bash
# Start services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Check all running
docker-compose -f docker-compose.yml -f docker-compose.dev.yml ps

# Test WHEP endpoint
curl -I http://localhost/stream/whep

# Access web interface
# Open browser: http://odroid.local/
# Login: admin / admin123
# Click "Start Stream"
```

Everything should work now!
