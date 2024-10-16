import osrm
from googlesearch import search
import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
from selenium import webdriver as wd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pathlib import Path
from tqdm import tqdm
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import random
import time
from pathlib import Path
import shutil
from copy import deepcopy



coordinates = [[55.7522, 37.6156], [55.7887, 49.1221], [55.3949, 43.8399]]
tgt_coord = [55.7254, 52.4112]


class GeoProcessor:
    def __init__(self):
        self.osrm_client = osrm.Client(host='http://router.project-osrm.org')
        self.headers = Headers(
                os="mac",  # Generate ony Windows platform
                headers=True  # generate misc headers
        ).generate()
        
        self.options = wd.ChromeOptions()
        self.options.add_argument("--enable-javascript")
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # Скрываем признак автоматизации
        self.options.add_argument("--disable-infobars")  # Отключаем инфо-бар Selenium
        self.options.add_argument("--start-maximized")  # Полноэкранный режим для имитации реального пользователя
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36")  # Задаем реальный User-Agent

        # Отключаем дополнительные всплывающие окна и уведомления
        prefs = {"profile.default_content_setting_values.notifications": 2, 
                "profile.default_content_setting_values.geolocation": 2}
        self.options.add_experimental_option("prefs", prefs)

    def distance(self, from_coords, tgt_coords):
        """ (широта, долгота) """
        coordinates_osrm = [from_coords[::-1], tgt_coords[::-1]] # lat, lon
        osrm_response = self.osrm_client.route(coordinates=coordinates_osrm, overview=osrm.overview.full)
        dist_osrm = osrm_response.get('routes')[0].get('distance')/1000 # in km
        print('distance using OSRM: ', dist_osrm)
        return dist_osrm
    
    def google_address(self, addr: str, num_results=5, proxy=None, banned=False, captcha_sleep=2):
        if banned:
            res = list(self.search_selenium(addr, num_results=num_results, captcha_sleep=captcha_sleep))
        else:
            res = list(search(addr, sleep_interval=1, num_results=num_results, proxy=proxy))
        return res
    

    def search_selenium(self, address: str, num_results=5, captcha_sleep=2):
        options = deepcopy(geopc.options)
        options.page_load_strategy = 'eager'

        browser = wd.Chrome(options=options)
        browser.get('https://www.google.com/search')
        textarea = browser.find_element(By.XPATH, "/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea")
        textarea.send_keys(address)
        textarea.send_keys(Keys.ENTER)
        time.sleep(captcha_sleep)
        html = browser.page_source
        soup = BeautifulSoup(html, "html.parser")
        return self.parse_soup(soup, num_results=num_results)
            
    def parse_soup(self, soup, num_results=5):
        fetched_results = 0
        while fetched_results < num_results:
            result_block = soup.find_all("div", attrs={"class": "g"})
            new_results = 0  # Keep track of new results in this iteration

            for result in result_block:
                # Find link, title, description
                link = result.find("a", href=True)
                title = result.find("h3")
                description_box = result.find("div", {"style": "-webkit-line-clamp:2"})

                if link and title and description_box:
                    description = description_box.text
                    fetched_results += 1
                    new_results += 1
                    # if advanced:
                        # yield SearchResult(link["href"], title.text, description)
                    # else:
                    yield link["href"]

                if fetched_results >= num_results:
                    break  # Stop if we have fetched the desired number of results

            if new_results == 0:
                break


    def parse_freicon(self, freicon_url: str='https://online.freicon.ru/info/stations/799101'):
        """ If alta not in urls """
        try:
            browser = wd.Chrome(options=self.options)
            browser.get(freicon_url)
            lat = float(browser.find_element(By.XPATH, '/html/body/app-root/app-admin-layout/div/main/app-info/app-station-details/section/div[1]/div[13]/div[1]/span').text)
            lon = float(browser.find_element(By.XPATH, '/html/body/app-root/app-admin-layout/div/main/app-info/app-station-details/section/div[1]/div[13]/div[2]/span').text)
            return lat, lon
        except:
            return None
    
    def parse_alta(self, alta_url: str='https://www.alta.ru/railway/station/81200/'):
        """ More prioitised than freicon.ru"""
        try:
            soup = BeautifulSoup(requests.get(alta_url, headers=self.headers).text, 'html.parser')
            lon = float(soup.find('div', class_='dib pl-10').text.split(':')[1].strip())
            lat = float(soup.find('div', class_='dib pr-10').text.split(':')[1].strip())
            lat, lon
            return lat, lon
        except:
            return None
    
    def parse_yandex(self, ya_url: str='https://yandex.ru/maps/970/novorossiysk/house/krasnaya_ulitsa_108/Z04YcQVgSUYDQFpufXt2dHlhZA==/', soup=None):
        """ Best if object is not a railway station """
        try:
            if soup is None:
                soup = BeautifulSoup(requests.get(ya_url, headers=self.headers).text, 'html.parser')
            lat, lon = map(float, map(str.strip, soup.find('div', class_='toponym-card-title-view__coords-badge').text.split(',')))
            return lat, lon
        except:
            return None
        
    def parse_yandex_final(self, ya_url: str='https://yandex.ru/maps/org/otdeleniye_pochtovoy_svyazi_644040/170954544743/'):
        try:
            browser = wd.Chrome(options=self.options)
            browser.get(ya_url)

            num_try = 0
            while ('?ll=' not in self.basename) and (num_try < 5):
                time.sleep(0.2)
                self.basename = Path(browser.current_url).name
                num_try += 1
            lon = self.basename.split('ll=')[1].split('%2C')[0]
            lat = self.basename.split('%2C')[1].split('&')[0]
            try:
                lon = float(lon)
                lat = float(lat)
            except:
                pass
            return lat, lon
        except:
            return None
    
    def parse_2gis(self, gis_url: str='https://2gis.ru/noyabrsk/search/%D0%A2%D1%80%D1%83%D0%B1%D0%BD%D0%B0%D1%8F%20%D0%B1%D0%B0%D0%B7%D0%B0'):
        """
            https://2gis.ru/krasnodar/directions/points/%7C39.086777%2C45.043662%3B3237597887345181

            template: %7C{lon}%2C{lat}%{hash}'
            swap => lat, lon
        """
        try:
            browser = wd.Chrome(options=self.options)
            browser.get(gis_url)
            try:
                elem = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div[1]/div[2]/div[3]/a')
            except:
                browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div/div/div[2]/div/div/div/div[2]/div[2]/div[1]/div/div/div/div[2]/div/div/div').click()
                elem = browser.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div[1]/div[1]/div[3]/a')
            elem.click()
            self.basename = Path(browser.current_url).name
            while '%7C' not in self.basename:
                time.sleep(0.2)
                self.basename = Path(browser.current_url).name
            lon = float(self.basename.split('%7C')[1].split('%2C')[0])
            lat = float(self.basename.split('%2C')[1].split('%')[0])
            return lat, lon
        except:
            return None
    
    def network_sleep(self, flag, delay) -> None:
        if flag:
            time.sleep(delay)

    def try_parse_by_one(self, idx, pattern, parsing_func, exist_check, stage_delay, matrix, urls, network_busy):
        """ Попытаться распарсить url соответствующим методом """
        if exist_check[pattern]:
            network_busy |= True
            cur_urls = np.array(urls)[matrix[idx]].tolist()
            for cur_url in cur_urls:
                res = parsing_func(cur_url)
                if res is not None:
                    return res, exist_check, pattern
                
        self.network_sleep(network_busy, stage_delay)
        return network_busy

    def process(self, addr, num_results=10, google_delay=2, stage_delay=2, proxy=None, banned=False, captcha_sleep=2):
        """
        1. Если есть alta, то альта
            если она none, то freicon если есть
                если none, то yandex
                    если none то 2gis => далее none тк none
        2. Если нет alta, есть freicon, то freicon
            если none, то yandex
                если none то 2 gis => далее none тк none
        3. если нет ни alta ни freicon, то yandex
            если none то 2gis => далее none тк none

        :return: returned value must be in ['banned', 'nan', (lat, lon)]
        """
        self.patterns = ['yandex.ru', '2gis.ru', 'alta.ru', 'freicon.ru']
        self.funcs = [self.parse_yandex, self.parse_2gis, self.parse_alta, self.parse_freicon]

        try:
            urls = self.google_address(addr=addr, num_results=num_results, proxy=proxy, banned=banned, captcha_sleep=captcha_sleep)
            matrix = np.array([[pattern in url.lower() for url in urls] for pattern in self.patterns])

            if (len(urls) < 2) or (matrix.sum() < 1):
                time.sleep(google_delay)
                
                urls = self.google_address(addr=addr[:int(len(addr)/2)], num_results=num_results, proxy=proxy, banned=banned, captcha_sleep=captcha_sleep)
                matrix = np.array([[pattern in url.lower() for url in urls] for pattern in self.patterns])
                if (matrix.sum() < 1):
                    time.sleep(google_delay)
                    urls = self.google_address(addr=addr[int(len(addr)/2):], num_results=num_results, proxy=proxy, banned=banned, captcha_sleep=captcha_sleep)
                    matrix = np.array([[pattern in url.lower() for url in urls] for pattern in self.patterns])
                    if (matrix.sum() < 1):
                        time.sleep(google_delay)
                        sp = addr.split()
                        urls = self.google_address(addr=' '.join(sp[2:len(sp)-1]), num_results=num_results, proxy=proxy, banned=banned, captcha_sleep=captcha_sleep)
                        matrix = np.array([[pattern in url.lower() for url in urls] for pattern in self.patterns])
                        if (matrix.sum() < 1):
                            self.matrix = matrix
                            self.urls = urls
                            return 'nan'
        except Exception as e:
            print(f'Probably, banned! {e}')
            return 'banned'

        exist_check = {k:v for k, v in zip(self.patterns, matrix.sum(axis=1).tolist())}
        network_busy = False
        list_enumerate = list(enumerate(zip(self.patterns, self.funcs)))

        # shuffle `list_enumerate` in right order and execute
        for idx, (pattern, parsing_func) in list_enumerate[2:-1] + list_enumerate[:2] + [list_enumerate[-1]]:
            result = self.try_parse_by_one(idx, pattern, parsing_func, exist_check, stage_delay, matrix, urls, network_busy)
            if isinstance(result, tuple):
                return result
            network_busy = result

        self.matrix = matrix
        self.urls = urls
        return 'nan'
    
    def init_browser_ymaps(self):
        ya_home_url = 'https://yandex.ru/maps'
        browser = wd.Chrome(options=self.options)
        browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        browser.get(ya_home_url)
        time.sleep(10)
        return browser

    def process_v2(self, addr, browser=None):
        ya_home_url = 'https://yandex.ru/maps'
        if browser is None:
            browser = wd.Chrome(options=self.options)
            browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            browser.get(ya_home_url)
            time.sleep(10)
        results = 'init'
        try:
            elem = browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Поиск мест и адресов"]')
            elem.send_keys(addr)
            # for char in addr:
            #     elem.send_keys(char)
            #     time.sleep(random.uniform(0.1, 0.5))  # Случайная задержка

            elem.send_keys(Keys.ENTER)

            # Ожидаем загрузку результатов с рандомной задержкой
            time.sleep(random.uniform(1, 4))

            # Получаем HTML код страницы
            html = browser.page_source
            soup = BeautifulSoup(html, "html.parser")

            # Парсим результат
            result_v1 = self.parse_yandex(soup=soup)
            if result_v1 is None:
                # print('Parsing v2 and nan')
                try:
                    route = browser.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[10]/div[1]/div[1]/div[1]/div/div[1]/div/div/div[3]/div[3]/div/div[7]/div/div/div/div/div/div[1]/div/button')
                    route.click()
                except KeyboardInterrupt:
                    return results
                except:
                    try:
                        route = browser.find_element(By.CSS_SELECTOR, 'input[placeholder="Поиск мест и адресов"]')
                        route.click()
                        time.sleep(random.uniform(0.1, 0.3))
                        html = browser.page_source
                        soup = BeautifulSoup(html, "html.parser")
                        s = soup.find('li', class_='search-snippet-view')
                        divs = s.findAll('div')
                        for div in divs:
                            if div.has_attr('data-coordinates'):
                                results = ','.join(div['data-coordinates'].split(',')[::-1])
                            break
                        # time.sleep(random.uniform(1, 3))
                        try:
                            clear_button = browser.find_element(By.CSS_SELECTOR, "button[aria-label='Закрыть']")
                            clear_button.click()
                            # print('go back')
                        except KeyboardInterrupt:
                            return results
                        except:
                            # print('go back failed')
                            pass
                    except KeyboardInterrupt:
                        return results
                    except:
                        """ возможно вышел лист адресов """
                        try:
                            html = browser.page_source
                            soup = BeautifulSoup(html, "html.parser")
                            s = soup.find('li', class_='search-snippet-view')
                            divs = s.findAll('div')
                            for div in divs:
                                if div.has_attr('data-coordinates'):
                                    results = ','.join(div['data-coordinates'].split(',')[::-1])
                                break
                            # print('closing addr')
                            # time.sleep(random.uniform(0.5, 4))
                            clear_button = browser.find_element(By.CSS_SELECTOR, "button[aria-label='Закрыть']")
                            clear_button.click()
                            # time.sleep(random.uniform(0.5, 4))
                        except:
                            # print(f'Не кликнулось, {addr=}')
                            try:
                                clear_button = browser.find_element(By.CSS_SELECTOR, "button[aria-label='Закрыть']")
                                clear_button.click()
                            except:
                                # print('WARNING: НЕ СРАБОТАЛО ЗАКРЫТИЕ')
                                pass
                            results = 'nan'
                    
            else:
                # time.sleep(random.uniform(0.5, 4))
                clear_button = browser.find_element(By.CSS_SELECTOR, "button[aria-label='Закрыть']")
                clear_button.click()
                # time.sleep(random.uniform(0.5, 4))
                results = result_v1
            # print(f'{results=}')
            time.sleep(random.uniform(1, 2.5))
        except KeyboardInterrupt:
            return results
        return results
    
if __name__ == '__main__':
    geopc = GeoProcessor()