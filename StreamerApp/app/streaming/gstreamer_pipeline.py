from .media_pipeline import MediaPipeline
from gi.repository import Gst, GstWebRTC, GLib
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstWebRTC', '1.0')


class GstreamerPipeline(MediaPipeline):
    def __init__(self, v_src=None, a_src=None, webrtc_uri=None, res=(1280, 720), test_src=False):
        super().__init__(v_src, a_src, res)
        Gst.init(None)
        self.pipeline = None
        self.loop = None
        self.test_src = test_src
        self.webrtc_uri = webrtc_uri
        if self.webrtc_uri is None:
            # this is the default uri for the signalling server in webrtsink
            self.webrtc_uri = "ws://localhost:8443"

    def start(self):
        if self.status == 1:
            self._log("Pipeline is already running")
            return
        gstreamer_video_src = f"v4l2src device={self.v_src}"
        gstreamer_audio_src = f"alsasrc device={self.a_src}"
        if self.test_src:
            gstreamer_video_src = "videotestsrc"
            gstreamer_audio_src = "audiotestsrc"
        pipeline_str = f"""
        webrtcsink signaller::uri={self.webrtc_uri} name=ws meta="meta,name=gst-stream"
        {gstreamer_video_src} ! video/x-raw,width={self.resolution[0]},height={self.resolution[1]} ! videoconvert ! queue ! ws.
        {gstreamer_audio_src} ! audio/x-raw ! audioconvert ! audioresample ! queue ! ws.
        """
        print(pipeline_str)

        self.pipeline = Gst.parse_launch(pipeline_str)

        # Set up bus message handling
        self.loop = GLib.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._bus_call)

        # Start playing the pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        self.status = 1
        self._log("Pipeline started")

        try:
            self.loop.run()
        except KeyboardInterrupt:
            self._log("Keyboard interrupt received")
            self.stop()

    def stop(self):
        if self.status == 0:
            self._log("Pipeline is already stopped")
            return

        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        if self.loop:
            self.loop.quit()
        self.status = 0
        self._log("Pipeline stopped")

    def get_status(self):
        return self.status

    def _bus_call(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self._log("End-of-stream")
            self.stop()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            self._log(f"Error: {err} {debug}")
            self.stop()
        return True

    def set_video_source(self, src):
        super().set_video_source(src)
        if self.status == 1:
            self._log("Pipeline needs to be restarted for changes to take effect")

    def set_audio_source(self, src):
        super().set_audio_source(src)
        if self.status == 1:
            self._log("Pipeline needs to be restarted for changes to take effect")

    def set_resolution(self, width, height):
        super().set_resolution(width, height)
        if self.status == 1:
            self._log("Pipeline needs to be restarted for changes to take effect")
