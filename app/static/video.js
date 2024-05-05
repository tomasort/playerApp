const create = (video) => {
    // always prefer hls.js over native HLS.
    // this is because some Android versions support native HLS
    // but don't support fMP4s.
    var url = window.location.protocol + '//' + window.location.hostname + ':8888' + '/mystream/index.m3u8';
    if (Hls.isSupported()) {
        const hls = new Hls({
            maxLiveSyncPlaybackRate: 1,
            liveSyncDurationCount: 1, 
            liveMaxLatencyDurationCount: 2.5, 
            liveDurationInfinity: true
        });

        hls.on(Hls.Events.ERROR, (evt, data) => {
            if (data.type === Hls.ErrorTypes.MEDIA_ERROR){
                console.log("hls error");
                hls.recoverMediaError();
            }else if (data.fatal) {
                hls.destroy();
                setTimeout(() => create(video), 2000);
            }
        });

        hls.on(Hls.Events.MEDIA_ATTACHED, () => {
            hls.loadSource(url);
        });

        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            video.play();
        });

        hls.attachMedia(video);

    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        // since it's not possible to detect timeout errors in iOS,
        // wait for the playlist to be available before starting the stream
        fetch(url)
            .then(() => {
                video.src = url;
                video.play();
            });
    }
};

/**
 * Parses the query string from a URL into an object representing the query parameters.
 * If no URL is provided, it uses the query string from the current page's URL.
 *
 * @param {string} [url=window.location.search] - The URL to parse the query string from.
 * @returns {Object} An object representing the query parameters with keys as parameter names and values as parameter values.
 */
const parseQueryString = (url) => {
    const queryString = (url || window.location.search).split("?")[1];
    if (!queryString) return {};

    const paramsArray = queryString.split("&");
    const result = {};

    for (let i = 0; i < paramsArray.length; i++) {
        const param = paramsArray[i].split("=");
        const key = decodeURIComponent(param[0]);
        const value = decodeURIComponent(param[1] || "");

        if (key) {
            if (result[key]) {
                if (Array.isArray(result[key])) {
                    result[key].push(value);
                } else {
                    result[key] = [result[key], value];
                }
            } else {
                result[key] = value;
            }
        }
    }

    return result;
};

/**
 * Parses a string with boolean-like values and returns a boolean.
 * @param {string} str The string to parse
 * @param {boolean} defaultVal The default value
 * @returns {boolean}
 */
const parseBoolString = (str, defaultVal) => {
    const trueValues = ["1", "yes", "true"];
    const falseValues = ["0", "no", "false"];
    str = (str || "").toString();

    if (trueValues.includes(str.toLowerCase())) {
        return true;
    } else if (falseValues.includes(str.toLowerCase())) {
        return false;
    } else {
        return defaultVal;
    }
};

/**
 * Sets video attributes based on query string parameters or default values.
 *
 * @param {HTMLVideoElement} video - The video element on which to set the attributes.
 */
const setVideoAttributes = (video) => {
    let qs = parseQueryString();

    video.controls = parseBoolString(qs["controls"], true);
    video.muted = parseBoolString(qs["muted"], true);
    video.autoplay = parseBoolString(qs["autoplay"], true);
    video.playsInline = parseBoolString(qs["playsinline"], true);
};

/**
 *
 * @param {(video: HTMLVideoElement) => void} callback
 * @param {HTMLElement} container
 * @returns
 */
const initVideoElement = (callback) => {
    return () => {
        const video = document.getElementById('video');;
        setVideoAttributes(video);
        callback(video);
    };
};

window.addEventListener('DOMContentLoaded', initVideoElement(create));

