# Diplom

Don't forget to pip install all from ***requirements.txt***

<ins>How to use?</ins>  
In the ***.env*** directory put your arguments  

At the very top, select the path to your file ***.env***, an example of such a file is ***env.sample***  
Uncomment functions you need  
Then click run  
That's all  

<ins>How it works?</ins>  
Example:  
uncomment ***show_image_by_tag()*** function at the bottom  
All images will appear in ***"out_imgs"*** package in packages with their own ***hashtag*** name  

Each image has its own ***unique name***  

So you can find data here  

<ins>Выгрузить данные по списку тэгов без бд</ins>  
Раскомментировать функции ***log_in()*** (не обязательно) и ***load_data_by_tag_without_database()***  
Результат будет на сервере  

<ins>Выгрузить данные по списку пользователей без бд</ins>  
Раскомментировать функции ***load_data_by_user_name_without_database()***  
Результат будет на сервере  

<ins>Выгрузить данные по списку тэгов</ins>  
Раскомментировать функции ***log_in()*** (не обязательно) и ***load_data_by_tag()***  
Результат будет на сервере  

<ins>Выгрузить данные по списку юзеров</ins>  
Раскомментировать функцию ***load_data_by_user_name()***  
Результат будет на сервере  

<ins>Выгрузить данные по списку тэгов с сервера</ins>  
Раскомментировать функцию ***show_image_by_tag()***  
Результат будет в папке ***out_imgs***  

<ins>Выгрузить данные по списку юзеров с сервера</ins>  
Раскомментировать функцию ***show_image_by_user_name()***  
Результат будет в папке ***out_imgs*** и ***out_txt***  

Теперь две следующие функции не обязательны, так как макияж и палетка цветов сразу вырезаются при выгрузке изображения из инстаграмма

<ins>Вырезать макияж по списку тэгов</ins>  
Раскомментировать функцию ***extract_makeup_by_tag()***  
Результат будет в папке ***out_imgs***   

<ins>Вырезать макияж по списку юзеров</ins>  
Раскомментировать функцию ***extract_makeup_by_user()***  
Результат будет в папке ***out_imgs***   
