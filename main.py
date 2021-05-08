import cv2
from igramscraper.instagram import Instagram
from pymongo import MongoClient
import requests
import os
import base64
from dotenv import load_dotenv, find_dotenv
import io
import re
import makeup_extractor
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import urllib.request

# Load path to all safe variables
load_dotenv(find_dotenv('.env'))

# Create the client
# client = MongoClient('localhost', 27017)
client = MongoClient(os.getenv('MONGO_URL'))

# Connect to our database
# db = client['test_images']
db = client['test_images']

# Fetch our images collection
images_collection = db['images']
users_collection = db['users']

# Check if string contains something, but not like this trash "" or " or .
def contains(string):
    """
    :param string: string value
    :return: True or False
    """
    return not re.search(r'[^a-zA-Z0-9а-яА-Я_ ]', string)

instagram = Instagram()

# Instagram login
def log_in():
    """
    :return: write headers and credits for login
    """
    # account = instagram.get_account_by_id(3015034946)
    # print(account)

    # Proxies to use
    proxies = {
        'http': 'http://50.206.25.107:80',
        # 'http':'http://109.172.57.64:8081',
        # 'http': 'http://46.229.214.206:3128',
    }

    instagram.set_proxies(proxies)

    instagram.with_credentials(os.getenv('IG_LOGIN'), os.getenv('IG_PASSWORD'), 'sessions/')
    """
    :third param : path to your sessions folder, which contains cookies
    :return: login with these credentials
    """
    try:
        instagram.login()
    except Exception as e:
        print(e)

# Download images in database
def load_data_by_tag():
    """
    :return: Download images in database test_images
    """

    # cookie = "sessions/diplom-test.txt"
    # instagram.set_cookies(cookie)

    hash_list = os.getenv('HASHTAGS').split()
    print(hash_list)
    print(hash_list[0])
    print(len(hash_list))

    i=0
    while i < len(hash_list):
        #Creating a hashtag
        hashtag = str(hash_list[i])
        medias = instagram.get_medias_by_tag(hashtag, count=int(os.getenv('HASH_COUNT')))

        # Get medias
        for media in medias:
            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]

            # Face detection
            url = p.url
            webUrl = urllib.request.urlopen(url)
            image = Image.open(webUrl)
            content = p.content

            extr_makeup = makeup_extractor.ExtractMakeup(False)
            color_palette_extractor = makeup_extractor.ExtractColors()

            img = np.array(image)
            if extr_makeup.detect_face(img):
                # Extract makeup and palette

                try:
                    makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                except Exception as e:
                    print(e)
                    continue

                m_retval, m_buffer = cv2.imencode('.png', makeup)
                p_retval, p_buffer = cv2.imencode('.png', palette)

                makeup_as_txt = base64.b64encode(m_buffer)
                palette_as_txt = base64.b64encode(p_buffer)

                # ENCODE IMAGE
                b_img = base64.b64encode(content)

                # Extract out_text
                list_of_image_tags = []
                caption = media.caption
                arr = caption.split('#')
                j = 1
                while j < len(arr):
                    el = arr[j].replace(' ', '')
                    if contains(el):
                        list_of_image_tags.append(el)
                    j = j + 1
                print(list_of_image_tags)

                # Insert data in database
                try:
                    images_collection.insert_one({'_id': pic_url.split('.')[0], 'tag': list_of_image_tags, 'q_grade': 0, 'image': b_img, 'makeup': makeup_as_txt, 'palette': palette_as_txt})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)

        print('close file ' + hashtag)
        i = i + 1

