import unittest
import warnings
from unittest.mock import patch
from PIL import Image
from io import BytesIO

class TestSecurityImageValidation(unittest.TestCase):
    def setUp(self):
        """Save original Pillow settings."""
        self.original_max_pixels = Image.MAX_IMAGE_PIXELS

    def tearDown(self):
        """Restore original Pillow settings."""
        Image.MAX_IMAGE_PIXELS = self.original_max_pixels

    def test_oversized_image_triggers_warning(self):
        """
        Tests that opening an image exceeding MAX_IMAGE_PIXELS issues a
        DecompressionBombWarning.
        """
        Image.MAX_IMAGE_PIXELS = 100 * 100
        img = Image.new('L', (101, 100))
        b = BytesIO()
        img.save(b, 'PNG')
        b.seek(0)

        with self.assertWarns(Image.DecompressionBombWarning):
            Image.open(b)

    def test_valid_sized_image_does_not_warn(self):
        """
        Tests that an image at the size limit does not issue a warning.
        """
        Image.MAX_IMAGE_PIXELS = 100 * 100
        img = Image.new('L', (100, 100))
        b = BytesIO()
        img.save(b, 'PNG')
        b.seek(0)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Capture all warnings
            Image.open(b)
            # Check that no DecompressionBombWarning was issued
            for warning_message in w:
                if issubclass(warning_message.category, Image.DecompressionBombWarning):
                    self.fail("DecompressionBombWarning was raised unexpectedly")

if __name__ == '__main__':
    unittest.main()
