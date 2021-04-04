from igramscraper.instagram import Instagram
import csv
import requests
import configparser
import os

proxies = {
    #'http':'http://109.172.57.64:8081',
    'http':'http://46.229.214.206:3128',
}

config = configparser.ConfigParser()
config.read("settings.ini")
hash_list = config.get("FilesConf", "hashtags").split()
print(hash_list)
print(hash_list[0])
print(len(hash_list))

instagram = Instagram()
instagram.set_proxies(proxies)

instagram.with_credentials('login', 'password')
instagram.login()

# account = instagram.get_account_by_id(3015034946)
# print(account)

def load_data():
    i=0
    while i < len(hash_list):
        #Creating a hashtag
        hashtag = str(hash_list[i])
        medias = instagram.get_medias_by_tag(hashtag, count=1)
        #csvWriter.writerow(['Heshtag', hashtag])

        # Open/Create a file to append data to
        # fcsv = open('files_with_data/' + str(hash_list[i]) + '.csv', 'w')
        # csvWriter = csv.writer(fcsv)

        print('open file ' + str(hash_list[i]))
        for media in medias:
            if not os.path.exists('files_with_data/' + str(hash_list[i])):
                os.mkdir('files_with_data/' + str(hash_list[i]))

            p = requests.get(media.image_high_resolution_url)
            pic_url = p.url.split('?')[0].split('/')[-1]
            print(pic_url)
            out = open('files_with_data/' + str(hash_list[i]) + '/' + str(pic_url), "wb")
            out.write(p.content)
            out.close()
            #csvWriter.writerow([media.square_images])

        #fcsv.close()
        print('close file ' + str(hash_list[i]))
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

load_data()
print('max image size = ' + str(find_max_size_from_all()) + ' bites')