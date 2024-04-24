import os
import random

import pandas as pd
import json
import time as t1

import requests
from bs4 import BeautifulSoup
import csv

from user_agent_list import user_agent_list
requests.adapters.DEFAULT_RETRIES = 10  # 增加重连次数

cookies = {
    'XSRF-TOKEN': 'JFDNuL_v0VwXIo55Gcmr4mjo',
    'SUB': '_2A25ISNAHDeRhGeFN6FAZ8i7Ezz-IHXVrJG3PrDV8PUNbmtB-LROtkW9NQCtG7UGY04pxEiDMoC4Dw5q3o6yqI-Gg',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WhEuTqkNYcDTOyIDQmMpSYg5JpX5KzhUgL.FoM0e0zReo5RShe2dJLoIp97dNW7i--fi-z7iKysi--Xi-zRi-8F',
    'WBPSESS': 'i_AOz0LvidmiqM0KH1vJS_2TbSzEebEfwiwvocJJgCmvDILFkjcgaXIOWUP8Om5xktgYCTHaTWbX',
    '_s_tentry': '-',
    'Apache': '3433530080542.02.1699520578911',
    'SINAGLOBAL': '3433530080542.02.1699520578911',
    'ULV': '1699520578926:1:1:1:3433530080542.02.1699520578911:',
    'SSOLoginState': '1699520599',
    'SCF': 'AiQugWU3ZMnuVjwDLwGqaKamSi5Hn3FfE0ois5IerC0iN9ItlHLWHCVKOBl21OBpJWZyjbsRvgDG0sMNQklZhzE.',
    'ALF': '1702134067',
    'PC_TOKEN': '0e92f044f2'
}

proxies = {
    "http": None,
    "https": None,
}


headers = {
    'Connection': 'close',
    'User-Agent': random.choice(user_agent_list)
}


def get_file_names(folder):
    file_names = []
    for file_name in os.listdir(folder):
        file_names.append(file_name)
    return file_names


def get_title_url(time):
    filepath = 'URL/' + time
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    info = json.loads(data)
    titles = []
    for content in info:
        titles.append(content['title'])
    times = [time[0:10]] * len(titles)

    f.close()
    return times, titles


def get_info(url, max_attempts=10):
    """
    Function to repeatedly try fetching content from a URL using requests.get.
    It attempts up to a maximum number of times specified by max_attempts.

    Args:
    url (str): The URL to fetch content from.
    max_attempts (int): The maximum number of attempts to try fetching the content. -1 means unlimited.

    Returns:
    str: The content of the webpage if successful, else None.
    """
    attempts = 0
    t1.sleep(1)
    while attempts < max_attempts or max_attempts == -1:
        try:
            response = requests.get(url, cookies=cookies, verify=True, headers=headers, proxies=proxies)
            # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text

        except requests.RequestException as e:
            print(f"Attempt {attempts + 1} failed: {e}")
            t1.sleep(2)
            attempts += 1
    return None


if __name__ == '__main__':
    folder = 'URL'
    times = get_file_names(folder)

    time_list = []
    title_list = []

    for t in times:
        time, title = get_title_url(t)
        time_list.extend(time)
        title_list.extend(title)

    print(len(time_list))
    print(len(title_list))

    with open('data1000.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        index = list(range(0, len(time_list)))

        introduction = []
        for i, title in enumerate(title_list):
            print(index[i], time_list[i])
            rs = requests.session()
            rs.keep_alive = False  # 关闭多余连接
            url2 = f'https://s.weibo.com/weibo?q=%23{title}%23'
            print(url2)
            # s = rs.get(url2, cookies=cookies, verify=True, headers=headers, proxies=proxies)
            # s.encoding = 'utf-8'
            # stext = s.text
            stext = get_info(url2)
            ssoup = BeautifulSoup(stext, 'html.parser')
            divs = ssoup.find('div', {'class': 'card card-topic-lead s-pg16'})
            if divs is None:
                introduction.append(''.strip('"'))
            if divs is not None:
                introduction.append(divs.get_text().strip().strip('"'))
            print(introduction[i])

            data = [time_list[i], title_list[i], introduction[i]]
            writer.writerow(data)

        print(len(introduction))
        file.close()

    data = {
        'Date': time_list,
        'Title': title_list,
        'Introduction': introduction
    }
    df = pd.DataFrame(data)
    df.to_csv("hotband_detail.csv", index=True, encoding='utf-8')
