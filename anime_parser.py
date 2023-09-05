from bs4 import BeautifulSoup as Soup
import requests
from base64 import b64decode
import json
import html5lib
from time import sleep

token = '447d179e875efe44217f20d1ee2146be'
def get_responce_200(url,headers):
    response = requests.get(url=url,headers=headers)
    if response.status_code != 200:
            while response.status_code != 200:
                sleep(0.5)
                response = requests.get(url=url,headers=headers)
    return response

def get_shiki_popular(all=False):
    #возвращает словарь с онгоингами
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition Yx GX)",
        }
    shiki_popular_url = f'https://shikimori.me/animes/kind/tv/status/popular'
    try:
        
        response = requests.get(url=shiki_popular_url,headers=headers)
        response.raise_for_status()
    except:
        sleep(0.5)
        return get_shiki_popular()
    soup = Soup(response.text, 'html5lib')
    now_year = int(soup.find('span', class_='date').text.split('-')[1])
    shiki_popular_url = f'https://shikimori.me/animes/kind/tv/status/released,latest,ongoing/season/{now_year},{now_year-1}/score/6/order-by/popularity'
    response = get_responce_200(shiki_popular_url,headers)
   
    
    soup = Soup(response.text, 'html5lib')    
    pages = int(soup.find('span', class_='link-total').text.strip())
    result = {}
    if not all:
        pages = 3
    for x in range(1,pages+1):
        shiki_popular_url = f'https://shikimori.me/animes/kind/tv/status/released,latest,ongoing/season/{now_year},{now_year-1}/score/6/order-by/popularity/page/{x}'
        response = get_responce_200(shiki_popular_url,headers)
        soup = Soup(response.text, 'html5lib')
        ids = [x['id'] for x in soup.find_all('article')]
        images = [x['srcset'].split(' ')[0] for x in soup.find_all('img')]
        title = []
        titles = soup.find_all('article')
        for x in titles:
            check = x.find('span', class_='name-ru')
            if check:
                title+=[check.text.strip()]
            elif x.find('img')['alt']:
                title+=[x.find('img')['alt']]
            else:
                title+=['без названия']
        for id,image,titl in zip(ids,images,title):
            result[id] = [image,titl] 
    return result

def get_shiki_ongoing():
    #возвращает словарь с онгоингами
    headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition Yx GX)",
        }
    shiki_ongoing_url = f'https://shikimori.me/animes/kind/tv/status/ongoing'
    try:
        response = requests.get(url=shiki_ongoing_url,headers=headers)
        response.raise_for_status()
    except:
        sleep(0.5)
        return get_shiki_ongoing()
    soup = Soup(response.text, 'html5lib')
    now_year = soup.find('span', class_='date').text.split('-')[1]
    pages = int(soup.find('span', class_='link-total').text.strip())
    result = {}
    
    for x in range(1,pages+1):
        shiki_ongoing_url = f'https://shikimori.me/animes/kind/tv/status/ongoing/season/{now_year}/page/{x}'
        response = get_responce_200(shiki_ongoing_url,headers)
        soup = Soup(response.text, 'html5lib')
        ids = [x['id'] for x in soup.find_all('article')]
        images = [x['srcset'].split(' ')[0] for x in soup.find_all('img')]
        title = []
        titles = soup.find_all('article')
        for x in titles:
            check = x.find('span', class_='name-ru')
            if check:
                title+=[check.text.strip()]
            elif x.find('img')['alt']:
                title+=[x.find('img')['alt']]
            else:
                title+=['без названия']
        for id,image,titl in zip(ids,images,title):
            result[id] = [image,titl]   
    return result

def convert_char(char: str):
    low = char.islower()
    alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if char.upper() in alph:
        ch = alph[(alph.index(char.upper())+13)%len(alph)]
        if low:
            return ch.lower()
        else:
            return ch
    else:
        return char

def convert(string: str):
    # Декодирование строки со ссылкой
    return "".join(map(convert_char, list(string)))

