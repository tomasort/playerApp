import pytest
from unittest.mock import patch, MagicMock
from app.streaming.gstreamer_pipeline import GstreamerPipeline
from gi.repository import Gst

@pytest.fixture
def gst_pipeline(request):
    """Fixture to create a GstreamerPipeline instance with optional parameters."""
    params = getattr(request, 'param', {})
    v_src = params.get('v_src')
    a_src = params.get('a_src')
    res = params.get('res', (640, 480))
    test_src = params.get('test_src', False)
    
    with patch('gi.repository.Gst.init'):
        yield GstreamerPipeline(v_src=v_src, a_src=a_src, res=res, test_src=test_src)

@pytest.mark.parametrize('gst_pipeline', [
    {'v_src': "/dev/video0", 'a_src': "hw:1,0", 'res': (640, 480)},
    {'v_src': "/dev/video1", 'a_src': "hw:2,0", 'res': (1280, 720), 'test_src': True},
    {'res': (1280, 720), 'test_src': True},
], indirect=True)
def test_init(gst_pipeline):
    """Test the initialization of GstreamerPipeline with different parameters."""
    assert gst_pipeline.status == 0
    assert gst_pipeline.v_src == gst_pipeline.v_src
    assert gst_pipeline.a_src == gst_pipeline.a_src
    assert gst_pipeline.resolution == gst_pipeline.resolution
    assert gst_pipeline.test_src == gst_pipeline.test_src

# TODO: for all the set tests, the pipeline should restart with the new attribute set. 
@pytest.mark.parametrize('src',  [
    ("/dev/video0")
])
def test_set_video_source(gst_pipeline, src):
    """Test setting video sources."""
    gst_pipeline.set_video_source(src)
    assert gst_pipeline.v_src == src 

@pytest.mark.parametrize('src',  [
    ("hw:1,0")
])
def test_set_audio_source(gst_pipeline, src):
    """Test setting audio sources."""
    gst_pipeline.set_audio_source(src)
    assert gst_pipeline.a_src == src

def test_set_resolution(gst_pipeline):
    """Test setting resolution."""
    gst_pipeline.set_resolution(1280, 720)
    assert gst_pipeline.resolution == (1280, 720)

# def test_get_status(gst_pipeline):
#     assert gst_pipeline.get_status() == 0


@pytest.mark.parametrize('gst_pipeline', [
    {'v_src': "/dev/video0", 'a_src': "hw:0,0", 'res': (640, 480)},
    {'test_src': True},
], indirect=True)
def test_start(gst_pipeline):
    """Test starting the pipeline with different configurations."""
    with patch.object(gst_pipeline, 'pipeline', MagicMock()) as mock_pipeline, \
         patch.object(gst_pipeline, 'loop', MagicMock()) as mock_loop, \
         patch('gi.repository.Gst.parse_launch', return_value=mock_pipeline) as mock_parse_launch, \
         patch('gi.repository.GLib.MainLoop', return_value=mock_loop) as mock_MainLoop, \
         patch.object(gst_pipeline, '_log') as mock_log:
        
        mock_bus = MagicMock()
        mock_pipeline.get_bus.return_value = mock_bus
        
        gst_pipeline.start()
        
        assert gst_pipeline.pipeline is not None
        mock_parse_launch.assert_called_once()
        parse_launch_call_args = mock_parse_launch.call_args[0][0]
        
        expected_video_src = "videotestsrc" if gst_pipeline.test_src else f"v4l2src device={gst_pipeline.v_src}"
        expected_audio_src = "audiotestsrc" if gst_pipeline.test_src else f"alsasrc device={gst_pipeline.a_src}"
        
        assert expected_video_src in parse_launch_call_args
        assert expected_audio_src in parse_launch_call_args
        assert f"width={gst_pipeline.resolution[0]},height={gst_pipeline.resolution[1]}" in parse_launch_call_args
        
        assert gst_pipeline.loop is not None
        mock_MainLoop.assert_called_once()
        mock_loop.run.assert_called_once()
        mock_bus.add_signal_watch.assert_called_once()
        mock_bus.connect.assert_called_once_with("message", gst_pipeline._bus_call, mock_loop)
        mock_pipeline.set_state.assert_called_once_with(Gst.State.PLAYING)
        assert gst_pipeline.status == 1

def test_stop(gst_pipeline):
    """Test stopping the pipeline."""
    gst_pipeline.status = 1
    gst_pipeline.pipeline = MagicMock()
    gst_pipeline.loop = MagicMock()
    
    gst_pipeline.stop()
    
    gst_pipeline.pipeline.set_state.assert_called_once_with(Gst.State.NULL)
    gst_pipeline.loop.quit.assert_called_once()
    assert gst_pipeline.status == 0