def load_data_by_user_name():
    """
    :return: Download images and user info(tags) in database test_images
    """
    user_name_list = os.getenv('USER_NAMES').split()
    print(user_name_list)
    print(user_name_list[0])
    print(len(user_name_list))

    extr_makeup = makeup_extractor.ExtractMakeup(False)
    color_palette_extractor = makeup_extractor.ExtractColors()

    i = 0
    while i < len(user_name_list):
        # Creating a user_id
        user_name = str(user_name_list[i])
        log_in()
        try:
            medias = instagram.get_medias(user_name, int(os.getenv('MEDIA_COUNT')))
        except Exception as infe:
            print(infe)
            i = i + 1
            continue

        list_of_user_tags = []

        # Get medias
        for media in medias:
            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]

            # Check if image has face
            url = p.url
            webUrl = urllib.request.urlopen(url)
            image = Image.open(webUrl)
            content = p.content
            img = np.array(image)

            if extr_makeup.detect_face(img):

                # ENCODE IMAGE
                b_img = base64.b64encode(content)

                # Extract makeup and palette
                try:
                    makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                except Exception as e:
                    print(e)
                    continue

                m_retval, m_buffer = cv2.imencode('.png', makeup)
                p_retval, p_buffer = cv2.imencode('.png', palette)

                makeup_as_txt = base64.b64encode(m_buffer)
                palette_as_txt = base64.b64encode(p_buffer)

                # Extract out_text
                caption = media.caption
                arr = caption.split('#')
                j = 1
                while j < len(arr):
                    el = arr[j].replace(' ', '')
                    if contains(el):
                        list_of_user_tags.append(el)
                    j = j + 1
                print(list_of_user_tags)

                # Insert data in database
                try:
                    users_collection.insert_one({'_id': user_name, 'tags_list': list_of_user_tags, 'q_grade': 0, 'images': [pic_url.split('.')[0]]})
                except Exception as e:
                    print(e)
                    users_collection.update_one({'_id': user_name}, {'$addToSet': {'tags_list': {'$each': list_of_user_tags}, 'images': pic_url.split('.')[0]}}, upsert=True)
                try:
                    images_collection.insert_one(
                        {'_id': pic_url.split('.')[0], 'tag': list_of_user_tags, 'q_grade': 0, 'image': b_img, 'makeup': makeup_as_txt, 'palette': palette_as_txt})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)

        print('close file ' + user_name)
        i = i + 1

def show_image_by_id(img_id_list):
    """
    :param img_id_list: string array of image ids
    :return: list of binary images
    """
    images_list = []
    makeup_list = []
    palette_list = []
    for img_id in img_id_list:
        if images_collection.find_one({'_id': img_id}) == {}:
            print('NO IMAGE WITH ID = ' + img_id)
        else:
            image = images_collection.find_one({'_id': img_id})
            images_list.append(image['image'])
            palette_list.append(image['palette'])
            makeup_list.append(image['makeup'])
    return images_list, makeup_list, palette_list

def show_image_by_tag(tags):
    """
    :param tags: string array or value of tags
    :return: download images in out_img_path
    """
    tag_list = tags.split()
    for tag in tag_list:
        for img in images_collection.find({'tag': { '$all' : [str(tag)] }}):
            tags_path = 'out_imgs/tags/' + str(tag) + '/'
            out_img_path = 'out_imgs/tags/' + str(tag) + '/' + img['_id'] + '/'
            if not os.path.exists(tags_path):
                os.mkdir(tags_path)
            if not os.path.exists(out_img_path):
                os.mkdir(out_img_path)
            with open(out_img_path + img['_id'] + '.jpg', "wb") as fimage:
                decoded_image = base64.b64decode(img['image'])
                fimage.write(decoded_image)
                fimage.close()

            # Extract makeup and palette
            makeup_nparr = np.frombuffer(base64.b64decode(img['makeup']), np.uint8)
            palette_nparr = np.frombuffer(base64.b64decode(img['palette']), np.uint8)

            makeup_img = cv2.imdecode(makeup_nparr, cv2.IMREAD_UNCHANGED)
            palette_img = cv2.imdecode(palette_nparr, cv2.IMREAD_UNCHANGED)

            makeup = Image.fromarray(makeup_img)
            palette = Image.fromarray(palette_img)

            makeup.save(out_img_path + 'makeup.png')
            palette.save(out_img_path + 'palette.png')


