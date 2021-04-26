'''
MIT License

Copyright (c) 2020 fkubota

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import time
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary
import urllib.parse


def japanize(from_text: str) -> str:
    '''
    ref.
    https://qiita.com/fujino-fpu/items/e94d4ff9e7a5784b2987
    https://github.com/fkubota/Carrier-Owl/blob/bae2c1e54061eb0b0d457b3fdf1855dafdf0fd56/src/carrier_owl.py
    '''

    sleep_time = 1

    # urlencode
    from_text = urllib.parse.quote(from_text)

    # url作成
    url = 'https://www.deepl.com/translator#en/ja/' + from_text

    # ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')

    # ブラウザーを起動
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)
    driver.implicitly_wait(10)  # 見つからないときは、10秒まで待つ

    for i in range(30):
        # 指定時間待つ
        time.sleep(sleep_time)
        html = driver.page_source
        to_text = get_text_from_page_source(html)

        if to_text:
            break

    # ブラウザ停止
    driver.quit()
    return to_text


def get_text_from_page_source(html: str) -> str:
    soup = BeautifulSoup(html, features='lxml')
    target_elem = soup.find(class_="lmt__translations_as_text__text_btn")
    text = target_elem.text
    return text
