# Diplom

How to use?  

In the main.py file we have this section:  

instagram.with_credentials('login', 'password')  
instagram.login()  

Here you should enter your instagram login and password  

Next step:  
In settings.ini file you should check "hashtags" field if you need any of these hashtags and change some if necessary  

Next:  
On line 32 of the main.py file  
medias = instagram.get_medias_by_tag(hashtag, count=10)  

You change the number of images for each hashtag in the "count" field    

Then click run  
That's all  

How it works?  
All images will appear in "files_with_data" package in packages with their own hashtag name  

Each image has its own unique name  

So you can find data here  