def show_image_by_user_name(names):
    """
    :param names: string array or value of names
    :return: download images in out_img_path
             download array of tags in out_text_path
    """
    names_list = names.split()
    for name in names_list:
        for user in users_collection.find({'_id': str(name)}):
            names_path = 'out_imgs/names/' + str(name) + '/'
            if not os.path.exists(names_path):
                os.mkdir(names_path)

            out_text_path = 'out_text/user_names/'
            if not os.path.exists(out_text_path):
                os.mkdir(out_text_path)

            for el in user['images']:
                out_img_path = names_path + el + '/'
                if not os.path.exists(out_img_path):
                    os.mkdir(out_img_path)

            images_list, makeups_list, palettes_list = show_image_by_id(user['images'])

            i = 0
            while i < len(images_list):
                with open(names_path + user['images'][i] + '/' + user['images'][i] + '.jpg', "wb") as fimage:
                    fimage.write(base64.b64decode(images_list[i]))
                    fimage.close()

                    # Extract makeup and palette
                    makeup_nparr = np.frombuffer(base64.b64decode(makeups_list[i]), np.uint8)
                    palette_nparr = np.frombuffer(base64.b64decode(palettes_list[i]), np.uint8)

                    makeup_img = cv2.imdecode(makeup_nparr, cv2.IMREAD_UNCHANGED)
                    palette_img = cv2.imdecode(palette_nparr, cv2.IMREAD_UNCHANGED)

                    makeup = Image.fromarray(makeup_img)
                    palette = Image.fromarray(palette_img)

                    makeup.save(names_path + user['images'][i] + '/' + 'makeup.png')
                    palette.save(names_path + user['images'][i] + '/' + 'palette.png')

                i = i + 1

            with open(out_text_path + str(name) + '.txt', 'w') as ftxt:
                for el in user['tags_list']:
                    ftxt.write(el + ' ')
                ftxt.close()


def extract_makeup_by_tag(tag_list):
    extr_makeup = makeup_extractor.ExtractMakeup(False)
    color_palette_extractor = makeup_extractor.ExtractColors()
    imagePath_to_extract = 'out_imgs/tags/'

    for address, dirs, files in os.walk(imagePath_to_extract):
        tags = tag_list.split()
        folders = list(set(tags) & set(dirs))
        for folder in folders:
            dist_path = imagePath_to_extract + folder + '/'
            for fol_address, fol_dirs, fol_files in os.walk(dist_path):
                for fol_file in fol_files:
                    if re.search(r'_n', fol_file):
                        img = plt.imread(fol_address + '/' + fol_file, 'jpg')
                        makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                        makeup_img = Image.fromarray(makeup)
                        palette_img = Image.fromarray(palette)
                        makeup_img.save(fol_address + '/' + 'makeup.png')
                        palette_img.save(fol_address + '/' + 'palette.png')

def extract_makeup_by_user(users_list):
    extr_makeup = makeup_extractor.ExtractMakeup(False)
    color_palette_extractor = makeup_extractor.ExtractColors()
    imagePath_to_extract = 'out_imgs/names/'

    for address, dirs, files in os.walk(imagePath_to_extract):
        users = users_list.split()
        folders = list(set(users) & set(dirs))
        for folder in folders:
            dist_path = imagePath_to_extract + folder + '/'
            for fol_address, fol_dirs, fol_files in os.walk(dist_path):
                for fol_file in fol_files:
                    if re.search(r'_n', fol_file):
                        img = plt.imread(fol_address + '/' + fol_file, 'jpg')
                        makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                        makeup_img = Image.fromarray(makeup)
                        palette_img = Image.fromarray(palette)
                        makeup_img.save(fol_address + '/' + 'makeup.png')
                        palette_img.save(fol_address + '/' + 'palette.png')

# Login to instagram
#log_in()

# Load data
# You don't have to run log_in() function for load_data_by_user_name(), because it included there
#load_data_by_tag()
#load_data_by_user_name()

# Download images in out_img_path
# No instagram login required
#show_image_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))
#show_image_by_user_name(os.getenv('USER_NAMES_FOR_SEARCH'))

