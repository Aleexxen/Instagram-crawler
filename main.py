from igramscraper.instagram import Instagram
import csv
from pymongo import MongoClient
import requests
import configparser
import os
import detect_face
import zlib
from bson import binary
from PIL import Image
import matplotlib.pyplot as plt
import gzip
import shutil
import base64
from dotenv import load_dotenv, find_dotenv
import io
import re

#load path to all safe variables
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

def contains(string):
    return not re.search(r'[^a-zA-Z0-9а-яА-Я_ ]', string)

instagram = Instagram()

def log_in():
    # account = instagram.get_account_by_id(3015034946)
    # print(account)

    proxies = {
        'http': 'http://50.206.25.107:80',
        # 'http':'http://109.172.57.64:8081',
        # 'http': 'http://46.229.214.206:3128',
    }

    instagram.set_proxies(proxies)

    instagram.with_credentials(os.getenv('IG_LOGIN'), os.getenv('IG_PASSWORD'), 'sessions/')
    try:
        instagram.login()
    except Exception as e:
        print(e)

# Download images in database
def load_data_by_tag():

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
            # print(pic_url)
            # out_path = data_path + '/' + str(pic_url)
            # out = open(out_path, "wb")
            # out.write(p.content)
            # out.close()

            # Face detection
            image = p.content
            stream = io.BytesIO(image)
            result = detect_face.check_faces(stream)
            if not result == []:
                # DECODE IMAGE
                b_img = base64.b64encode(image)
                stream.close()

                # Extract out_text
                list_of_image_tags = []
                caption = media.caption
                arr = caption.split('#')
                print(arr)
                j = 1
                while j < len(arr):
                    el = arr[j].replace(' ', '')
                    if contains(el):
                        list_of_image_tags.append(el)
                    j = j + 1
                print(list_of_image_tags)

                # Insert data in database
                try:
                    images_collection.insert_one({'_id': pic_url.split('.')[0], 'tag': list_of_image_tags, 'q_grade': 0, 'image': b_img})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)

        #fcsv.close()
        print('close file ' + hashtag)
        i = i + 1

def load_data_by_user_name():
    user_name_list = os.getenv('USER_NAMES').split()
    print(user_name_list)
    print(user_name_list[0])
    print(len(user_name_list))

    i = 0
    while i < len(user_name_list):
        # Creating a user_id
        user_name = str(user_name_list[i])
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
            image = p.content
            # stream = io.BytesIO(image)
            # result = detect_face.check_faces(stream)
            # if not result == []:

            # Extract out_text
            caption = media.caption
            arr = caption.split('#')
            print(arr)
            j = 1
            while j < len(arr):
                list_of_user_tags.append(arr[j])
                j = j + 1
            print(list_of_user_tags)

            # DECODE IMAGE
            b_img = base64.b64encode(image)
            # stream.close()

            # Insert data in database
            try:
                users_collection.update_one({'_id': user_name, 'tags_list': list_of_user_tags, 'q_grade': 0},
                                        {'$addToSet': { 'images': str(pic_url.split('.')[0])} } )
            except Exception as e:
                print(e)
                continue
            print(pic_url)

        # fcsv.close()
        print('close file ' + user_name)
        i = i + 1

def find_max_size_from_all():
    all_max_size = 0
    for address, dirs, files in os.walk('files_with_data'):
        for file in files:
            if os.stat(address + '/' + file).st_size > all_max_size:
                all_max_size = os.stat(address + '/' + file).st_size

    return all_max_size

def find_max_size_in_each_hashtag():
    for address, dirs, files in os.walk('files_with_data'):
        for dir in dirs:
            if not os.path.exists('sizes/' + dir):
                os.mkdir('sizes/' + dir)
            for address1, dirs1, files1 in os.walk('files_with_data/' + dir):
                max_size = 0
                for file in files1:
                    if os.stat('files_with_data/' + dir + '/' + str(file)).st_size > max_size:
                        max_size = os.stat('files_with_data/' + dir + '/' + str(file)).st_size
            size_file = open('sizes/' + dir + '/size_file.txt', 'w')
            size_file.write(str(max_size))
            size_file.close()

def show_image_by_tag(tags):
    tag_list = tags.split()
    for tag in tag_list:
        for img in images_collection.find({'tag': { '$all' : [str(tag)] }}):
            out_img_path = 'out_imgs/tags/' + str(tag) + '/'
            if not os.path.exists(out_img_path):
                os.mkdir(out_img_path)
            with open(out_img_path + img['_id'] + '.jpg', "wb") as fimage:
                fimage.write(base64.b64decode(img['image']))
                fimage.close()

def show_image_by_user_name(name):
    for img in users_collection.find({'_id': str(name)}):
        out_img_path = 'out_imgs/names/' + str(name) + '/'
        out_text_path = 'out_text/user_names/'
        if not os.path.exists(out_img_path):
            os.mkdir(out_img_path)
        if not os.path.exists(out_text_path):
            os.mkdir(out_img_path)
        with open(out_text_path + str(name) + '.txt', 'a') as ftxt:
            for el in img['tags_list']:
                ftxt.write(el)
            ftxt.write(' ')
            ftxt.close()
        for image in img['images']:
            with open(out_img_path + image + '.jpg', "wb") as fimage:
                fimage.write(base64.b64decode(image))
                fimage.close()

log_in()
st = 'beninmua beninmuas makeupartistinbenin okuku beads beninokuku'

# Load data
#load_data_by_tag()
#load_data_by_user_name()

# Download images in out_img_path
show_image_by_tag(st)
#show_image_by_user_name('helenesjostedt')

# db.images.drop()
