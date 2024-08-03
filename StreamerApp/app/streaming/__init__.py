from .ffmpeg_pipeline import FFmpegPipeline
from .gstreamer_pipeline import GstreamerPipeline

def create_pipeline(pipeline_type, v_src, a_src):
    if pipeline_type == 'ffmpeg':
        return FFmpegPipeline(v_src, a_src)
    elif pipeline_type == 'gstreamer':
        return GstreamerPipeline(v_src, a_src)
    else:
        raise ValueError(f"Unknown pipeline type: {pipeline_type}")