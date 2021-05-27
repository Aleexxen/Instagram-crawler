import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import bson.json_util

import winsound
import easygui

import cv2
from igramscraper.instagram import Instagram
from pymongo import MongoClient
import requests
import os
import base64
from dotenv import load_dotenv, find_dotenv
import re
import makeup_extractor
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import urllib.request
import time
from igramscraper.instagram import endpoints
from igramscraper.exception.instagram_exception import InstagramException
from igramscraper.model.media import Media
from threading import *

# Load path to all safe variables
load_dotenv(find_dotenv('.env'))

# Sound signal at the end of work
def add_signal():
    if sys.platform == 'win32':
        duration = 1000 # millisecond
        freq = 440 # Hz
        winsound.Beep(freq, duration)
    elif sys.platform == 'darwin':
        os.system('say "your program has finished"')
    elif sys.platform == 'linux':
        os.system('spd-say "your program has finished"')

def connecting_to_mongo_server():
    # Create the client
    # client = MongoClient('localhost', 27017)
    client = MongoClient(os.getenv('MONGO_URL'))

    # Connect to our database
    # db = client['test_images']
    db = client[os.getenv('YOUR_DATABASE_NAME')]

    # Fetch our images collection
    images_collection = db['images']
    users_collection = db['users']
    tags_collection = db['tags']
    tag_search_collection = db['good_tags']

    return images_collection, users_collection, tags_collection

def runThreads(function, args):
    start = time.perf_counter()
    threads = []
    function1 = function
    hash_list = args

    playOn = True

    # with ThreadPoolExecutor(len(hash_list)) as executor:
    #     for i in executor.map(load_data_locally.load_data_by_tag_without_database, hash_list):
    #         print(i)
    while (playOn):
        i = 0
        while i < len(hash_list):
            # Creating a hashtag
            hashtag = str(hash_list[i])
            t = Thread(target=function1, args=(hashtag,))
            t.start()
            threads.append(t)
            i += 1
            time.sleep(5)

        for thread in threads:
            thread.join()

        finish = time.perf_counter()
        print('____________________________________________________________')
        print('end of work')
        print(start)
        print(finish)
        print(finish - start)
        add_signal()

        user_answer = easygui.buttonbox("Restart program?", choices=["Yes", "No"])
        if user_answer == "Yes": playOn = True

        else:
            playOn = False
            easygui.msgbox("Bye for now!")

# Creating folders
out_imgs_folder = 'out_imgs/'
out_text_folder = 'out_text/'
out_imgs_folder_for_names = out_imgs_folder + 'names/'
out_imgs_folder_for_tags = out_imgs_folder + 'tags/'
out_text_folder_for_names = out_text_folder + 'user_names/'
out_text_folder_for_images = out_text_folder + 'image_names/'
out_all_images_folder = 'all_images/'
out_all_makeups_folder = 'all_makeups/'
out_all_palettes_folder = 'all_palettes/'

if not os.path.exists(out_imgs_folder):
    os.mkdir(out_imgs_folder)
if not os.path.exists(out_text_folder):
    os.mkdir(out_text_folder)
if not os.path.exists(out_imgs_folder_for_names):
    os.mkdir(out_imgs_folder_for_names)
if not os.path.exists(out_imgs_folder_for_tags):
    os.mkdir(out_imgs_folder_for_tags)
if not os.path.exists(out_text_folder_for_names):
    os.mkdir(out_text_folder_for_names)
if not os.path.exists(out_text_folder_for_images):
    os.mkdir(out_text_folder_for_images)
if not os.path.exists(out_all_images_folder):
    os.mkdir(out_all_images_folder)
if not os.path.exists(out_all_makeups_folder):
    os.mkdir(out_all_makeups_folder)
if not os.path.exists(out_all_palettes_folder):
    os.mkdir(out_all_palettes_folder)

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
    # proxies = {
    #     'http': 'http://50.206.25.107:80',
    #     # 'http':'http://109.172.57.64:8081',
    #     # 'http': 'http://46.229.214.206:3128',
    # }

    # instagram.set_proxies(proxies)

    # Log in
    instagram.with_credentials(os.getenv('IG_LOGIN'), os.getenv('IG_PASSWORD'), 'sessions/')
    """
    :third param : path to your sessions folder, which contains cookies
    :return: login with these credentials
    """
    try:
        instagram.login()
    except Exception as e:
        print(e)