# Extract makeup from downloaded images
#extract_makeup_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))
#extract_makeup_by_user(os.getenv('USER_NAMES_FOR_SEARCH'))

# Delete <collection_name> collection from db test_images
#db.<collection_name>.drop()





# Experiments

# def find_max_size_from_all():
#     all_max_size = 0
#     for address, dirs, files in os.walk('files_with_data'):
#         for file in files:
#             if os.stat(address + '/' + file).st_size > all_max_size:
#                 all_max_size = os.stat(address + '/' + file).st_size
#
#     return all_max_size
#
# def find_max_size_in_each_hashtag():
#     for address, dirs, files in os.walk('files_with_data'):
#         for dir in dirs:
#             if not os.path.exists('sizes/' + dir):
#                 os.mkdir('sizes/' + dir)
#             for address1, dirs1, files1 in os.walk('files_with_data/' + dir):
#                 max_size = 0
#                 for file in files1:
#                     if os.stat('files_with_data/' + dir + '/' + str(file)).st_size > max_size:
#                         max_size = os.stat('files_with_data/' + dir + '/' + str(file)).st_size
#             size_file = open('sizes/' + dir + '/size_file.txt', 'w')
#             size_file.write(str(max_size))
#             size_file.close()


            # if os.path.exists(imagePath_to_extract + tag):
            #     img = plt.imread(address + '/' + tag + '/' + file, 'jpg')
            #     makeup, palette = makeup_extractor.get_results_as_base64(img, extr_makeup, color_palette_extractor)
            #     makeup_img = Image.fromarray(makeup)
            #     palette_img = Image.fromarray(palette)
            #     makeup_img.save(address + '/' + tag + '/' + 'makeup.jpg')
            #     palette_img.save(address + '/' + tag + '/' + 'palette.jpg')

# extr_makeup = makeup_extractor.ExtractMakeup(False)
# color_palette_extractor = makeup_extractor.ExtractColors()
# for address, dirs, files in os.walk('out_imgs/tags/makeupaddict/'):
#     for file in files:
        #image = Image.open(address + '/' + file)
        #img = np.array(image)
        # img = plt.imread(address + '/' + file, 'jpg')
        # # print(extr_makeup.detect_face(img))
        # # print(extr_makeup.extract(img))
        # makeup, palette = makeup_extractor.get_results_as_base64(img, extr_makeup, color_palette_extractor)
        # # extr_makeup.plot_face_box()
        #
        # retval, buffer = cv2.imencode('.png', makeup)
        # png_as_txt = base64.b64encode(buffer)
        # nparr = np.frombuffer(base64.b64decode(png_as_txt), np.uint8)
        # img2 = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        #
        # im = Image.fromarray(img2)
        # im.save(address + '/' + 'makeup.png')

        #base64_makeup = base64.b64encode(makeup)
        #base64_palette = base64.b64encode(palette)

        #image_data = re.sub('^data:image/.+;base64,', '', str(base64_makeup))
        #b_image_data = bytes(image_data).decode('base64')

        #encoded_image = str(base64_makeup).split(",")[1]
        #decoded_image = base64.b64decode(encoded_image)
        #bytes_image = io.BytesIO(decoded_image)
        #image = Image.open(bytes_image).convert('RGB')

        #print()
        #print(base64_makeup)
        #print(base64_palette)
        #img = np.frombuffer(base64.b64decode(base64_makeup), dtype=np.uint8)
        #image_string = io.BytesIO(base64.b64decode(base64_makeup))
        #image_string.seek(0)

        #image = Image.open(b_image_data)
        #img = np.array(image)
        #print('_____________________________________________________________')
        #print(img2)
        # with open(address + '/' + 'makeup.png', "wb") as fmakeup:
        #     fmakeup.write(base64.b64decode(base64_makeup))
        #     fmakeup.close()
        # with open(address + '/' + 'palette.png', "wb") as fpalette:
        #     fpalette.write(base64.b64decode(base64_palette))
        #     fpalette.close()
        #print(np.array_equal(makeup, img2))


#183089633_562793591356472_5912704159024989417_n
