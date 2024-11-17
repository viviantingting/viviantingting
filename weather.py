'''
# 作者: 112121931 林智鴻
# 描述: 於氣象資訊開放平臺，取得相關氣資訊
'''

import requests
import folium
from cities import get_cities

API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
API_KEY = "CWA-D5B056EA-33C1-4099-9FE8-C6282F14A951"

def get_city_info(city, location):
    '''
    取得城市資訊
    '''
    weather_elements = location['weatherElement']
    weather_description = weather_elements[0]['time'][0]['parameter']['parameterName']
    max_temp = weather_elements[4]['time'][0]['parameter']['parameterName']
    min_temp = weather_elements[2]['time'][0]['parameter']['parameterName']
    return f"{city} 的天氣狀況：{weather_description}\n最高溫度：{max_temp}°C\n最低溫度：{min_temp}°C"

def get_weather(city):
    '''
    # 查詢天氣
    '''
    params = {
        "Authorization": API_KEY,
        "locationName": city
    }
    response = requests.get(API_URL, params=params, timeout=10)

    if response.status_code == 200:
        data = response.json()
        if 'records' in data and 'location' in data['records']:
            location_data = data['records']['location']
            for location in location_data:
                if location['locationName'] == city:
                    return get_city_info(city, location)

        return f"無法取得 {city} 的天氣資料。"

    return "API 請求失敗，請稍後再試。"

def get_weather_map():
    '''
    繪制天氣地圖
    '''
    # 創建地圖
    m = folium.Map(location=[23.6978, 120.9605], zoom_start=8)

    # 添加標記
    for city, coords in get_cities().items():
        folium.Marker(
        location=coords,
        popup=city,
        tooltip=get_weather(city)
    ).add_to(m)

    # 使用 branca.element.Element 來獲取 HTML 表示
    map_html = m.get_root().render()

    return map_html
