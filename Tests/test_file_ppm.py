import pytest

from PIL import Image, UnidentifiedImageError

from .helper import assert_image_equal, assert_image_similar, hopper

# sample ppm stream
TEST_FILE = "Tests/images/hopper.ppm"


def test_sanity():
    with Image.open(TEST_FILE) as im:
        im.load()
        assert im.mode == "RGB"
        assert im.size == (128, 128)
        assert im.format, "PPM"
        assert im.get_format_mimetype() == "image/x-portable-pixmap"


def test_16bit_pgm():
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        im.load()
        assert im.mode == "I"
        assert im.size == (20, 100)
        assert im.get_format_mimetype() == "image/x-portable-graymap"

        with Image.open("Tests/images/16_bit_binary_pgm.png") as tgt:
            assert_image_equal(im, tgt)


def test_16bit_pgm_write(tmp_path):
    with Image.open("Tests/images/16_bit_binary.pgm") as im:
        im.load()

        f = str(tmp_path / "temp.pgm")
        im.save(f, "PPM")

        with Image.open(f) as reloaded:
            assert_image_equal(im, reloaded)


def test_pnm(tmp_path):
    with Image.open("Tests/images/hopper.pnm") as im:
        assert_image_similar(im, hopper(), 0.0001)

        f = str(tmp_path / "temp.pnm")
        im.save(f)

        with Image.open(f) as reloaded:
            assert_image_equal(im, reloaded)


def test_header_with_comments(tmp_path):
    path = str(tmp_path / "temp.ppm")
    with open(path, "wb") as f:
        f.write(b"P6 #comment\n#comment\r12#comment\r8\n128 #comment\n255\n")

    with Image.open(path) as im:
        assert im.size == (128, 128)


def test_nondecimal_header(tmp_path):
    path = str(tmp_path / "temp.djvurle")
    with open(path, "wb") as f:
        f.write(b"P6\n128\x00")

    with pytest.raises(UnidentifiedImageError):
        Image.open(path)


def test_truncated_file(tmp_path):
    path = str(tmp_path / "temp.pgm")
    with open(path, "w") as f:
        f.write("P6")

    with pytest.raises(UnidentifiedImageError):
        Image.open(path)


def test_neg_ppm():
    # Storage.c accepted negative values for xsize, ysize.  the
    # internal open_ppm function didn't check for sanity but it
    # has been removed. The default opener doesn't accept negative
    # sizes.

    with pytest.raises(UnidentifiedImageError):
        Image.open("Tests/images/negative_size.ppm")


def test_mimetypes(tmp_path):
    path = str(tmp_path / "temp.pgm")

    with open(path, "w") as f:
        f.write("P4\n128 128\n255")
    with Image.open(path) as im:
        assert im.get_format_mimetype() == "image/x-portable-bitmap"

    with open(path, "w") as f:
        f.write("PyCMYK\n128 128\n255")
    with Image.open(path) as im:
        assert im.get_format_mimetype() == "image/x-portable-anymap"
