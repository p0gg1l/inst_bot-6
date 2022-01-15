import os.path

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from auth_data import username, password
import time
import random
from selenium.common.exceptions import NoSuchElementException
import requests


class instagramBot():

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.browser = webdriver.Chrome('../chromedriver/chromedriver.exe')


    def close_browser(self):
        self.browser.close()
        self.browser.quit()


    def login(self):
        browser = self.browser
        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(6)
    def xpath_exists(self, url):

        browser = self.browser
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def get_on_posts_url(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(4)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print("Такого пользователя не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пользователь успешно найден, ставим лайки!")
            time.sleep(2)

            posts_count = int(browser.find_element_by_xpath(
                "/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span").text)
            loops_count = int(posts_count / 60)
            print(loops_count)

            posts_urls = []
            for i in range(0, loops_count):
                hrefs = browser.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.randrange(2, 4))
                print(f"Итерация #{i}")

            file_name = userpage.split("/")[-2]

            with open(f'{file_name}.txt', 'a') as file:
                for post_url in posts_urls:
                    file.write(post_url + "\n")

            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f'{file_name}_set.txt', 'a') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')


    def download_content(self, userpage):
        browser = self.browser
        self.get_on_posts_url(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        img_and_videos_src_url = []

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list[0:10]:
                try:
                    browser.get(post_url)
                    time.sleep(4)

                    img_src = '/html/body/div[6]/div[2]/div/article/div/div[1]/div/div/div[1]/img'
                    video_src = '/html/body/div[6]/div[2]/div/article/div/div[1]/div/div/div/div/div/video'

                    if self.xpath_exists(img_src):
                        img_src_url = browser.find_element_by_xpath(img_src).get_attribute("src")
                        img_and_videos_src_url.append(img_src_url)
                        post_id = post_id.split("/")[-2]

                        #coxp изобр
                        get_img = requests.get(img_src_url)
                        with open(f"{post_id}_img.jpg", "wb") as img_file:
                            img_file.write(get_img.content)



                    elif self.xpath_exists(video_src):
                            video_src_url = browser.find_element_by_xpath(video_src).get_attribute("src")
                            img_and_videos_src_url.append(video_src_url)

                            # coxp video
                            get_video = requests.get(video_src_url, stream=True)
                            with open(f"{post_id}_video.mp4", "wb") as video_file:
                                for chunk in get_video.iter.content(chunk_size = 1024 * 1024):
                                    if chunk:
                                        video_file.write(chunk)
                    else:
                        #print("Oops, 4to to poshlo po pizde, nado ispravit!!!")
                        img_and_videos_src_url.append(f"{post_url} нет ссылки!")
                    print(f"Контент из поста {post_url} успешн скачан!!!")
                except Exception as ex:
                    print(ex)
                    self.close_browser()

            self.close_browser()
        with open('img_and_videos_src_url','a') as file:
            for i in img_and_videos_src_url:
                file.write(i + "\n")


    def put_many_likes(self, userpage):

        browser = self.browser
        self.get_on_posts_url(userpage)
        file_name = userpage.split("/")[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list[0:6]:
                try:
                    browser.get(post_url)
                    time.sleep(2)

                    like_button = "/html/body/div[1]/section/main/div/div/article/div[3]/section[1]/span[1]/button"
                    browser.find_element_by_xpath(like_button).click()
                    # time.sleep(random.randrange(80, 100))
                    time.sleep(2)

                    print(f"Лайк на пост: {post_url} успешно поставлен!")
                except Exception as ex:
                    print(ex)
                    self.close_browser()

        self.close_browser()

    def get_subscribe(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(4)
        file_name = userpage.split("/")[-2]

        #папка для каждого пользователя
        if os.path.exists(f"{file_name}"):
            print(f"Папка {file_name} уже есть")
        else:
            print(f"Создадем папку пользователя {file_name}")
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            print(f"Пользователя {file_name} не существует, проверьте URL")
            self.close_browser()
        else:
            print("Пользователь успешно найден, скачиваем ссылки!")
            time.sleep(2)

            koli4estvo_followers = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[2]/a")
            followers_count = koli4estvo_followers.text
            followers_count = int(followers_count.split(' ')[0])
            print(f"Количество подписчиков {followers_count}")
            time.sleep(2)

            loops_count = int(followers_count / 12)
            print(f"Количество итераций: {loops_count}")
            time.sleep(random.randrange(2, 4))

            koli4estvo_followers.click()
            time.sleep(random.randrange(1,3))


            followers_ul = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]")

            try:
                followers_urls = []
                for i in range (1 , loops_count + 1):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                    time.sleep(random.randrange(2 , 4))
                    print(f"Итерация {i}")

                all_urls_div = followers_ul.find_elements_by_tag_name("li")

                for url in all_urls_div:
                    url = url.find_element_by_tag_name("a").get_attribute("href")
                    followers_urls.append(url)

                #Сохраняем список в файл
                with open(f"{file_name}/{file_name}.txt", "a") as text_file:
                    for link in followers_urls:
                        text_file.write(link + "\n")

                with open(f"{file_name}/{file_name}.txt",) as text_file:
                    users_urls = text_file.readlines()

                    for user in users_urls:
                        try:
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()
                                    if user in lines:
                                        print(f'Мы уже подписаны на {user}, переходим к следующему!')
                                        continue

                            except Exception as ex:
                                print("файл с ссылками еще не создан")

                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split("/")[-2]

                            if self.xpath_exists('/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/a'):
                                print("Это наш профиль, уже подписан, пропускаем итерацию!")
                            elif self.xpath_exists(
                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div[2]/div/span/span[1]/button/div/span"):
                                print(f"Уже подписаны, на {page_owner} пропускаем итерацию!")
                            else:
                                time.sleep(random.randrange(4, 8))

                            if self.xpath_exists(
                                    "/html/body/div[1]/section/main/div/div/article/div[1]/div/h2"):
                                try:
                                    follow_button = browser.find_element_by_xpath(
                                    "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button").click()
                                    print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
                                except Exception as ex:
                                    print(ex)
                            else:
                                try:
                                    if self.xpath_exists(
                                            "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button"):
                                        follow_button = browser.find_element_by_xpath(
                                            "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button").click()
                                        print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                    else:
                                        follow_button = browser.find_element_by_xpath(
                                            "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/span/span[1]/button").click()
                                        print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')
                                except Exception as ex:
                                    print(ex)

                            # записываем данные в файл для ссылок всех подписок, если файла нет, создаём, если есть - дополняем
                            with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                      'a') as subscribe_list_file:
                                subscribe_list_file.write(user)

                            time.sleep(random.randrange(7, 15))

                        except Exception as ex:
                            print(ex)
                            self.close_browser()

            except Exception as ex:
                print(ex)
                self.close_browser()

            self.close_browser()


    def send_direct_message(self, username="", message=""):

        browser = self.browser
        time.sleep(random.randrange(2, 4))

        direct_message_button = "/html/body/div[1]/section/nav/div[2]/div/div/div[3]/div/div[2]/a"

        if not self.xpath_exists(direct_message_button):
            print("Кнопка директа не найдена")
            self.close_browser()
        else:
            print("Отправляем сообщения:)))")
            direct_message = browser.find_element_by_xpath(direct_message_button).click()
            time.sleep(random.randrange(2, 4))

        #выключаем всплывающее окно

        error_window = "/html/body/div[6]/div/div"
        button_error_window = "/html/body/div[6]/div/div/div/div[3]/button[2]"

        if self.xpath_exists(error_window):
            browser.find_element_by_xpath(button_error_window).click()
            print("Всплывающее окно успешно закрыто:))")
            # self.close_browser()
            time.sleep(random.randrange(2, 4))

        send_message_button = browser.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div/div[3]/div/button").click()
        time.sleep(2)

        #вводим получателя

        to_input_send = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div[1]/div/div[2]/input")
        to_input_send.send_keys(username)
        time.sleep(4)

        #выбираем получателя из списка

        direct_users = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div[2]").find_element_by_tag_name("button").click()
        time.sleep(random.randrange(2, 4))

        next_button = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[1]/div/div[2]/div/button").click()
        time.sleep(random.randrange(2, 4))

        #вводим сообщения

        send_message = browser.find_element_by_xpath("/html/body/div[1]/section/div/div[2]/div/div/div[2]/div[2]/div/div[2]/div/div/div[2]/textarea")
        send_message.clear()
        send_message.send_keys(message)
        time.sleep(random.randrange(2, 4))
        send_message.send_keys(Keys.ENTER)
        print(f"Сообщение для {username} успешно отправлено, поздравляем!!!:)")
        self.close_browser()



my_bot = instagramBot(username, password)
my_bot.login()
my_bot.send_direct_message("davromaniak", "Привет, я готов к работе!!!")
# my_bot.get_subscribe("https://www.instagram.com/davromaniak/")