#NOT READY NOW
class MyInstagram(Instagram):
    def get_medias_by_tag_new(self, tag, start_date, end_date, count=12, max_id='', min_timestamp=None):
        """
        :param tag: tag string
        :param count: the number of how many media you want to get
        :param max_id: used to paginate
        :param min_timestamp: limit the time you want to start from
        :param start_date: the start time of the existing interval
        :param end_date: the end time of the existing interval
        :return: list of Media
        """

        index = 0
        medias = []
        media_ids = []
        has_next_page = True
        while index < count and has_next_page:

            time.sleep(self.sleep_between_requests)
            response = self.__req.get(
                endpoints.get_medias_json_by_tag_link(tag, max_id),
                headers=self.generate_headers(self.user_session))

            if response.status_code != Instagram.HTTP_OK:
                raise InstagramException.default(response.text,
                                                 response.status_code)

            arr = response.json()

            try:
                arr['graphql']['hashtag']['edge_hashtag_to_media']['count']
            except KeyError:
                return []

            nodes = arr['graphql']['hashtag']['edge_hashtag_to_media']['edges']
            for media_array in nodes:
                if index == count:
                    return medias
                media = Media(media_array['node'])
                if media.identifier in media_ids:
                    return medias

                if min_timestamp is not None \
                        and media.created_time < min_timestamp:
                    return medias

                if (end_date < media.created_time < start_date):
                    print('This media is already checked')
                    continue

                media_ids.append(media.identifier)
                medias.append(media)
                index += 1

            if len(nodes) == 0:
                return medias

            max_id = \
                arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info'][
                    'end_cursor']
            has_next_page = \
                arr['graphql']['hashtag']['edge_hashtag_to_media']['page_info'][
                    'has_next_page']

        return medias

myInstagram = MyInstagram()


