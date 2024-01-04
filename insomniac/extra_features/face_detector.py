from enum import Enum, unique

from PIL import Image

import insomniac
from insomniac.utils import *


class FaceDetector:
    ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(insomniac.__file__)), "assets")
    GENDER_MODEL = os.path.join(ASSETS_PATH, 'gender_net.caffemodel')  # the gender model architecture
    GENDER_MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)  # mean substraction to eliminate the effect of illunination changes
    GENDER_PROTO = os.path.join(ASSETS_PATH, 'gender_deploy.prototxt')  # the gender model pre-trained weights
    MIN_CONFIDENCE_LEVEL = 0.70

    is_initialized = False
    face_cascade = None
    gender_net = None

    def init(self):
        try:
            import cv2
            import numpy
        except ImportError:
            raise ImportError("Please install OpenCV: python3 -m pip install opencv-python")

        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.gender_net = cv2.dnn.readNetFromCaffe(self.GENDER_PROTO, self.GENDER_MODEL)
        self.is_initialized = True

    def is_face_on_image(self, image: Image) -> bool:
        if not self.is_initialized:
            print(COLOR_FAIL + "Initialize FaceDetector before usage!" + COLOR_ENDC)
            return False
        import numpy
        open_cv_image = numpy.array(image)
        faces = self.face_cascade.detectMultiScale(open_cv_image, 1.1, 4)
        return len(faces) > 0

    def is_face_on_image_by_filename(self, filename: str) -> bool:
        is_face = self.is_face_on_image(Image.open(filename).convert('RGB'))
        print(f"{filename}: this {'contains' if is_face else 'does not contain'} face")
        return is_face

    def get_gender(self, image: Image) -> (Optional['Gender'], float):
        """
        Determines gender by face on the image.
        @return: gender and level of confidence (if lower than MIN_CONFIDENCE_LEVEL, gender will be None)
        """
        if not self.is_initialized:
            print(COLOR_FAIL + "Initialize FaceDetector before usage!" + COLOR_ENDC)
            return None, 0.5
        import numpy
        import cv2

        open_cv_image = numpy.array(image)
        faces = self.face_cascade.detectMultiScale(open_cv_image, 1.1, 4)
        if len(faces) == 0:
            return FaceDetector.Gender.NOT_HUMAN, 0.5

        original_width = open_cv_image.shape[1]
        original_height = open_cv_image.shape[0]
        padding = min(original_width, original_height) // 20
        x, y, w, h = faces[0]

        x1_cropped = max(x - padding, 0)
        y1_cropped = max(y - padding, 0)
        x2_cropped = min(x + w + padding, original_width)
        y2_cropped = min(y + h + padding, original_height)
        face_img = open_cv_image[y1_cropped: y2_cropped, x1_cropped: x2_cropped]

        blob = cv2.dnn.blobFromImage(face_img, 1.0, (227, 227), self.GENDER_MODEL_MEAN_VALUES, swapRB=False)
        self.gender_net.setInput(blob)
        gender_preds = self.gender_net.forward()
        is_male_confidence = gender_preds[0][0]
        is_female_confidence = 1 - is_male_confidence
        if is_male_confidence >= self.MIN_CONFIDENCE_LEVEL:
            return FaceDetector.Gender.MALE, is_male_confidence
        elif is_female_confidence >= self.MIN_CONFIDENCE_LEVEL:
            return FaceDetector.Gender.FEMALE, is_female_confidence
        else:
            return FaceDetector.Gender.ANY, max(is_male_confidence, is_female_confidence)

    def get_gender_by_filename(self, filename: str) -> Optional['Gender']:
        gender, confidence = self.get_gender(Image.open(filename).convert('RGB'))
        print(f"{filename}: {gender.value}, confidence: {confidence}")
        return gender

    @unique
    class Gender(Enum):
        MALE = "male"
        FEMALE = "female"
        ANY = "any"
        NOT_HUMAN = "not a human"
