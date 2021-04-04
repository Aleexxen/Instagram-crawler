from igramscraper.instagram import Instagram
import csv
import requests
import configparser
import os

proxies = {
    'http':'http://109.172.57.64:8081',
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

instagram.with_credentials('alek_chereshnya', 'Leeyler_1234567890')
instagram.login()

# account = instagram.get_account_by_id(3015034946)
# print(account)

i=0
while i < len(hash_list):
    #Creating a hashtag
    hashtag = str(hash_list[i])
    medias = instagram.get_medias_by_tag(hashtag, count=10)
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