# Download images without using database
class LoadDataWithoutDatabase:
    def __init__(self):
        log_in()

    def load_data_by_tag_without_database(self, hashtags):
        """
        :return: Download images in file folders
        """

        # hash_list = hashtags.split()
        # print(hash_list)
        # print(hash_list[0])
        # print(len(hash_list))

    # i=0
    # while i < len(hash_list):
    #     #Creating a hashtag
    #     hashtag = str(hash_list[i])

        # Loading medias
        # try:
        #     medias = instagram.get_medias_by_tag(hashtag, count=int(os.getenv('HASH_COUNT')))
        # except Exception as e:
        #     print(e)
        #     i = i + 1
        #     continue

        extr_makeup = makeup_extractor.ExtractMakeup(False)
        color_palette_extractor = makeup_extractor.ExtractColors()

        print(hashtags + ' _____________________')

        medias = instagram.get_medias_by_tag(hashtags, count=int(os.getenv('HASH_COUNT')))

        if medias == []:
            print('Данный аккаунт не подходит для работы, попробуйте другой аккаунт')
            # break
        else:
            # Get medias
            print(medias)
            for media in medias:

                # Get image
                p = requests.get(media.image_high_resolution_url)
                pic_url = p.url.split('?')[0].split('/')[-1]

                # Face detection
                url = p.url
                webUrl = urllib.request.urlopen(url)
                image = Image.open(webUrl)
                content = p.content

                img = np.array(image)
                if extr_makeup.detect_face(img):
                    print('face detected')

                    # Extract makeup and palette
                    try:
                        makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                    except Exception as e:
                        print(e)
                        continue

                    makeup_img = Image.fromarray(makeup)
                    palette_img = Image.fromarray(palette)

                    print('extracted')

                    # Extract out_text
                    list_of_image_tags = []
                    caption = media.caption
                    if caption != None:
                        arr = caption.split('#')
                        j = 1
                        while j < len(arr):
                            el = arr[j].replace(' ', '')
                            if contains(el):
                                list_of_image_tags.append(el)
                            j = j + 1
                    else:
                        list_of_image_tags.append(hashtags)

                    print(list_of_image_tags)

                    # # Extract user name
                    # account = media.owner
                    # acc_id = account.identifier
                    # try:
                    #     acc_info = instagram.get_account_by_id(acc_id)
                    # except Exception as e:
                    #     print(e)
                    #     user_name = None
                    # else:
                    #     user_name = acc_info.username

                    # Write data to files
                    tags_path = out_imgs_folder_for_tags + hashtags + '/'
                    out_img_path = tags_path + '/' + pic_url.split('.')[0] + '/'
                    if not os.path.exists(tags_path):
                        os.mkdir(tags_path)
                    if not os.path.exists(out_img_path):
                        os.mkdir(out_img_path)

                    # Save images
                    with open(out_img_path + pic_url.split('.')[0] + '.jpg', "wb") as fimage:
                        fimage.write(content)
                        fimage.close()
                    with open(out_all_images_folder + pic_url.split('.')[0] + '.jpg', "wb") as allfimage:
                        allfimage.write(content)
                        allfimage.close()

                    makeup_img.save(out_img_path + '/' + 'makeup.png')
                    palette_img.save(out_img_path + '/' + 'palette.png')

                    makeup_img.save(out_all_makeups_folder + pic_url.split('.')[0] + '.png')
                    palette_img.save(out_all_palettes_folder + pic_url.split('.')[0] + '.png')

                    print('saved')

                    # Save text
                    if list_of_image_tags != []:
                        if os.path.exists(out_text_folder_for_images + pic_url.split('.')[0] + '.txt'):
                            with open(out_text_folder_for_images + pic_url.split('.')[0] + '.txt', "r") as frtxt:
                                list_of_existing_tags = frtxt.read()
                                list_of_existing_tags.rstrip(' ')
                                tags_list = list_of_existing_tags.split()
                                frtxt.close()
                            with open(out_text_folder_for_images + pic_url.split('.')[0] + '.txt', "a") as fatxt:
                                for el in list_of_image_tags:
                                    if not any(x == el for x in tags_list):
                                        fatxt.write(el + ' ')
                                fatxt.close()
                        else:
                            with open(out_text_folder_for_images + pic_url.split('.')[0] + '.txt', "a") as fatxt:
                                for el in list_of_image_tags:
                                   fatxt.write(el + ' ')
                                fatxt.close()

            print('close file ' + hashtags)
            print('________________________________________________________')
            # i = i + 1

    def load_data_by_user_name_without_database(self, username):
        """
        :return: Download images and user info(tags) in database test_images
        """

        extr_makeup = makeup_extractor.ExtractMakeup(False)
        color_palette_extractor = makeup_extractor.ExtractColors()

        # i = 0
        # while i < len(user_name_list):
        # Creating a user_id
        user_name = username
        log_in()
        try:
            medias = instagram.get_medias(user_name, int(os.getenv('MEDIA_COUNT')))
        except Exception as infe:
            print(infe)
            return print('nothing to find')
            # i = i + 1
            # continue

        list_of_user_tags = []

        # Get medias
        for media in medias:

            # Get image
            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]

            # Check if image has face
            url = p.url
            webUrl = urllib.request.urlopen(url)
            image = Image.open(webUrl)
            content = p.content
            img = np.array(image)

            if extr_makeup.detect_face(img):

                # Extract makeup and palette
                try:
                    makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                except Exception as e:
                    print(e)
                    continue

                makeup_img = Image.fromarray(makeup)
                palette_img = Image.fromarray(palette)


                # Extract out_text
                caption = media.caption
                if caption != None:
                    arr = caption.split('#')
                    j = 1
                    while j < len(arr):
                        el = arr[j].replace(' ', '')
                        if contains(el):
                            list_of_user_tags.append(el)
                        j = j + 1

                print(list_of_user_tags)

                # Write data to files
                images_path = out_imgs_folder_for_names + user_name + '/'
                images_path_name = images_path + pic_url.split('.')[0] + '/'
                if not os.path.exists(images_path):
                    os.mkdir(images_path)
                if not os.path.exists(images_path_name):
                    os.mkdir(images_path_name)

                # Save images
                with open(images_path_name + pic_url.split('.')[0] + '.jpg', "wb") as fimage:
                    fimage.write(content)
                    fimage.close()
                with open(out_all_images_folder + pic_url.split('.')[0] + '.jpg', "wb") as allfimage:
                    allfimage.write(content)
                    allfimage.close()

                makeup_img.save(images_path_name + '/' + 'makeup.png')
                palette_img.save(images_path_name + '/' + 'palette.png')

                makeup_img.save(out_all_makeups_folder + pic_url.split('.')[0] + '.png')
                palette_img.save(out_all_palettes_folder + pic_url.split('.')[0] + '.png')

                # Save text
                if not list_of_user_tags == []:
                    if os.path.exists(out_text_folder_for_names + user_name + '.txt'):
                        with open(out_text_folder_for_names + user_name + '.txt', "r") as frtxt:
                            list_of_existing_tags = frtxt.read()
                            list_of_existing_tags.rstrip(' ')
                            tags_list = list_of_existing_tags.split()
                            frtxt.close()
                        with open(out_text_folder_for_names + user_name + '.txt', "a") as fatxt:
                            for el in list_of_user_tags:
                                if not any(x == el for x in tags_list):
                                    fatxt.write(el + ' ')
                            fatxt.close()
                    else:
                        with open(out_text_folder_for_names + user_name + '.txt', "a") as fatxt:
                            for el in list_of_user_tags:
                                fatxt.write(el + ' ')
                            fatxt.close()

        print('close file ' + user_name)
        print('________________________________________________________')
        # i = i + 1

    def by_tags(self):
        hashtags = os.getenv('HASHTAGS')
        hash_list = hashtags.split()
        print(hash_list)
        print(len(hash_list))
        print("number of publication = " + os.getenv('HASH_COUNT'))

        runThreads(self.load_data_by_tag_without_database, hash_list)

    def by_user_names(self):
        user_name_list = os.getenv('USER_NAMES').split()
        print(user_name_list)
        print(user_name_list[0])
        print(len(user_name_list))
        print("number of publication = " + os.getenv('MEDIA_COUNT'))

        runThreads(self.load_data_by_user_name_without_database, user_name_list)

