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

    # config = configparser.ConfigParser()
    # config.read("settings.ini")
    # hash_list = config.get("FilesConf", "hashtags").split()

    instagram.with_credentials(os.getenv('IG_CLIENT_ID'), os.getenv('IG_CLIENT_SECRET'))
    try:
        # instagram.is_logged_in('./sessions')
        instagram.login()
    except Exception as e:
        print(e)
        # cookie = "sessions/diplom-test.txt"
        # instagram.set_cookies(cookie)

# Download images in database
def load_data():

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
            image = p.content
            stream = io.BytesIO(image)
            result = detect_face.check_faces(stream)
            if not result == []:
                # os.remove(out_path)
                b_img = base64.b64encode(image)
                stream.close()

                # Insert data in database
                try:
                    db.images.insert_one({'_id': pic_url.split('.')[0], 'tag': hashtag, 'q_grade': 0, 'image': b_img})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)

        #fcsv.close()
        print('close file ' + hashtag)
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

def show_image(tag):
    for img in db.images.find({'tag': str(tag)}):
        out_img_path = 'out_imgs/' + str(tag) + '/'
        if not os.path.exists(out_img_path):
            os.mkdir(out_img_path)
        with open(out_img_path + img['_id'] + '.jpg', "wb") as fimage:
            fimage.write(base64.b64decode(img['image']))
            fimage.close()

log_in()
load_data()

# Download images in out_img_path
#show_image('artmakeup')