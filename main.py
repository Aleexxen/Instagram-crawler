from igramscraper.instagram import Instagram
from pymongo import MongoClient
import requests
import os
import detect_face
import base64
from dotenv import load_dotenv, find_dotenv
import io
import re

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
    """
    :return: Download images and user info(tags) in database test_images
    """
    user_name_list = os.getenv('USER_NAMES').split()
    print(user_name_list)
    print(user_name_list[0])
    print(len(user_name_list))

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
            image = p.content
            # stream = io.BytesIO(image)
            # result = detect_face.check_faces(stream)
            # if not result == []:

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

            # DECODE IMAGE
            b_img = base64.b64encode(image)
            # stream.close()

            # Insert data in database
            try:
                users_collection.insert_one({'_id': user_name, 'tags_list': list_of_user_tags, 'q_grade': 0, 'images': [pic_url.split('.')[0]]})
            except Exception as e:
                print(e)
                users_collection.update_one({'_id': user_name}, {'$addToSet': {'tags_list': {'$each': list_of_user_tags}, 'images': pic_url.split('.')[0]}}, upsert=True)
            try:
                images_collection.insert_one(
                    {'_id': pic_url.split('.')[0], 'tag': list_of_user_tags, 'q_grade': 0, 'image': b_img})
            except Exception as e:
                print(e)
                continue
            print(pic_url)

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

def show_image_by_id(img_id_list):
    """
    :param img_id_list: string array of image ids
    :return: list of binary images
    """
    images_list = []
    for img_id in img_id_list:
        if images_collection.find_one({'_id': img_id}) == {}:
            print('NO IMAGE WITH ID = ' + img_id)
        else:
            image = images_collection.find_one({'_id': img_id})
            images_list.append(image['image'])
    return images_list

def show_image_by_tag(tags):
    """
    :param tags: string array or value of tags
    :return: download images in out_img_path
    """
    tag_list = tags.split()
    for tag in tag_list:
        for img in images_collection.find({'tag': { '$all' : [str(tag)] }}):
            out_img_path = 'out_imgs/tags/' + str(tag) + '/'
            if not os.path.exists(out_img_path):
                os.mkdir(out_img_path)
            with open(out_img_path + img['_id'] + '.jpg', "wb") as fimage:
                fimage.write(base64.b64decode(img['image']))
                fimage.close()

def show_image_by_user_name(names):
    """
    :param names: string array or value of names
    :return: download images in out_img_path
             download array of tags in out_text_path
    """
    names_list = names.split()
    for name in names_list:
        for user in users_collection.find({'_id': str(name)}):
            out_img_path = 'out_imgs/names/' + str(name) + '/'
            out_text_path = 'out_text/user_names/'

            if not os.path.exists(out_img_path):
                os.mkdir(out_img_path)

            if not os.path.exists(out_text_path):
                os.mkdir(out_img_path)

            with open(out_text_path + str(name) + '.txt', 'w') as ftxt:
                for el in user['tags_list']:
                    ftxt.write(el + ' ')
                ftxt.close()

            images_list = show_image_by_id(user['images'])
            i = 0
            for image in images_list:
                if i < len(images_list):
                    with open(out_img_path + user['images'][i] + '.jpg', "wb") as fimage:
                        fimage.write(base64.b64decode(image))
                        fimage.close()
                        i = i + 1

# Login to instagram
#log_in()

# Load data
# You don't have to run log_in() function for load_data_by_user_name()
#load_data_by_tag()
#load_data_by_user_name()

# Download images in out_img_path
# No instagram login required
#show_image_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))
#show_image_by_user_name(os.getenv('USER_NAMES_FOR_SEARCH'))

# Delete <collection_name> collection from db test_images
#db.<collection_name>.drop()

