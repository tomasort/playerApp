from celery import shared_task
from ..streaming import GstreamerPipeline


@shared_task(ignore_result=True)
def start_pipeline(video_src: str = None, audio_src: str = None, webrtc_uri: str = None) -> None:
    # Use test sources if no real video/audio sources are provided
    use_test_src = video_src is None or video_src == "" or video_src == "None"
    
    pipeline = GstreamerPipeline(
        v_src=video_src, 
        a_src=audio_src, 
        webrtc_uri=webrtc_uri,
        test_src=use_test_src
    )
    pipeline.start()
    return