# отправляем запрос на получение ссылки и декодируем ее в рабочую ссылку на видео
def get_download_link_with_data(video_type: str, video_hash: str, video_id: str, seria_num: int):
    params={
        # Данные для теста: hash: "6476310cc6d90aa9304d5d8af3a91279"  id: 19850  type: video
        "hash": video_hash,
        "id": video_id,
        "quality":"720p",
        "type":video_type,
        "protocol": '',
        "host":"kodik.cc",
        "d":"kodik.cc",
        "d_sign":"9945930febce35101e96ce0fe360f9729430271c19941e63c5208c2f342e10ed",
        "pd":"kodik.cc",
        "pd_sign":"9945930febce35101e96ce0fe360f9729430271c19941e63c5208c2f342e10ed",
        "ref": '',
        "ref_sign":"208d2a75f78d8afe7a1c73c2d97fd3ce07534666ab4405369f4f8705a9741144",
        "advert_debug": True,
        "first_url": False,
    }

    data = requests.post('http://kodik.cc/gvi', params=params).json()
    url = data['links']['720'][0]['src']
    url = convert(data['links']['720'][0]['src'])
    try:
        return b64decode(url.encode())
    except:
        return str(b64decode(url.encode()+b'==')).replace("https:", '')
    

def get_shiki_serial_id(data):
    shiki_id = {}
    for name in data['results']:
        print(name)
        if 'shikimori_id' in name.keys() and 'last_episode' in name.keys():
            if name['title'] in shiki_id:
                continue
            shiki_id[name['title']] = name['shikimori_id']
   
    sorted_shiki = dict(sorted(shiki_id.items()))
    i = 1
    for name,number in sorted_shiki.items():
        print(i,name)
        i+=1
    select_user = int(input('выберите сезон - '))
    i = 1
    for name,shiki_id in sorted_shiki.items():
        if i == select_user:
            return (shiki_id)
        i+=1

def get_voice_id(data,id):
    voice_id = {}
    for name in data['results']:
        if 'shikimori_id' in name.keys() and name['shikimori_id'] == str(id):
            voice_id[name['translation']['id']] = [name['translation']['title'], name['last_episode']]
    i = 1
    for name,title in voice_id.items():
        print(i,title[0],'эпизодов - ',title[1])
        i+=1
    select_user = int(input('выберите озвучку - '))
    i = 1
    for name,title in voice_id.items():
        if i == select_user:
            print(name)
            return name
        i+=1
def get_seria_num(data,id,voice):
    for name in data['results']:
        if 'shikimori_id' in name.keys() and name['translation']['id'] == voice and name['shikimori_id'] == id:
            print("выберите серсию с 1 до ",name['last_episode'])
            select_user = input()
            return select_user
        
#собирает все вместе и выдает готовую ссылку        
def get_link_anime(search_name):
    payload = {
            "token": '447d179e875efe44217f20d1ee2146be',
            "title": search_name
        }
    url = "https://kodikapi.com/search"
    data = requests.post(url, data=payload).json()
    print(data)
    id = get_shiki_serial_id(data) # шикимори айди
    translation_id = get_voice_id(data,id) # translation_id: #Id озвучки
    seria_num = get_seria_num(data,id,translation_id)
    data = requests.get(f'https://kodikapi.com/get-player?title=Player&hasPlayer=false&url=https%3A%2F%2Fkodikdb.com%2Ffind-player%3FshikimoriID%3D{id}&token={token}&shikimoriID={id}')
    
    url = json.loads(data.text)['link']
    data = requests.get(f'https:{url}').text
    soup = Soup(data, 'html5lib')
    
    # находим нужную озвучку и ее данные
    container = soup.find('div', {'class': 'serial-translations-box'}).find('select')
    media_hash = None
    media_id = None
    for translation in container.find_all('option'):
        if translation.get_attribute_list('data-id')[0] == str(translation_id): #Id озвучки
            media_hash = translation.get_attribute_list('data-media-hash')[0]
            media_id = translation.get_attribute_list('data-media-id')[0]
            break
    
    url = f'https://kodik.info/serial/{media_id}/{media_hash}/720p?d=kodik.cc&d_sign=9945930febce35101e96ce0fe360f9729430271c19941e63c5208c2f342e10ed&pd=kodik.info&pd_sign=09ffe86e9e452eec302620225d9848eb722efd800e15bf707195241d9b7e4b2b&ref=&ref_sign=208d2a75f78d8afe7a1c73c2d97fd3ce07534666ab4405369f4f8705a9741144&advert_debug=true&min_age=16&first_url=false&season=1&episode={seria_num}'
    data = requests.get(url).text
    soup = Soup(data, 'html5lib')
    hash_container = soup.find_all('script')[4].text

    video_type = hash_container[hash_container.find('.type = \'')+9:]
    video_type = video_type[:video_type.find('\'')]
    video_hash = hash_container[hash_container.find('.hash = \'')+9:]
    video_hash = video_hash[:video_hash.find('\'')]
    video_id = hash_container[hash_container.find('.id = \'')+7:]
    video_id = video_id[:video_id.find('\'')]

    download_url = str(get_download_link_with_data(video_type, video_hash, video_id, '4')).replace("https://", '')
    download_url = download_url[2:-26]
    print(f'https:{download_url}720.mp4')