# Download images in database
class LoadData:
    def __init__(self):
        log_in()

    def load_data_by_tag(self, hashtags):
        """
        :return: Download images in database test_images
        """

        # cookie = "sessions/diplom-test.txt"
        # instagram.set_cookies(cookie)

        images_collection, users_collection, tags_collection = connecting_to_mongo_server()

        extr_makeup = makeup_extractor.ExtractMakeup(False)
        color_palette_extractor = makeup_extractor.ExtractColors()

        # hash_list = hashtags.split()
        # print(hash_list)
        # print(hash_list[0])
        # print(len(hash_list))

        # i=0
        # while i < len(hash_list):
        #Creating a hashtag
        hashtag = hashtags

        # Loading medias
        try:
            medias = instagram.get_medias_by_tag(hashtag, count=int(os.getenv('HASH_COUNT')))
        except Exception as jsonerror:
            print(jsonerror)
            # i = i + 1
            # continue
            return print("nothing to find")

        if medias == []:
            return print('Данный аккаунт не подходит для работы, попробуйте другой аккаунт')
            # break

        # Get medias
        for media in medias:

            # Extract date of publication
            publication_time = media.created_time

            # Get image
            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]

            # Face detection
            url = p.url
            webUrl = urllib.request.urlopen(url)
            image = Image.open(webUrl)
            content = p.content

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

                makeup_as_txt = m_buffer.tobytes()
                palette_as_txt = p_buffer.tobytes()

                # makeup_as_txt = base64.b64encode(m_buffer)
                # palette_as_txt = base64.b64encode(p_buffer)

                # ENCODE IMAGE
                # b_img = base64.b64encode(content)

                # Extract out_text
                list_of_image_tags = []
                caption = media.caption
                if caption != None:
                    arr = caption.split('#')
                else:
                    arr = [hashtag]
                j = 0
                while j < len(arr):
                    el = arr[j].replace(' ', '')
                    if contains(el):
                        list_of_image_tags.append(el)
                    j = j + 1
                print(list_of_image_tags)

                # Extract user name
                account = media.owner
                acc_id = account.identifier
                try:
                    acc_info = instagram.get_account_by_id(acc_id)
                except Exception as e:
                    print(e)
                    user_name = None
                else:
                    user_name = acc_info.username


                # Insert data in database
                try:
                    images_collection.insert_one({'_id': pic_url.split('.')[0], 'tag': list_of_image_tags, 'q_grade': 0, 'image': content, 'makeup': makeup_as_txt, 'palette': palette_as_txt, 'publication_time': publication_time})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)
                if user_name != None:
                    try:
                        users_collection.insert_one({'_id': user_name, 'tags_list': list_of_image_tags, 'q_grade': 0, 'images': [pic_url.split('.')[0]]})
                    except Exception as e:
                        print(e)
                        users_collection.update_one({'_id': user_name}, {'$addToSet': {'tags_list': {'$each': list_of_image_tags}, 'images': pic_url.split('.')[0]}}, upsert=True)

        print('close file ' + hashtag)
        print('________________________________________________________')
        # i = i + 1

    def load_data_by_user_name(self, user_name):
        """
        :return: Download images and user info(tags) in database test_images
        """

        images_collection, users_collection, tags_collection = connecting_to_mongo_server()

        extr_makeup = makeup_extractor.ExtractMakeup(False)
        color_palette_extractor = makeup_extractor.ExtractColors()

        # user_name_list = os.getenv('USER_NAMES').split()
        # print(user_name_list)
        # print(user_name_list[0])
        # print(len(user_name_list))

        # i = 0
        # while i < len(user_name_list):
        # Creating a user_id
        user_name = user_name
        log_in()
        try:
            medias = instagram.get_medias(user_name, int(os.getenv('MEDIA_COUNT')))
        except Exception as infe:
            print(infe)
            # i = i + 1
            # continue
            return print("nothing to find")

        list_of_user_tags = []

        # Get medias
        for media in medias:

            # Get image
            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]

            # Check if image has face
            url = p.url
            webUrl = urllib.request.urlopen(url)
            image = Image.open(webUrl)
            content = p.content
            img = np.array(image)

            if extr_makeup.detect_face(img):

                # Extract date of publication
                publication_time = media.created_time

                # ENCODE IMAGE
                # b_img = base64.b64encode(content)

                # Extract makeup and palette
                try:
                    makeup, palette = makeup_extractor.get_results_as_nparray(img, extr_makeup, color_palette_extractor)
                except Exception as e:
                    print(e)
                    continue

                m_retval, m_buffer = cv2.imencode('.png', makeup)
                p_retval, p_buffer = cv2.imencode('.png', palette)

                makeup_as_txt = m_buffer.tobytes()
                palette_as_txt = p_buffer.tobytes()

                # makeup_as_txt = base64.b64encode(m_buffer)
                # palette_as_txt = base64.b64encode(p_buffer)

                # Extract out_text
                caption = media.caption
                if caption != None:
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
                        {'_id': pic_url.split('.')[0], 'tag': list_of_user_tags, 'q_grade': 0, 'image': content, 'makeup': makeup_as_txt, 'palette': palette_as_txt, 'publication_time': publication_time})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)

        print('close file ' + user_name)
        print('________________________________________________________')
        # i = i + 1

    def by_tags(self):
        hashtags = os.getenv('HASHTAGS')
        hash_list = hashtags.split()
        print(hash_list)
        print(len(hash_list))
        print("number of publication = " + os.getenv('HASH_COUNT'))

        runThreads(self.load_data_by_tag, hash_list)

    def by_user_names(self):
        user_name_list = os.getenv('USER_NAMES').split()
        print(user_name_list)
        print(user_name_list[0])
        print(len(user_name_list))
        print("number of publication = " + os.getenv('MEDIA_COUNT'))

        runThreads(self.load_data_by_user_name, user_name_list)

