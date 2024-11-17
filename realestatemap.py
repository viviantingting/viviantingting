'''
# 作者: 112121931 林智鴻
# 描述: 於不動產成交案件，實際資料供應系統下載實價登錄資訊檔案
#       查詢實價登入資訊與結合google map，查詢地點
'''

import os
import re
import pickle
import pandas as pd
import folium
from geopy.geocoders import Nominatim
from cities import get_city_files, get_location_by_city
from realestate import read_city_data

DATA_DIR = "real_estate_data"
ZIP_FILE_PATH = os.path.join(DATA_DIR, "lvr_landcsv.zip")

def clean_address(address):
    '''
    # 定義阿拉伯數字、中文數字和全形數字的集合
    '''
    arabic_digits = '0123456789'
    chinese_digits = '一二三四五六七八九十'
    fullwidth_digits = '０１２３４５６７８９'

    # 創建正則表達式來匹配這些數字後跟“弄”或“樓”的部分
    pattern = (
        f'[{arabic_digits}{chinese_digits}{fullwidth_digits}]+弄|'
        f'[{arabic_digits}{chinese_digits}{fullwidth_digits}]+號|'
        f'[{arabic_digits}{chinese_digits}{fullwidth_digits}]+樓'
    )

    # 使用正則表達式進行替換
    cleaned_address = re.sub(pattern, '', address)
    # 去除 '之' (含) 以後的資料
    cleaned_address = re.sub(r'之.*$', '', cleaned_address)

    return cleaned_address

def get_coordinates(location):
    '''
    查詢座標資訊
    '''
    cache_file = os.path.join(DATA_DIR, 'location_cache.pkl')

    # 嘗試從暫存檔中讀取座標資訊
    try:
        with open(cache_file, 'rb') as f:
            location_cache = pickle.load(f)
    except FileNotFoundError:
        location_cache = {}

    # 如果暫存檔中已有該地點的座標，則直接返回
    if location in location_cache:
        return location_cache[location]

    # 否則，使用 geolocator 查詢座標
    geolocator = Nominatim(user_agent="realestatemap")
    location_obj = geolocator.geocode(location, timeout=10)

    if location_obj:
        coordinates = (location_obj.latitude, location_obj.longitude)
    else:
        coordinates = None

    # 將查詢結果存入暫存檔
    location_cache[location] = coordinates
    with open(cache_file, 'wb') as f:
        pickle.dump(location_cache, f)

    return coordinates

def query_real_estate_map(city, min_price, max_price):
    '''
    查詢指定城市的房屋交易資料地圖
    '''
    if city not in get_city_files():
        return f"抱歉，目前不支援 {city} 的資料查詢"

    # 讀取資料
    df = read_city_data(get_city_files()[city])
    if df is None:
        return f"抱歉，{city} 的 {get_city_files()[city]} 資料檔案不存在，請執行『下載實價登錄資訊』"

    # 將總價元轉換為帶千分位的格式
    df['總價'] = df['總價元'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')

    # 篩選價格範圍
    filtered_df = df[(df['總價元'] >= min_price * 1000000) & (df['總價元'] <= max_price * 1000000)]

    # 顯示篩選後的結果
    if not filtered_df.empty:
        m = folium.Map(location=get_location_by_city(city), zoom_start=12)

        # 添加標記
        count = 0
        for index, row in filtered_df.iterrows():
            if count >= 100 or index >= 100:
                break
            location = get_coordinates(clean_address(row['土地位置建物門牌']))
            if location is not None:
                folium.Marker(
                location= location,
                popup=f"門牌:{row['鄉鎮市區']}{row['土地位置建物門牌']}, 金額 :{int(row['總價元']):,}",
                tooltip=f"門牌:{row['鄉鎮市區']}{row['土地位置建物門牌']}, 金額 :{int(row['總價元']):,}"
                ).add_to(m)
                count += 1

        # 使用 branca.element.Element 來獲取 HTML 表示
        map_html = m.get_root().render()

        return map_html

    return f"沒有符合價格範圍 {min_price} - {max_price} 佰萬元的交易資料。"
