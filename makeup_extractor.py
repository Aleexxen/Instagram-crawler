import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from PIL import Image
# from matplotlib import cm
# from imageio import imread
# from skimage.transform import resize
# from matplotlib.colors import to_hex, to_rgba
# from google.colab.patches import cv2_imshow
import cv2
import extcolors
import dlib

import copy

from os import listdir
from os.path import isfile, join

import wget

# Download face landmarks predictor
#mmod_human_face_detector = wget.download("https://github.com/justadudewhohacks/face-recognition.js-models/raw/master/models/mmod_human_face_detector.dat")
#shape_predictor_68_face_landmarks = wget.download("https://github.com/italojs/facial-landmarks-recognition/raw/master/shape_predictor_68_face_landmarks.dat")
#shape_predictor_68_face_landmarks = wget.download('http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2')

# Direction to image files
# dir_path = r'/content/drive/MyDrive/csc_makeup/unzip_images/images/#v93oo'
# file_name = '0a0f3092-ae26-42de-98fc-0c9cc1774221.jpg'
# f = join(dir_path, file_name)

# Makeup extractor
# детектор лица и ключевых точек из dlib: обычный или cnn

class ExtractMakeup:
    def __init__(self, use_cnn_face_detector=False):
        # define landmarks numbers for different regions
        self.left_eyelid = [0] + list(range(17, 22)) + [27, 28]
        self.right_eyelid = [28, 27] + list(range(22, 27)) + [16]
        self.eyelids = [self.left_eyelid, self.right_eyelid]

        self.left_eye = list(range(36, 42))
        self.right_eye = list(range(42, 48))
        self.eyes = [self.left_eye, self.right_eye]

        self.mouth = list(range(48, 60))
        self.teeth = list(range(60, 68))

        self.use_cnn = use_cnn_face_detector
        if self.use_cnn:
            self.detector_weights_path = 'mmod_human_face_detector.dat'
            self.face_detector = dlib.cnn_face_detection_model_v1(self.detector_weights_path)
        else:
            self.face_detector = dlib.get_frontal_face_detector()
        self.predictor_weights_path = 'shape_predictor_68_face_landmarks.dat'
        self.landmarks_predictor = dlib.shape_predictor(self.predictor_weights_path)

    def detect_face(self, img):
        self.img = img

        # face detection
        faces = self.face_detector(self.img)
        if not faces:
            return False
        else:
            return True

    def get_landmarks(self, regions):
        points = []
        for region in regions:
            landmarks = self.landmarks_predictor(image=self.gray_img, box=self.face)
            cur_points = []

            for n in region:
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cur_points.append(np.array([x, y]))

            points.append(np.array(cur_points))

        return points

    def get_mask(self, points):
        mask = np.zeros(self.img.shape[:2], dtype=np.uint8)
        mask = cv2.fillPoly(mask, points, 255)
        return mask

    def add_transparent_background(self, img, mask):
        res = img.copy()
        res = cv2.cvtColor(res, cv2.COLOR_BGR2BGRA)
        res[:, :, 3] = mask[:, :, 0]
        return res

    def extract(self, img):
        self.img = img
        self.mask = np.zeros(self.img.shape[:2], dtype=np.uint8)

        # face boundary box
        self.gray_img = cv2.cvtColor(src=img, code=cv2.COLOR_BGR2GRAY)
        faces = self.face_detector(self.img)
        if not faces:
            return None
        if self.use_cnn:
            self.face = faces[0].rect
        else:
            self.face = faces[0]

        # eyelids + eyes region mask
        eyelids_landmarks = self.get_landmarks(self.eyelids)
        eyelids_mask = self.get_mask(eyelids_landmarks)

        # eyes region mask
        eyes_landmarks = self.get_landmarks(self.eyes)
        eyes_mask = self.get_mask(eyes_landmarks)

        # only eyelids mask
        eyelids_mask = cv2.bitwise_and(eyelids_mask, (255 - eyes_mask))

        # mouth region mask (lips + teeth)
        mouth_landmarks = self.get_landmarks([self.mouth])
        mouth_mask = self.get_mask(mouth_landmarks)

        # teeth region mask
        teeth_landmarks = self.get_landmarks([self.teeth])
        teeth_mask = self.get_mask(teeth_landmarks)

        # lips (exclude teeth region)
        lips_mask = cv2.bitwise_and(mouth_mask, (255 - teeth_mask))

        # full mask
        self.mask = cv2.bitwise_or(eyelids_mask, lips_mask)
        self.mask = np.array([self.mask] * 3)
        self.mask = np.transpose(self.mask, [1, 2, 0])

        # get regions from input image
        self.img_mask = cv2.bitwise_and(self.img, self.mask)

        self.top = np.min([y for eye in eyelids_landmarks for x, y in eye])
        self.bottom = np.max([y for m in mouth_landmarks for x, y in m])
        self.left = np.min([x for eye in eyelids_landmarks for x, y in eye])
        self.right = np.max([x for eye in eyelids_landmarks for x, y in eye])

        self.img_crop = self.img_mask[self.top:self.bottom, self.left:self.right]
        self.mask_crop = self.mask[self.top:self.bottom, self.left:self.right]

        self.transparent_img = self.add_transparent_background(self.img_crop, self.mask_crop)
        return self.transparent_img

    def plot_face_box(self):
        x = self.face.left()
        y = self.face.top()
        w = self.face.right() - x
        h = self.face.bottom() - y
        img = self.img.copy()
        plt.imshow(cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2))


# Color palette extractor
class ExtractColors:
    def __init__(self):
        pass

    def extract(self, img):
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img, 'RGBA')

        self.colors, pixel_count = extcolors.extract_from_image(img)

        return self.colors


# Color palette visualization
def create_color_palette(palette, proportionately=False, height=300, width=50):
    total_pixels = sum([pixels_count for color, pixels_count in palette])

    bar = np.zeros((height, width, 3), dtype="uint8")
    start_y = 0

    if not proportionately:
        percent = 1 / len(palette)

    for color, pixels_count in palette:
        if proportionately:
            percent = pixels_count / total_pixels
        end_y = start_y + (percent * height)
        top_left_corner = (0, int(start_y))
        bottom_right_corner = (width, int(end_y))
        cv2.rectangle(bar, top_left_corner, bottom_right_corner,
                      np.array(color).astype("uint8").tolist(), -1)
        start_y = end_y

    return bar


# Plot original image, extracted makeup and color palette
def plot_results(img, makeup_extractor, colors_extractor):
    makeup = makeup_extractor.extract(img)
    colors = colors_extractor.extract(makeup)
    palette = create_color_palette(colors)

    f = plt.figure(figsize=(10, 5))

    plt.subplot(131, autoscale_on=True)
    plt.imshow(img)
    plt.axis('off')

    plt.subplot(132, autoscale_on=True)
    plt.imshow(makeup)
    plt.axis('off')

    plt.subplot(133, autoscaley_on=True)
    plt.imshow(palette)
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    plt.show()


# Experiments