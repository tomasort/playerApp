from abc import ABC, abstractmethod
import json

class MediaPipeline(ABC):
    """
    Abstract base class for a media pipeline that handles video and audio sources.

    Attributes:
        v_src (str): Video source.
        a_src (str): Audio source.
        status (int): Current status of the pipeline (0: Stopped, 1: Running).
        resolution (tuple): Resolution of the video as a (width, height) tuple.
        log (list): List to store log messages.
    """

    def __init__(self, v_src=None, a_src=None, res=(640, 480)):
        """
        Initializes the MediaPipeline with optional video and audio sources.

        Args:
            v_src (str, optional): Initial video source. Defaults to None.
            a_src (str, optional): Initial audio source. Defaults to None.
            res (tuple, optional): Initial video resolution. Defaults to (640, 480).
        """
        self.status = 0  # 0: Stopped, 1: Running, other states can be defined
        self.v_src = v_src 
        self.a_src = a_src
        self.resolution = res
        self.log = []

    @abstractmethod
    def start(self) -> None:
        """
        Starts the media pipeline.
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Stops the media pipeline.
        """
        pass

    @abstractmethod
    def get_status(self) -> int:
        """
        Gets the current status of the media pipeline.

        Returns:
            int: Current status (0: Stopped, 1: Running).
        """
        pass

    def set_video_source(self, src: str) -> None:
        """
        Sets the video source.

        Args:
            src (str): Path or identifier for the video source.
        """
        self.v_src = src
        self._log(f"Video source set to {src}")

    def get_video_source(self) -> str:
        """
        Gets the current video source.

        Returns:
            str: Current video source.
        """
        return self.v_src

    def set_audio_source(self, src: str) -> None:
        """
        Sets the audio source.

        Args:
            src (str): Path or identifier for the audio source.
        """
        self.a_src = src
        self._log(f"Audio source set to {src}")

    def get_audio_source(self) -> str:
        """
        Gets the current audio source.

        Returns:
            str: Current audio source.
        """
        return self.a_src

    def set_resolution(self, width: int, height: int) -> None:
        """
        Sets the resolution of the video.

        Args:
            width (int): The width of the video resolution.
            height (int): The height of the video resolution.
        """
        self.resolution = (width, height)
        self._log(f"Resolution set to {width}x{height}")

    def get_resolution(self) -> tuple:
        """
        Gets the current video resolution.

        Returns:
            tuple: Current video resolution as (width, height).
        """
        return self.resolution

    def restart(self) -> None:
        """
        Restarts the media pipeline by stopping and then starting it again.
        """
        self.stop()
        self.start()
        self._log("Pipeline restarted")

    def _log(self, message: str) -> None:
        """
        Logs a message to the internal log list and prints it.

        Args:
            message (str): The message to log.
        """
        self.log.append(message)
        print(message)  # Or use a proper logging mechanism

    def save_config(self, filepath: str) -> None:
        """
        Saves the current configuration to a file.

        Args:
            filepath (str): Path to the file where the configuration will be saved.
        """
        config = {
            "v_src": self.v_src,
            "a_src": self.a_src,
            "status": self.status,
            "resolution": self.resolution
        }
        with open(filepath, 'w') as f:
            json.dump(config, f)
        self._log(f"Configuration saved to {filepath}")

    def load_config(self, filepath: str) -> None:
        """
        Loads configuration from a file.

        Args:
            filepath (str): Path to the file from which the configuration will be loaded.
        """
        with open(filepath, 'r') as f:
            config = json.load(f)
        self.v_src = config.get("v_src")
        self.a_src = config.get("a_src")
        self.status = config.get("status", 0)
        self.resolution = config.get("resolution", (640, 480))
        self._log(f"Configuration loaded from {filepath}")
