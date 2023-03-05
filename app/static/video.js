
var player = videojs('video-player');
var url = window.location.protocol + '//' + window.location.hostname + ':8080' + '/hls/stream.m3u8';


player.src({
    src: url,
    type: 'application/x-mpegURL'
});