#Load images from database to local directories
class ShowImages:
    def __init__(self):
        self.images_collection, self.users_collection, self.tags_collection = connecting_to_mongo_server()

    def show_image_by_id(self, img_id_list):
        """
        :param img_id_list: string array of image ids
        :return: list of binary images
        """

        images_list = []
        makeup_list = []
        palette_list = []
        for img_id in img_id_list:
            if self.images_collection.find_one({'_id': img_id}) == {}:
                print('NO IMAGE WITH ID = ' + img_id)
            else:
                image = self.images_collection.find_one({'_id': img_id})
                images_list.append(image['image'])
                palette_list.append(image['palette'])
                makeup_list.append(image['makeup'])
        return images_list, makeup_list, palette_list

    def show_image_by_tag(self, tags):
        """
        :param tags: string array or value of tags
        :return: download images in out_img_path
        """

        # for i in self.images_collection.find({}):
        #     docSize = sys.getsizeof(i['image'])
        #     print(i['_id'])
        #     print(docSize)
        #     print('_______________')

        tag_list = tags.split()
        for tag in tag_list:
            for img in self.images_collection.find({'tag': { '$all' : [str(tag)] }}):
                tags_path = 'out_imgs/tags/' + str(tag) + '/'
                out_img_path = 'out_imgs/tags/' + str(tag) + '/' + img['_id'] + '/'
                if not os.path.exists(tags_path):
                    os.mkdir(tags_path)
                if not os.path.exists(out_img_path):
                    os.mkdir(out_img_path)
                out_text_path = 'out_text/image_names/'
                if not os.path.exists(out_text_path):
                    os.mkdir(out_text_path)


                with open(out_img_path + img['_id'] + '.jpg', "wb") as fimage:
                    #decoded_image = base64.b64decode(img['image'])
                    fimage.write(img['image'])
                    fimage.close()
                with open(out_all_images_folder + img['_id'] + '.jpg', "wb") as allfimage:
                    #decoded_image = base64.b64decode(img['image'])
                    allfimage.write(img['image'])
                    allfimage.close()

                # Extract makeup and palette
                # makeup_nparr = np.frombuffer(base64.b64decode(img['makeup']), np.uint8)
                # palette_nparr = np.frombuffer(base64.b64decode(img['palette']), np.uint8)

                makeup_nparr = np.frombuffer(img['makeup'], np.uint8)
                palette_nparr = np.frombuffer(img['palette'], np.uint8)

                makeup_img = cv2.imdecode(makeup_nparr, cv2.IMREAD_UNCHANGED)
                palette_img = cv2.imdecode(palette_nparr, cv2.IMREAD_UNCHANGED)

                makeup = Image.fromarray(makeup_img)
                palette = Image.fromarray(palette_img)

                makeup.save(out_img_path + 'makeup.png')
                palette.save(out_img_path + 'palette.png')

                makeup.save(out_all_makeups_folder + img['_id'] + '.png')
                palette.save(out_all_palettes_folder + img['_id'] + '.png')

                with open(out_text_path + img['_id'] + '.txt', 'w') as ftxt:
                    for el in img['tag']:
                        ftxt.write(el + ' ')
                    ftxt.close()


    def show_image_by_user_name(self, names):
        """
        :param names: string array or value of names
        :return: download images in out_img_path
                 download array of tags in out_text_path
        """

        names_list = names.split()
        for name in names_list:
            for user in self.users_collection.find({'_id': str(name)}):
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

                images_list, makeups_list, palettes_list = self.show_image_by_id(user['images'])

                i = 0
                while i < len(images_list):
                    with open(names_path + user['images'][i] + '/' + user['images'][i] + '.jpg', "wb") as fimage:
                        fimage.write(images_list[i])
                        fimage.close()
                    with open(out_all_images_folder + user['images'][i] + '.jpg', "wb") as allfimage:
                        allfimage.write(images_list[i])
                        allfimage.close()

                        # Extract makeup and palette
                        # makeup_nparr = np.frombuffer(base64.b64decode(makeups_list[i]), np.uint8)
                        # palette_nparr = np.frombuffer(base64.b64decode(palettes_list[i]), np.uint8)

                        makeup_nparr = np.frombuffer(makeups_list[i], np.uint8)
                        palette_nparr = np.frombuffer(palettes_list[i], np.uint8)

                        makeup_img = cv2.imdecode(makeup_nparr, cv2.IMREAD_UNCHANGED)
                        palette_img = cv2.imdecode(palette_nparr, cv2.IMREAD_UNCHANGED)

                        makeup = Image.fromarray(makeup_img)
                        palette = Image.fromarray(palette_img)

                        makeup.save(names_path + user['images'][i] + '/' + 'makeup.png')
                        palette.save(names_path + user['images'][i] + '/' + 'palette.png')

                        makeup.save(out_all_makeups_folder + user['images'][i] + '.png')
                        palette.save(out_all_palettes_folder + user['images'][i] + '.png')

                    i = i + 1

                with open(out_text_path + str(name) + '.txt', 'w') as ftxt:
                    for el in user['tags_list']:
                        ftxt.write(el + ' ')
                    ftxt.close()

