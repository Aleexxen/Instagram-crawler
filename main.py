from igramscraper.instagram import Instagram
import csv
import configparser

# proxies = {
#     'http': 'http://123.45.67.8:1087',
#     'https': 'http://123.45.67.8:1087',
# }

config = configparser.ConfigParser()
config.read("settings.ini")
hash_list = config.get("FilesConf", "hashtags").split()
print(hash_list)
print(hash_list[0])
print(len(hash_list))

instagram = Instagram()
# instagram.set_proxies(proxies)

instagram.with_credentials('login', 'password')
instagram.login()

# account = instagram.get_account_by_id(3015034946)
# print(account)

i=0
while i < len(hash_list):
    # Open/Create a file to append data to
    # ftxt = open('runwaymakeup1.txt', 'w')
    # fxls = open('runwaymakeup1.xls', 'w')
    fcsv = open('files_with_data/' + str(hash_list[i]) + '.csv', 'w')
    csvWriter = csv.writer(fcsv)
    print('open file ' + str(hash_list[i]))

    # Creating a hashtag
    hashtag = str(hash_list[i])
    medias = instagram.get_medias_by_tag(hashtag, count=10000)
    csvWriter.writerow(['Heshtag', hashtag])

    for media in medias:
        csvWriter.writerow([media.image_high_resolution_url])

    fcsv.close()
    print('close file ' + str(hash_list[i]))
    i = i + 1