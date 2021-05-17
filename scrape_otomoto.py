from bs4 import BeautifulSoup, NavigableString
import requests
import pandas as pd
import re
import time
from datetime import datetime
import locale
import multiprocessing as mp
import concurrent.futures

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


'''
Webscrapes all otomoto car offers and saves output csv files to /scraped_data folder
'''


def get_url(brand, model=None):
    template = "https://www.otomoto.pl/osobowe/{}/?search%5Border%5D=created_at_first%3Adesc&search%5Bbrand_program_id%5D%5B0%5D=&search%5Bcountry%5D="
    if model:
        url = template.format(f"{brand}/{model}")
    else:
        url = template.format(f"{brand}")
    return url


def get_car_brands():
    """
    return list of tuples (brand_name, number of brand offers)
    """
    main_http = requests.get("https://www.otomoto.pl/osobowe/")
    soup = BeautifulSoup(main_http.text, 'html.parser')

    brand_filter = soup.find_all("div", {"class": "filter-item rel"})[1]
    brand_select = brand_filter.find('select')

    car_brands = list()
    for l in brand_select.contents[2:]:
        if isinstance(l, NavigableString):
            continue
        brand_count = re.findall(r"[0-9]+", l.text)[0]
        brand_count = int(brand_count)
        brand_name = l['value']
        car_brands.append((brand_name, brand_count))

    # brand warszawa must be search as marka_warszawa
    car_brands = [('marka_warszawa', count) if brand == 'warszawa' else (
        brand, count) for brand, count in car_brands]

    return car_brands


def get_brand_models(brand, web_driver):
    url = f"https://www.otomoto.pl/osobowe/{brand}/"
    web_driver.get(url)
    soup = BeautifulSoup(web_driver.page_source, 'html.parser')

    model_filter = soup.find_all("div", {"class": "filter-item rel"})[1]
    model_select = model_filter.find('select')

    car_models = set()
    for l in model_select.contents:
        if isinstance(l, NavigableString):
            continue
        car_models.add(l['value'])
    return list(filter(None, car_models))


def get_webscrap_list():
    """
    Otomoto displays only 16000 offers per selected option,
    so we need to split searched settings according to this

    return list of (brand,model) according to which page will be scraped
    """

    to_scrap = list()
    brands = get_car_brands()

    web_driver = webdriver.Chrome(ChromeDriverManager().install())
    threshold = 500 * 32  # otomoto allows to explore ma 500 pages 32 offers each

    for brand, count in get_car_brands():
        if count <= threshold:
            to_scrap.append((brand, None))
            continue

        # if brand have more than 16000 offers than split it to single models
        brand_models = get_brand_models(brand, web_driver)
        for model in brand_models:
            to_scrap.append((brand, model))

    return to_scrap


def convert_date(date_string):
    """
    Get date in string and format it to dd/mm/yyyy.
    """
    locale.setlocale(locale.LC_ALL, 'en_US')
    month_dict = {'stycznia': 'January',
                  'lutego': 'February',
                  'marca': 'March',
                  'kwietnia': 'April',
                  'maja': 'May',
                  'czerwca': 'June',
                  'lipca': 'July',
                  'sierpnia': 'August',
                  'września': 'September',
                  'października': 'October',
                  'listopada': 'November',
                  'grudnia': 'December'}

    for key in month_dict.keys():
        date_string = date_string.replace(key, month_dict[key])
    date = datetime.strptime(date_string, "%H:%M, %d %B %Y")
    return date.strftime("%d/%m/%Y")


def get_offer_params(url):
    """
    Scrape variables from single offer based on url
    """
    http = requests.get(url)
    soup = BeautifulSoup(http.text, 'html.parser')

    params_dict = dict()
    try:
        params_dict["URL"] = url

        # ID
        ID_num = soup.find(
            "span", {"class": "offer-meta__value", "id": "ad_id"}).text
        params_dict["ID"] = ID_num

        # offer add date
        add_date = soup.find("span", {"class": "offer-meta__value"}).text
        params_dict['date'] = convert_date(add_date)

        # price
        price = soup.find("span", {"class": "offer-price__number"}).text
        currency = soup.find("span", {"class": "offer-price__currency"}).text
        price_value = price.replace(currency, '').replace(' ', '')
        params_dict["Price"] = int(price_value)
        params_dict["Currency"] = currency

        # location
        location = soup.find(
            "span", {"class": "seller-box__seller-address__label"}).text.strip()
        params_dict["Location"] = location

        # car parameters
        params_lists = soup.find_all("ul", {"class": "offer-params__list"})
        for params_list in params_lists:
            params_items = params_list.find_all(
                "li", {"class": "offer-params__item"})

            for l in params_items:
                if isinstance(l, NavigableString):
                    continue
                label = l.find("span").text.strip()
                value = l.find(
                    "div", {"class": "offer-params__value"}).text.strip()
                params_dict[label] = value

        # Features
        car_features_list = list()
        offer_features = soup.find_all("ul", {"class": "offer-features__list"})
        for features in offer_features:
            features_items = features.find_all(
                "li", {"class": "offer-features__item"})
            for l in features_items:
                car_features_list.append(l.text.strip())
        params_dict["Features"] = car_features_list
    except Exception as err:
        print(f"Exception: {url} - {err}")
        return None


    final_keys = ['ID', 'Price', 'Currency', 'Stan', 'Marka pojazdu', 'Model pojazdu', 'Wersja', 'Generacja', 'Rok produkcji', 'Przebieg', 'Moc',
                  'Pojemność skokowa', 'Rodzaj paliwa', 'Emisja CO2', 'Napęd', 'Skrzynia biegów', 'Typ', 'Liczba drzwi', 'Kolor', 'Kraj pochodzenia',
                  'Pierwszy właściciel', 'Pierwsza rejestracja', 'date', 'Location', 'Features', 'URL']
    final_dict = {key: params_dict[key] if (
        key in params_dict) else "" for key in final_keys}
    return final_dict


def scrape_model_mp(brand, model=None):
    offers_params = list()

    url = get_url(brand, model)
    while True:
        print(url)
        http = requests.get(url)
        soup = BeautifulSoup(http.text, 'html.parser')

        offers = soup.find("div", {"class": "offers list"}).find_all("article")

        for offer in offers:
            try:
                offer_url = offer['data-href']
            except Exception as err:
                print(f"Exception: {err}")
                continue

            offer_params = get_offer_params(offer_url)
            if offer_params:
                offers_params.append(offer_params)

        if not soup.find("li", {"class": "next abs"}):
            print(f"saving {brand}-{model}.csv")
            df = pd.pandas.DataFrame.from_records(offers_params)
            df.to_csv(f"./scraped_data/{brand}-{model}.csv", index=False)
            return
        else:
            url = soup.find("li", {"class": "next abs"}).a['href']


def scrape_otomoto():
    print("Collecting webscrap list")
    webscrap_list = get_webscrap_list()

    n_cpu = mp.cpu_count()
    print(f"Webscraping using {n_cpu} threads")
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_cpu) as executor:
        executor.map(lambda p: scrape_model_mp(*p), webscrap_list)