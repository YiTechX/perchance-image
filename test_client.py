import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
from PIL import Image

from perchance_client import (
    normalize_shape,
    PerchanceImageClient,
    SHAPE_MAPPINGS,
    POPULAR_STYLES,
)


class TestPerchanceClient(unittest.TestCase):
    def test_normalize_shape(self):
        self.assertEqual(normalize_shape("square"), "768x768")
        self.assertEqual(normalize_shape("1:1"), "768x768")
        self.assertEqual(normalize_shape("portrait"), "512x768")
        self.assertEqual(normalize_shape("9:16"), "512x768")
        self.assertEqual(normalize_shape("landscape"), "768x512")
        self.assertEqual(normalize_shape("16:9"), "768x512")
        self.assertEqual(normalize_shape(None), "768x768")
        self.assertEqual(normalize_shape("unknown"), "768x768")

    def test_empty_prompt_raises(self):
        client = PerchanceImageClient(headless=True)
        with self.assertRaises(ValueError):
            client.generate(prompt="")
        with self.assertRaises(ValueError):
            client.generate(prompt="   ")

    def test_generate_mock_pipeline(self):
        # Create a small base64 test image
        img = Image.new("RGB", (64, 64), color="red")
        import io
        import base64
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        mock_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        mock_perchancy_client = MagicMock()
        mock_perchancy_client.images.generate.return_value = {
            "created": 1234567,
            "data": [{"url": f"data:image/png;base64,{mock_b64}"}]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            client = PerchanceImageClient(headless=True)
            with patch.object(client, "_get_client", return_value=mock_perchancy_client):
                res = client.generate(
                    prompt="a test red square",
                    style="Cinematic",
                    shape="16:9",
                    output_dir=tmpdir
                )

                self.assertEqual(res["prompt"], "a test red square")
                self.assertEqual(res["style"], "Cinematic")
                self.assertEqual(res["shape"], "768x512")
                self.assertEqual(len(res["saved_paths"]), 1)
                self.assertTrue(os.path.exists(res["saved_paths"][0]))
                self.assertEqual(len(res["images"]), 1)
                self.assertEqual(res["images"][0].size, (64, 64))


if __name__ == "__main__":
    unittest.main()
