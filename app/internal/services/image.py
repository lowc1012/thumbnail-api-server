import io

from PIL import Image, ImageOps

from app.internal.log.logger import get_logger

logger = get_logger()


class ImageService:
    def __init__(self):
        self.quality = 80

    def resize(self, image_bytes: bytes, size: tuple[int, int] = (100, 100)) -> tuple[bytes, str]:
        with io.BytesIO(image_bytes) as input_buffer:
            with Image.open(input_buffer) as img:
                img_format = img.format
                img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
                output_buffer = io.BytesIO()
                img.save(output_buffer, format=img_format, quality=self.quality)
                logger.info(f"Image resized to: {size}")
                return output_buffer.getvalue(), img_format