# NOT READY NOW
def load_data_by_tag_generate_autotags(hashtags, start_list, end_list):
    """
    :return: Download images in database test_images
    """

    # cookie = "sessions/diplom-test.txt"
    # instagram.set_cookies(cookie)

    images_collection, users_collection, tags_collection = connecting_to_mongo_server()

    hash_list = hashtags.split()
    print(hash_list)
    print(hash_list[0])
    print(len(hash_list))

    i=0
    while i < len(hash_list):
        #Creating a hashtag
        hashtag = str(hash_list[i])

        medias = myInstagram.get_medias_by_tag_new(hashtag, start_list[i], end_list[i], count=int(os.getenv('HASH_COUNT')))

        # Get medias
        for media in medias:

            # Get image
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

                # Extract date of publication
                publication_time = media.created_time

                # ENCODE IMAGE
                b_img = base64.b64encode(content)

                # Extract out_text
                list_of_image_tags = []
                caption = media.caption
                if caption != None:
                    arr = caption.split('#')
                else:
                    arr = []
                j = 1
                while j < len(arr):
                    el = arr[j].replace(' ', '')
                    if contains(el):
                        list_of_image_tags.append(el)
                    j = j + 1
                print(list_of_image_tags)

                # Extract user name
                account = media.owner
                acc_id = account.identifier
                acc_info = instagram.get_account_by_id(acc_id)
                user_name = acc_info.username


                # Insert data in database
                try:
                    images_collection.insert_one({'_id': pic_url.split('.')[0], 'tag': list_of_image_tags, 'q_grade': 0, 'image': b_img, 'makeup': makeup_as_txt, 'palette': palette_as_txt, 'publication_time': publication_time})
                except Exception as e:
                    print(e)
                    continue
                print(pic_url)
                try:
                    users_collection.insert_one({'_id': user_name, 'tags_list': list_of_image_tags, 'q_grade': 0, 'images': [pic_url.split('.')[0]]})
                except Exception as e:
                    print(e)
                    users_collection.update_one({'_id': user_name}, {'$addToSet': {'tags_list': {'$each': list_of_image_tags}, 'images': pic_url.split('.')[0]}}, upsert=True)

        print('close file ' + hashtag)
        print('________________________________________________________')
        i = i + 1

