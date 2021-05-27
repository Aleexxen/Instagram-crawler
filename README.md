# Diplom

Don't forget to pip install all from ***requirements.txt***

***<ins>How to use?</ins>***  
In the ***.env*** directory put your arguments  

At the very top, select the path to your file ***.env***, an example of such a file is ***env.sample***  
Uncomment functions you need  
Then click run  
That's all  

***<ins>How it works?</ins>***  
Example:  
uncomment function at the bottom   
***load_data_locally = LoadDataWithoutDatabase()***  

***load_data_locally.by_tags()***  
  
All images will appear in ***"out_imgs" "all_images" "all_makeups" "all_palettes"*** packages in packages with their own ***hashtag*** name  

Each image has its own ***unique name***  

So you can find data here  

***<ins>ПРЕДУПРЕЖДЕНИЕ!</ins>***  
Пожалуйста не ставьте в полях файла настроек ***HASH_COUNT и MEDIA_COUNT*** значения больше ***300***  
Иначе инстаграм выдает ошибку на превышение лимита запросов для некоторых из параметров поиска(ну какие-то всё равно будут загружены, так что на ваше усмотрение)

***<ins>Интерактивные окна и звуки</ins>***  
При запуске функций ниже для вашего удобства были сделаны следующие дополнения:  
Когда программа заканчивает работу, в зависимости от вашей операционной системы раздается либо гудок(Windows), либо голос(MacOS)  
  
 После оповещения об окончании программы в окне вам предложат выбор ***хотите ли вы перезапустить программу?***:  
 ![изображение](https://user-images.githubusercontent.com/49920406/119830047-8b227e00-bf04-11eb-8790-0a026ea6bf6e.png)

   
 Если ***Yes*** - программа перезапускается  
 Иначе выдается такое окно:  
![изображение](https://user-images.githubusercontent.com/49920406/119830118-9d042100-bf04-11eb-8557-147ca7b7491c.png)


  
***<ins>Выгрузить данные по списку тэгов без бд</ins>***  
Раскомментировать функции ***load_data_locally = LoadDataWithoutDatabase()*** (создать экземпляр класса) и ***load_data_locally.by_tags()***  
Результат будет в локальных папках  
  
***<ins>Выгрузить данные по списку пользователей без бд</ins>***  
Раскомментировать функции ***load_data_locally = LoadDataWithoutDatabase()*** и ***load_data_locally.by_user_names()***  
Результат будет в локальных папках  
  
***<ins>Выгрузить данные по списку тэгов</ins>***   
Раскомментировать функции ***load_data = LoadData()*** (создать экземпляр класса) и ***load_data.by_tags()***  
Результат будет на сервере  

***<ins>Выгрузить данные по списку юзеров</ins>***  
Раскомментировать функции ***load_data = LoadData()*** (создать экземпляр класса) и ***load_data.by_user_names()***  
Результат будет на сервере  

***<ins>Выгрузить данные по списку тэгов с сервера</ins>***  
Раскомментировать функции ***show_images = ShowImages()*** и ***show_images.show_image_by_tag(os.getenv('HASHTAGS_FOR_SEARCH'))***  
Результат будет в локальных папках  
  
***<ins>Выгрузить данные по списку юзеров с сервера</ins>***  
Раскомментировать функции ***show_images = ShowImages()*** и ***show_images.show_image_by_user_name(os.getenv('USER_NAMES_FOR_SEARCH'))***  
Результат будет в локальных папках   

Теперь две следующие функции не обязательны, так как макияж и палетка цветов сразу вырезаются при выгрузке изображения из инстаграмма

***<ins>Вырезать макияж по списку тэгов</ins>***  
Раскомментировать функцию ***extract_makeup_by_tag()***  
Результат будет в папке ***out_imgs***   

***<ins>Вырезать макияж по списку юзеров</ins>***  
Раскомментировать функцию ***extract_makeup_by_user()***  
Результат будет в папке ***out_imgs***   
