#!/usr/bin/python3
import argparse

parser = argparse.ArgumentParser(description='A test program.')
parser.add_argument("--f", help="from")
parser.add_argument("--t", help="to")
args = parser.parse_args()

import re
from datetime import datetime
import requests
import warnings
warnings.filterwarnings("ignore")

SEPARATE_STRING = '=================================================================='
key = "твой апи ключ"
now = datetime.now()
params = {"apikey": key,
          "format": "json",
          "from": None,
          "to": None,
          "lang": "ru_RU",
          "page": 1,
          "date": now.strftime("%Y-%m-%d"),
          "system": "esr"
          }

url = f"https://api.rasp.yandex.net/v3.0/search/"


def search_esr_code_by_name(station: str, name: str):
    print(SEPARATE_STRING)
    print('Ищем название')
    url = f"http://osm.sbin.ru/esr/search:{name}"

    response = requests.get(url)
    exp = r'<li>.+?</li>'

    matches = [i.replace("<li>", "").replace("</li>", "").replace("a href=./esr:", "").replace("</a>", "") for i in
               re.findall(exp, response.text)]
    if len(matches) == 0:
        print("Нет братан, ничего")
        print(SEPARATE_STRING)
        exit()
    else:
        print("Кароч вот че я нашел, пиши код станции и кайфуй")
        for index, i in enumerate(matches):
            print(index, i)
        a = input()
        try:
            match = matches[int(a)]
            numbers = re.search(r'\d+', match).group()
            params[station] = numbers
        except IndexError:
            params[station] = a

    print(SEPARATE_STRING)


if not (args.f and args.t):
    print("Велкам епта, куда плюнем? Вбиваешь откуда, куда, и я ищу тебе транспорт.")
    print("Откуда: вбиваешь ЕСР код станции, если не знаешь его просто пиши название попробуем найти")
    from_ = input()
    if from_.isdigit():
        params['from'] = from_  # апдейтим запрос
    else:
        search_esr_code_by_name(station='from', name=from_)
        # ищем и потом обновляем запрос

    print("Куда: вбиваешь ЕСР код станции, если не знаешь его просто пиши название попробуем найти")
    to_ = input()
    if to_.isdigit():
        params['to'] = to_  # апдейтим запрос
    else:
        search_esr_code_by_name(station='to', name=to_)
        # ищем и потом обновляем запрос
else:
    params['from'] = args.f
    params['to'] = args.t

response = requests.get(url, params=params, verify=False)
res = response.json()

search = res.get('search')
if search:
    print(f"Дата:{search['date']}\nОткуда:{search['from']['title']}\nКуда:{search['to']['title']}")
else:
    print(res)
    print("Все хуйня сори")
    exit()
print('=================== список доступных рейсов ======================')
segments = res.get('segments')
if segments:
    for i in segments:
        departure = i.get('departure')
        if departure:
            if datetime.fromisoformat(departure).timestamp() < now.timestamp():
                continue
            print(f'Отправление: {datetime.fromisoformat(departure).strftime("%H:%M")}')
        arrival = i.get('arrival')
        print(f'Прибытие: {datetime.fromisoformat(arrival).strftime("%H:%M")}')

        duration = i.get('duration')
        if duration:
            print(f'Продолжительность: {duration / 60} мин.')
        tickets_info = i.get('tickets_info')
        if tickets_info:
            try:
                info = tickets_info["places"]
                for j in info:
                    print(f'Стоимость билета: {j["price"]["whole"]} {j["currency"]}')
            except:
                print(tickets_info)
        thread = i.get('thread')
        if thread:
            print(f"Вид транспорта: {thread.get('transport_type')}")
            print(f"Название нитки: {thread.get('short_title')}")
        else:
            print(thread)
        print(SEPARATE_STRING)