#NOT READY NOW
def append_tags():

    images_collection, users_collection, tags_collection = connecting_to_mongo_server()

    tags_list_dubles = []
    tags_list = []
    tags_for_search = []
    start_date_list = []
    end_date_list = []
    for user in users_collection.find():
        tags_list_dubles.extend(user['tags_list'])
        tags_list = list(set(tags_list_dubles))

    i=0
    while i < len(tags_list):
        date_list = []
        count_smth = images_collection.count_documents({'tag': tags_list[i]})
        if count_smth > 5:
            tags_for_search.append(tags_list[i])
            for image in images_collection.find({'tag': tags_list[i]}):
                date_list.append(image['publication_time'])

            try:
                tags_collection.insert_one(
                    {'_id': tags_list[i], 'start_date': max(date_list), 'end_date': min(date_list)})
                start_date_list.append(max(date_list))
                end_date_list.append(min(date_list))
            except Exception as e:
                print(e)
                smth = tags_collection.find_one({'_id': tags_list[i]})['start_date']
                if smth < max(date_list):
                    tags_collection.update_one({'_id': tags_list[i]}, {'start_date': max(date_list)}, upsert=True)
                    start_date_list.append(max(date_list))

                else:
                    start_date_list.append(tags_collection.find_one({'_id': tags_list[i]})['start_date'])

                if tags_collection.find_one({'_id': tags_list[i]})['end_date'] > min(date_list):
                    tags_collection.update_one({'_id': tags_list[i]}, {'end_date': min(date_list)}, upsert=True)
                    end_date_list.append(min(date_list))

                else:
                    end_date_list.append(tags_collection.find_one({'_id': tags_list[i]})['end_date'])

        i = i+1

    return tags_for_search, start_date_list, end_date_list

