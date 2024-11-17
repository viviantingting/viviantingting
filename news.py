'''
# 作者: 112121931 林智鴻
# 描述: 自由時報區域新聞爬虫程式
'''

import requests
from bs4 import BeautifulSoup
from flask import render_template

# 定義地點選項
locations = {
    '臺北市': 'https://news.ltn.com.tw/list/breakingnews/Taipei',
    '新北市': 'https://news.ltn.com.tw/list/breakingnews/NewTaipei',
    '桃園市': 'https://news.ltn.com.tw/list/breakingnews/Taoyuan',
    '臺中市': 'https://news.ltn.com.tw/list/breakingnews/Taichung',
    '臺南市': 'https://news.ltn.com.tw/list/breakingnews/Tainan',
    '高雄市': 'https://news.ltn.com.tw/list/breakingnews/Kaohsiung',
    '基隆市': 'https://news.ltn.com.tw/list/breakingnews/Keelung',
    '新竹市': 'https://news.ltn.com.tw/list/breakingnews/Hsinchu',
    '嘉義市': 'https://news.ltn.com.tw/list/breakingnews/Chiayi',
    '新竹縣': 'https://news.ltn.com.tw/list/breakingnews/HsinchuCounty',
    '苗栗縣': 'https://news.ltn.com.tw/list/breakingnews/Miaoli',
    '彰化縣': 'https://news.ltn.com.tw/list/breakingnews/Changhua',
    '南投縣': 'https://news.ltn.com.tw/list/breakingnews/Nantou',
    '雲林縣': 'https://news.ltn.com.tw/list/breakingnews/Yunlin',
    '嘉義縣': 'https://news.ltn.com.tw/list/breakingnews/ChiayiCounty',
    '屏東縣': 'https://news.ltn.com.tw/list/breakingnews/Pingtung',
    '宜蘭縣': 'https://news.ltn.com.tw/list/breakingnews/Yilan',
    '花蓮縣': 'https://news.ltn.com.tw/list/breakingnews/Hualien',
    '臺東縣': 'https://news.ltn.com.tw/list/breakingnews/Taitung',
    '澎湖縣': 'https://news.ltn.com.tw/list/breakingnews/Penghu',
    '金門縣': 'https://news.ltn.com.tw/list/breakingnews/Kinmen',
    '連江縣': 'https://news.ltn.com.tw/list/breakingnews/Matsu'
}

def display_news_content(url):
    '''
    取得新閒內容
    '''
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    content = ' '.join([
        p.text.strip() for p in paragraphs
        if '爆' not in p.text and '為達最佳瀏覽效果' not in p.text
    ])
    return content

# 更新新聞標題選項
def query_news_list(location):
    '''
    取得新聞清單
    '''
    url = locations[location]

    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    headlines = soup.find_all('a', class_='tit')

    # 提取標題和鏈接
    table_data = [
        {
            'text': headline.get_text(strip=True),
            'href': headline.attrs['href'],
            'content': display_news_content(headline.attrs['href'])
        }
        for headline in headlines[:10]]
    return render_template('News.html', table_data=table_data)
