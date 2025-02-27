import shutil
import tempfile
from pathlib import Path
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone

from ..models import Document, Correspondent


class TestDocument(TestCase):
    def setUp(self) -> None:
        self.originals_dir = tempfile.mkdtemp()
        self.thumb_dir = tempfile.mkdtemp()

        override_settings(
            ORIGINALS_DIR=self.originals_dir,
            THUMBNAIL_DIR=self.thumb_dir,
        ).enable()

    def tearDown(self) -> None:
        shutil.rmtree(self.originals_dir)
        shutil.rmtree(self.thumb_dir)

    def test_file_deletion(self):
        document = Document.objects.create(
            correspondent=Correspondent.objects.create(name="Test0"),
            title="Title",
            content="content",
            checksum="checksum",
            mime_type="application/pdf",
        )

        file_path = document.source_path
        thumb_path = document.thumbnail_path

        Path(file_path).touch()
        Path(thumb_path).touch()

        with mock.patch("documents.signals.handlers.os.unlink") as mock_unlink:
            document.delete()
            mock_unlink.assert_any_call(file_path)
            mock_unlink.assert_any_call(thumb_path)
            self.assertEqual(mock_unlink.call_count, 2)

    def test_file_name(self):

        doc = Document(
            mime_type="application/pdf",
            title="test",
            created=timezone.datetime(2020, 12, 25),
        )
        self.assertEqual(doc.get_public_filename(), "2020-12-25 test.pdf")

    def test_file_name_jpg(self):

        doc = Document(
            mime_type="image/jpeg",
            title="test",
            created=timezone.datetime(2020, 12, 25),
        )
        self.assertEqual(doc.get_public_filename(), "2020-12-25 test.jpg")

    def test_file_name_unknown(self):

        doc = Document(
            mime_type="application/zip",
            title="test",
            created=timezone.datetime(2020, 12, 25),
        )
        self.assertEqual(doc.get_public_filename(), "2020-12-25 test.zip")

    def test_file_name_invalid_type(self):

        doc = Document(
            mime_type="image/jpegasd",
            title="test",
            created=timezone.datetime(2020, 12, 25),
        )
        self.assertEqual(doc.get_public_filename(), "2020-12-25 test")
