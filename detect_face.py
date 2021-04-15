import face_recognition
import os
from PIL import Image


def check_faces(my_img):

    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(my_img)

    return face_recognition.face_locations(image)


def cut_faces(my_img):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(my_img)

    face_locations = face_recognition.face_locations(image)

    # Cut faces from images
    for face_location in face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.show()

# print(check_faces('files_with_data/makeup/173679692_950381945500176_1300135386879308633_n.jpg'))
# cut_faces('files_with_data/makeup/173679692_950381945500176_1300135386879308633_n.jpg')