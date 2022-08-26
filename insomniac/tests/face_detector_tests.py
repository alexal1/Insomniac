import os
import unittest

from insomniac.extra_features.face_detector import FaceDetector


class FaceDetectorTests(unittest.TestCase):

    ASSETS_DIR = "assets"
    face_detector = FaceDetector()

    def setUp(self):
        print("Initializing FaceDetector")
        self.face_detector.init()

    def test_is_face_positive(self):
        for file in os.listdir(self.ASSETS_DIR):
            filename = os.fsdecode(file)
            if filename.startswith("face"):
                is_face = self.face_detector.is_face_on_image_by_filename(os.path.join(self.ASSETS_DIR, file))
                assert is_face

    def test_is_face_negative(self):
        for file in os.listdir(self.ASSETS_DIR):
            filename = os.fsdecode(file)
            if filename.startswith("notface"):
                is_face = self.face_detector.is_face_on_image_by_filename(os.path.join(self.ASSETS_DIR, file))
                assert not is_face

    def test_gender_male(self):
        for file in os.listdir(self.ASSETS_DIR):
            filename = os.fsdecode(file)
            if filename.startswith("face_male"):
                gender = self.face_detector.get_gender_by_filename(os.path.join(self.ASSETS_DIR, file))
                assert gender == FaceDetector.Gender.MALE

    def test_gender_female(self):
        for file in os.listdir(self.ASSETS_DIR):
            filename = os.fsdecode(file)
            if filename.startswith("face_female"):
                gender = self.face_detector.get_gender_by_filename(os.path.join(self.ASSETS_DIR, file))
                assert gender == FaceDetector.Gender.FEMALE

    @staticmethod
    def _interpret_faces_array(faces) -> str:
        if len(faces) > 0:
            return "face"
        else:
            return "not face"
