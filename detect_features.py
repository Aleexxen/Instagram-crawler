import face_recognition
import os
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import pandas as pd

# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)

full_face_arr = ['left_eye', 'right_eye', 'top_lip', 'bottom_lip']
eyes_arr = ['left_eye', 'right_eye']
lips_arr = ['top_lip', 'bottom_lip']
left_eye_arr = ['left_eye']
right_eye_arr = ['right_eye']


def compare(list1, list2):
    for item in list1:
        if item in list2:  # checking the item is present in list2
            continue  # if yes, goes for next item in list1 to check
        else:
            return False  # if no, immediately comes out with "False"
    else:
        return True  # reaches here, only if all the items in list1 is
        # present in list2 , returning "True"


def replace_file(new_catalog):
    if not os.path.exists(address + '/' + str(new_catalog)):
        os.mkdir(address + '/' + str(new_catalog))
    os.replace(address + '/' + file, address + '/' + str(new_catalog) + '/' + file)


# data = {'File': [],
#         'IfFace': []}
# frame = pd.DataFrame(data)

for address, dirs, files in os.walk('files_with_data/artmakeup'):
    # i = 0
    for file in files:
        image = face_recognition.load_image_file(address + '/' + file)

        # Find all facial features in all the faces in the image
        face_landmarks_list = face_recognition.face_landmarks(image)

        # Create a PIL imagedraw object so we can draw on the picture
        # pil_image = Image.fromarray(image)
        # d = ImageDraw.Draw(pil_image)

        for face_landmarks in face_landmarks_list:

            # Print the location of each facial feature in this image
            # for facial_feature in face_landmarks.keys():
            #     print("The {} in this face has the following points: {}".format(facial_feature,
            #                                                                     face_landmarks[facial_feature]))

            # Let's trace out each facial feature in the image with a line!
            # for facial_feature in face_landmarks.keys():
            #     d.line(face_landmarks[facial_feature], width=5)

            # Sort picture to it's place file
            if face_landmarks_list == []:
                replace_file('no_face')
            elif compare(full_face_arr, face_landmarks.keys()):
                replace_file('full_face')
            elif compare(eyes_arr, face_landmarks.keys()):
                replace_file('eyes')
            elif compare(lips_arr, face_landmarks.keys()):
                replace_file('lips')
            elif compare(left_eye_arr, face_landmarks.keys()):
                replace_file('left_eye')
            elif compare(right_eye_arr, face_landmarks.keys()):
                replace_file('right_eye')

        # Show the picture
        # pil_image.show()

        # face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")
        # # frame.loc[i,'File'] = address + '/' + file + ':'
        # # frame.loc[i,'IfFace'] = str(face_locations)
        # # i = i + 1
        # for face_location in face_locations:
        #     # Print the location of each face in this image
        #     top, right, bottom, left = face_location
        #     # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
        #
        #     # You can access the actual face itself like this:
        #     face_image = image[top:bottom, left:right]
        #     pil_image = Image.fromarray(face_image)
        #     pil_image.show()

# print(frame)

# image = face_recognition.load_image_file("files_with_data/artmakeup/166344047_476766790126387_7999381271883334155_n.jpg")
# face_locations = face_recognition.face_locations(image)
# print(face_locations)


# image = face_recognition.load_image_file("files_with_data/artmakeup/166561254_4002638516424808_247471634899416099_n.jpg")
# face_landmarks_list = face_recognition.face_landmarks(image)
# print(face_landmarks_list)
