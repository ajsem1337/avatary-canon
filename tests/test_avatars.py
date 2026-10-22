import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageChops

import tworzenie_avatarow as avatars


SCRIPT = Path(avatars.__file__).resolve()


class NormalizationTests(unittest.TestCase):
    def test_initials_are_cleaned_and_truncated(self):
        for value, expected in (
            (" mc ", "MC"),
            ("a-b_3", "AB"),
            ("łż", "ŁŻ"),
            ("7", "7"),
            (" -- ", ""),
        ):
            with self.subTest(value=value):
                self.assertEqual(avatars.normalize_initials(value), expected)

    def test_equivalent_unicode_has_the_same_initials(self):
        self.assertEqual(
            avatars.normalize_initials("z\u0307c\u0301"),
            avatars.normalize_initials("żć"),
        )


class RenderingTests(unittest.TestCase):
    def text_bounds(self, image, initials):
        background = Image.new("RGB", image.size, avatars.bg_from_text(initials))
        return ImageChops.difference(image, background).getbbox()

    def test_background_remains_compatible(self):
        self.assertEqual(avatars.bg_from_text("MC"), (1, 52, 171))

    def test_foreground_chooses_the_more_readable_color(self):
        for background, expected in (
            ((0, 0, 0), (255, 255, 255)),
            ((255, 255, 255), (0, 0, 0)),
            ((0, 160, 0), (0, 0, 0)),
            ((200, 0, 0), (255, 255, 255)),
            ((120, 120, 120), (0, 0, 0)),
        ):
            with self.subTest(background=background):
                self.assertEqual(avatars.fg_for_bg(background), expected)

    def test_rendering_is_repeatable(self):
        first = avatars.create_avatar("MC")
        second = avatars.create_avatar("MC")
        self.assertEqual(first.size, (256, 256))
        self.assertEqual(first.mode, "RGB")
        self.assertEqual(first.tobytes(), second.tobytes())

    def test_text_is_centered(self):
        for initials in ("MC", "WW", "IJ", "ŁŻ"):
            with self.subTest(initials=initials):
                image = avatars.create_avatar(initials)
                left, top, right, bottom = self.text_bounds(image, initials)
                self.assertLessEqual(abs((left + right) / 2 - 128), 4)
                self.assertLessEqual(abs((top + bottom) / 2 - 128), 2)

    def test_text_fits_smaller_canvases(self):
        for size in ((64, 64), (128, 64)):
            with self.subTest(size=size):
                image = avatars.create_avatar("WW", size=size)
                left, top, right, bottom = self.text_bounds(image, "WW")
                self.assertGreater(left, 0)
                self.assertGreater(top, 0)
                self.assertLess(right, size[0])
                self.assertLess(bottom, size[1])

    def test_missing_system_fonts_still_give_readable_text(self):
        original_truetype = avatars.ImageFont.truetype

        def bundled_font_only(font, size=10, *args, **kwargs):
            if isinstance(font, (str, Path)):
                raise OSError("No system font")
            return original_truetype(font, size, *args, **kwargs)

        with patch.object(avatars.ImageFont, "truetype", side_effect=bundled_font_only):
            image = avatars.create_avatar("MC")
        left, top, right, bottom = self.text_bounds(image, "MC")
        self.assertGreater(right - left, 80)
        self.assertGreater(bottom - top, 50)


class FontDiscoveryTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux XDG font discovery")
    def test_linux_user_fonts_are_found_in_custom_xdg_directory(self):
        bundled_font = avatars.ImageFont.load_default(size=32)
        with tempfile.TemporaryDirectory() as directory:
            font_path = Path(directory) / "fonts" / "custom" / "DejaVuSans-Bold.ttf"
            font_path.parent.mkdir(parents=True)
            font_path.write_bytes(bundled_font.path.getvalue())
            with patch.dict(os.environ, {
                "XDG_DATA_HOME": directory,
                "XDG_DATA_DIRS": directory,
            }):
                font = avatars.try_fonts(32)
            self.assertEqual(Path(font.path), font_path)
            self.assertEqual(font.size, 32)

    def test_other_platform_fonts_are_used_when_linux_fonts_are_missing(self):
        available_font = avatars.ImageFont.load_default(size=32)
        for available_name in ("segoeuib.ttf", "Arial Bold.ttf"):
            with self.subTest(font=available_name):
                def load_available(name, size):
                    if name == available_name:
                        return available_font
                    raise OSError("Font unavailable")

                with patch.object(avatars.ImageFont, "truetype", side_effect=load_available):
                    self.assertIs(avatars.try_fonts(32), available_font)


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
            cwd=self.directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def test_default_output_is_a_valid_png(self):
        result = self.run_cli("--user", "mc")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        output = Path(result.stdout.strip())
        self.assertEqual(output, Path("avatary") / "etg_MC.png")
        with Image.open(self.directory / output) as image:
            self.assertEqual(image.format, "PNG")
            self.assertEqual(image.size, (256, 256))
            self.assertEqual(image.mode, "RGB")
            image.load()

    def test_custom_output_directory_and_overwrite(self):
        output = self.directory / "nested folder" / "avatars" / "etg_MC.png"
        output.parent.mkdir(parents=True)
        output.write_bytes(b"old file")
        result = self.run_cli("--user", " m-c ", "--outdir", str(output.parent))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()), output)
        with Image.open(output) as image:
            image.verify()

    def test_polish_initials_are_preserved_in_the_filename(self):
        result = self.run_cli("--user", "łż")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = Path(result.stdout.strip())
        self.assertEqual(output.name, "etg_ŁŻ.png")
        with Image.open(self.directory / output) as image:
            image.verify()

    def test_invalid_initials_do_not_create_output(self):
        for value in ("", " ", "---"):
            with self.subTest(value=value):
                result = self.run_cli(f"--user={value}")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("1-2", result.stderr)
                self.assertFalse((self.directory / "avatary").exists())

    def test_missing_user_is_a_usage_error(self):
        self.assertEqual(self.run_cli().returncode, 2)

    def test_output_directory_error_has_no_traceback(self):
        output = self.directory / "file"
        output.write_text("existing file", encoding="utf-8")
        result = self.run_cli("--user", "mc", "--outdir", str(output))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(output.read_text(encoding="utf-8"), "existing file")

    def test_save_error_has_no_traceback(self):
        output = self.directory / "avatary" / "etg_MC.png"
        output.mkdir(parents=True)
        result = self.run_cli("--user", "mc")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())
        self.assertNotIn("Traceback", result.stderr)
        self.assertTrue(output.is_dir())


if __name__ == "__main__":
    unittest.main()
