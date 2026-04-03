# Minimal WHIP/WHEP Test

This is a bare-bones test to verify WHIP/WHEP streaming works.

## Quick Test

```bash
cd whep-test
docker-compose up -d
# Then open http://localhost:8080 in browser
```

## Components
- MediaMTX: WHIP ingest + WHEP playback
- Nginx: Simple web server for test page
- GStreamer: Runs on host to publish via WHIP