def get_url_data(url: str, headers: dict = None, session=None):
    return requests.get(url, headers=headers).text

def get_shiki_data(id: str):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition Yx GX)",
    }
    url = "https://shikimori.me/animes/"+id
    data = get_url_data(url, headers)
    soup = Soup(data, 'html5lib')
    try:
        if soup.find('img', {'class': 'image'}).get_attribute_list('src')[0] == "/images/static/page_moved.jpg":
            # Проверка на перемещение страницы
            new_id = soup.find("a").get_attribute_list('href')[0]
            new_id = new_id[new_id.rfind('/'):]
            return get_shiki_data(new_id)
        else:
            # Страница не перемещена
            raise FileExistsError
    except:
        try:
            if soup.find("div", {'class': 'b-age_restricted'}) == None:
                # Проверка на возрастные ограничения
                soup.find("div", {'class': 'c-poster'}).find('picture').find('img')
            else:
                raise PermissionError
        except PermissionError:
            title = f"18+ (Shikimori id: {id})"
            image = 'https://i.pinimg.com/originals/72/dc/2c/72dc2cfe0dd432c11502634450ff4ad0.png'
            p_data = "Неизвестно"
            dtype = "Неизвестно"
            dstatus = "Неизвестно"
            ddate = "Неизвестно"
            score = "Неизвестно"
        except:
            # Сервер не допукает слишком частое обращение
            sleep(0.5)
            return get_shiki_data(id)
        else:
            title = soup.find('header', {'class': 'head'}).find('h1').text
            try:
                image = soup.find("div", {'class': 'c-poster'}).find('div').get_attribute_list('data-href')[0]
            except:
                try:
                    image = soup.find("div", {'class': 'c-poster'}).find('picture').find('img').get_attribute_list('src')[0]
                except:
                    image = 'https://i.pinimg.com/originals/72/dc/2c/72dc2cfe0dd432c11502634450ff4ad0.png'
            try:
                descript = soup.find('div', class_="b-text_with_paragraphs").text
            except:
                descript = "нет описания"
            p_data = soup.find('div', {'class': 'b-entry-info'}).find_all('div', {'class': 'line-container'})
            dtype = p_data[0].find('div', {'class': 'value'}).text
            dstatus = soup.find('div', {'class': 'b-entry-info'}).find('span', {'class': 'b-anime_status_tag'}).get_attribute_list('data-text')[0]
            ddate = soup.find('div', {'class': 'b-entry-info'}).find('span', {'class': 'b-anime_status_tag'}).parent.text[2:].strip()
            try:
                score = soup.find('div', {'class': 'text-score'}).find('div').text
            except:
                score = "0"
                
        return {
            'title': title,
            'image': image,
            'descript':descript,
            'type': dtype,
            'date': ddate,
            'status': dstatus,
            'score': score
        }

