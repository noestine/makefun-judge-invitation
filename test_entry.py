"""Tests for the judge-invitation entry.

main.py (stdlib only) validates letter.png against the competition gate
(whole PNG, <= 1,048,576 bytes, <= 1024x1024 px) and copies it to
/output/entry.png. render_letter.py draws letter.png with PIL in-session.

Run: python3 -m unittest test_entry -v
"""
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

REPO = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(REPO, "main.py")
RENDER = os.path.join(REPO, "render_letter.py")
LETTER = os.path.join(REPO, "letter.png")

MAX_BYTES = 1_048_576
MAX_DIM = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def make_png(path, width=64, height=64, extra=b""):
    """Write a minimal valid PNG of the given dimensions."""
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x00\x00\x00" * width for _ in range(height))
    with open(path, "wb") as f:
        f.write(PNG_MAGIC)
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(raw)))
        if extra:
            f.write(chunk(b"tEXt", extra))
        f.write(chunk(b"IEND", b""))


def run_main(input_path, output_path):
    return subprocess.run(
        [sys.executable, MAIN, "--input", input_path, "--output", output_path],
        capture_output=True, text=True, timeout=30,
    )


class TestMainGate(unittest.TestCase):
    def test_copies_valid_png_byte_identical(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "out", "entry.png")
            make_png(src, 1024, 1024)
            r = run_main(src, out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(src, "rb") as f, open(out, "rb") as g:
                self.assertEqual(f.read(), g.read())

    def test_creates_output_directory(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "brand", "new", "entry.png")
            make_png(src)
            r = run_main(src, out)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(out))

    def test_rejects_bad_magic(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "entry.png")
            with open(src, "wb") as f:
                f.write(b"not a png at all, just text........")
            r = run_main(src, out)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(out))
            self.assertNotIn("Traceback", r.stderr)

    def test_rejects_oversize_dimensions(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "entry.png")
            make_png(src, 1025, 1024)
            r = run_main(src, out)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(out))
            self.assertNotIn("Traceback", r.stderr)

    def test_rejects_oversize_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "entry.png")
            make_png(src, 64, 64)
            with open(src, "ab") as f:
                f.write(b"\x00" * (MAX_BYTES + 1 - os.path.getsize(src)))
            self.assertGreater(os.path.getsize(src), MAX_BYTES)
            r = run_main(src, out)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(out))

    def test_boundary_exactly_max_is_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "entry.png")
            make_png(src, 1024, 1024)
            with open(src, "ab") as f:
                f.write(b"\x00" * (MAX_BYTES - os.path.getsize(src)))
            self.assertEqual(os.path.getsize(src), MAX_BYTES)
            r = run_main(src, out)
            self.assertEqual(r.returncode, 0, r.stderr)

    def test_missing_input(self):
        with tempfile.TemporaryDirectory() as d:
            r = run_main(os.path.join(d, "nope.png"), os.path.join(d, "entry.png"))
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("Traceback", r.stderr)

    def test_truncated_png(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out = os.path.join(d, "entry.png")
            with open(src, "wb") as f:
                f.write(PNG_MAGIC + b"\x00\x00\x00\x0dIHDR\x00")
            r = run_main(src, out)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(os.path.exists(out))
            self.assertNotIn("Traceback", r.stderr)

    def test_output_path_is_a_file(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            blocker = os.path.join(d, "blocker")
            with open(blocker, "w") as f:
                f.write("x")
            make_png(src)
            r = run_main(src, os.path.join(blocker, "entry.png"))
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("Traceback", r.stderr)

    def test_deterministic_copy_twice(self):
        with tempfile.TemporaryDirectory() as d:
            src = os.path.join(d, "letter.png")
            out1 = os.path.join(d, "a.png")
            out2 = os.path.join(d, "b.png")
            make_png(src, 512, 512)
            self.assertEqual(run_main(src, out1).returncode, 0)
            self.assertEqual(run_main(src, out2).returncode, 0)

            def sha(path):
                with open(path, "rb") as f:
                    return hashlib.sha256(f.read()).hexdigest()
            self.assertEqual(sha(out1), sha(out2))
            self.assertEqual(sha(out1), sha(src))


class TestRenderLetter(unittest.TestCase):
    def test_render_produces_valid_gate_passing_png(self):
        r = subprocess.run([sys.executable, RENDER],
                           capture_output=True, text=True, timeout=120, cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.exists(LETTER))
        size = os.path.getsize(LETTER)
        self.assertLessEqual(size, MAX_BYTES, f"letter.png is {size} bytes")
        with open(LETTER, "rb") as f:
            data = f.read(33)
        self.assertTrue(data.startswith(PNG_MAGIC))
        width, height = struct.unpack(">II", data[16:24])
        self.assertLessEqual(width, MAX_DIM)
        self.assertLessEqual(height, MAX_DIM)
        self.assertEqual((width, height), (1024, 1024))

    def test_render_is_deterministic(self):
        def run():
            r = subprocess.run([sys.executable, RENDER],
                               capture_output=True, text=True, timeout=120, cwd=REPO)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(LETTER, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(run(), run())

    def test_letter_text_content(self):
        # The invitation text lives in render_letter.py as LETTER_TEXT.
        import importlib.util
        spec = importlib.util.spec_from_file_location("render_letter", RENDER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        text = mod.LETTER_TEXT
        self.assertIn("Dear Judge", text)
        self.assertIn("dinner", text.lower())
        self.assertIn("chair", text.lower())
        self.assertIn("garden", text.lower())
        self.assertIn("cannot literally visit", text)
        self.assertIn("cloud", text.lower())
        self.assertIn("cat", text.lower())
        words = text.split()
        self.assertLessEqual(len(words), 110, f"letter is {len(words)} words; keep type big")
        self.assertGreaterEqual(len(words), 50)


class TestEndToEnd(unittest.TestCase):
    def test_main_on_real_letter(self):
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "entry.png")
            r = subprocess.run([sys.executable, MAIN, "--input", LETTER,
                                "--output", out],
                               capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(LETTER, "rb") as f:
                expected = f.read()
            with open(out, "rb") as f:
                self.assertEqual(expected, f.read())


if __name__ == "__main__":
    unittest.main()
