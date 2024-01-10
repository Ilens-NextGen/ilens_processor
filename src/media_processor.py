from dataclasses import dataclass
import imageio.v3 as iio
from numpy import ndarray
import cv2
import numpy as np
import asyncio
from typing import List
from PIL import Image  # type: ignore


@dataclass
class AsyncVideoProcessor:
    """Process video bytes to frames and return a list of frames."""

    max_frames: int = 4
    grid: bool = True

    async def get_best_frame(self, video_bytes: bytes):
        """Return the best frame from a video."""
        frames, fps = await asyncio.to_thread(self._bytes_to_frames, video_bytes)
        selected_frames = await asyncio.to_thread(
            self._select_frames, frames, fps, self.max_frames
        )
        return selected_frames[3]

    async def process_video(
        self, video_bytes: bytes, max_frame: int = 4, grid=True
    ) -> List[ndarray]:
        try:
            # Convert video bytes to frames
            frames, fps = await asyncio.to_thread(self._bytes_to_frames, video_bytes)
            resized_frames = await asyncio.to_thread(self._resize_frames, frames)
            selected_frames = await asyncio.to_thread(
                self._select_frames, resized_frames, fps, max_frame  # type: ignore
            )
            if not grid:
                return selected_frames  # type: ignore
            grid_image = await asyncio.to_thread(self._create_grid, selected_frames)  # type: ignore
            return [grid_image]

        except Exception as e:
            raise e

    def _bytes_to_frames(self, video_bytes: bytes):
        frames = iio.imread(video_bytes, index=None, format_hint=".mp4")
        return frames, len(frames)

    def _resize_frames(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        return [cv2.resize(frame, (0, 0), fx=0.9, fy=0.9) for frame in frames]

    def _select_frames(
        self, frames: np.ndarray, fps: int, max_frame: int
    ) -> np.ndarray:
        total_frames = len(frames)
        duration = total_frames / fps
        step = int(total_frames / (duration * max_frame))
        return frames[::step] if len(frames) <= max_frame else frames[-max_frame:]

    def _create_grid(self, frames: List[np.ndarray]) -> np.ndarray:
        """
        Create a grid of 2x2 grid images from a list of frames.
        Args:
            frames (List[np.ndarray]): a list of frames
        Returns:
            np.ndarray: the composite image
        """
        # Assuming frames are of the same size
        height, width, _ = frames[0].shape
        grid_image = np.zeros((2 * height, 2 * width, 3), dtype=np.uint8)
        for i, frame in enumerate(frames):
            row = i // 2
            col = i % 2
            grid_image[
                row * height : (row + 1) * height, col * width : (col + 1) * width
            ] = frame
        return grid_image

    async def convert_result_image_arrays_to_bytes(self, images: List[np.ndarray]):
        for image in images:
            image_pil = Image.fromarray(image)
            yield image_pil.tobytes()
