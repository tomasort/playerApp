from celery import shared_task
from ..streaming import GstreamerPipeline
from ..models import PipelineSession
from .. import db
from datetime import datetime


@shared_task(ignore_result=True)
def start_pipeline(video_src: str = None, audio_src: str = None, webrtc_uri: str = None) -> None:
    task_id = start_pipeline.request.id
    session = None
    
    try:
        # Find the session record
        session = PipelineSession.query.filter_by(task_id=task_id).first()
        if session:
            session.status = 'running'
            db.session.commit()
        
        # Use test sources if no real video/audio sources are provided
        use_test_src = video_src is None or video_src == "" or video_src == "None"
        
        pipeline = GstreamerPipeline(
            v_src=video_src, 
            a_src=audio_src, 
            webrtc_uri=webrtc_uri,
            test_src=use_test_src
        )
        pipeline.start()  # This blocks until pipeline stops
        
    except Exception as e:
        # Mark session as failed
        if session:
            session.status = 'failed'
            session.stopped_at = datetime.utcnow()
            db.session.commit()
        raise
    finally:
        # Mark session as stopped when pipeline ends
        if session and session.status == 'running':
            session.stop_session()
    
    return