# NOT READY NOW
def generate_autotags():

    images_collection, users_collection, tags_collection = connecting_to_mongo_server()

    new_tags, start, end = append_tags()
    new_tags_str = ' '.join(new_tags)
    log_in()
    load_data_by_tag_generate_autotags(new_tags_str, start, end)
    while images_collection.count_documents({}) < 500:
        new_tags, start, end = append_tags()
        new_tags_str = ' '.join(new_tags)
        log_in()
        load_data_by_tag_generate_autotags(new_tags_str, start, end)

# Extract makeup and palette locally (not needed any more)
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

# Extract makeup and palette locally (not needed any more)
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


# IT'S JUST TO TEST LOG_IN:

# Login to instagram
#log_in()

# LOAD DATA USING DATABASE:

# You don't have to run log_in() function for load_data_by_user_name(), because it included there
# load_data = LoadData()

# load_data.by_tags()
# load_data.by_user_names()

# NOT READY YET:
#generate_autotags()

# LOAD DATA WITHOUT DATABASE:

load_data_locally = LoadDataWithoutDatabase()

load_data_locally.by_tags()
# load_data_locally.by_user_names()

# SHOW IMAGES FROM DATABASE:

#show_images = ShowImages()
#show_images.show_image_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))
#show_images.show_image_by_user_name(os.getenv('USER_NAMES_FOR_SEARCH'))

# YOU DON'T NEED FUNCTIONS BELOW:

# Extract makeup from downloaded images
#extract_makeup_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))
#extract_makeup_by_user(os.getenv('USER_NAMES_FOR_SEARCH'))

# Delete <collection_name> collection from db test_images
#db.<collection_name>.drop()



# EXPERIMENTS (NOT FOR USERS):

# log_in()
# hashtags = os.getenv('HASHTAGS')
# hash_list = hashtags.split()
# for h in hash_list:
#     medias = instagram.get_medias_by_tag(h, count=10, min_timestamp=1621825200)

# timestamp = 1620244531
# time = time.strftime("%d %b %Y %H:%M:%S GMT", time.gmtime(timestamp / 1000.0)).split(' ')
# print(time)

# from datetime import datetime, timezone
#
# unix_timestamp = float("1621825200")
# # local_timezone = tzlocal.get_localzone() # get pytz timezone
# # local_time = datetime.fromtimestamp(unix_timestamp, local_timezone)
#
# utc_time = datetime.fromtimestamp(unix_timestamp, timezone.utc)
# local_time = utc_time.astimezone()
# print(local_time.strftime("%Y-%m-%d %H:%M:%S.%f%z (%Z)"))

# utc_time = datetime.utcfromtimestamp(unix_timestamp)
# print(utc_time.strftime("%Y-%m-%d %H:%M:%S.%f+00:00 (UTC)"))

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


# time_list = []
# medias = instagram.get_medias('alek_chereshnya')
# for media in medias:
#     print(media)
#     print('------------------------------------------------')
#     time_list.append(media.created_time)
#
# print(time_list)
#
# i = 0
# while i < len(time_list) - 1:
#     if time_list[i] > time_list[i+1]:
#         print('ok')
#     else:
#         print('nooo')
#     i = i+1
