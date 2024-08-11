from celery import shared_task
from ..streaming import GstreamerPipeline

@shared_task(ignore_result=True)
def start_pipeline(video_src: str, audio_src: str, webrtc_uri: str) -> None:
    pipeline = GstreamerPipeline(v_src=video_src, a_src=audio_src, webrtc_uri=webrtc_uri)
    pipeline.start()
    return