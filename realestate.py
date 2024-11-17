'''
# 作者: 112121931 林智鴻
# 描述: 於不動產成交案件，實際資料供應系統下載實價登錄資訊檔案
#       查詢實價登入資訊與結合google map，查詢地點
'''

import os
import zipfile
import requests
import pandas as pd
from cities import get_city_files

# 實價登錄資料 URL
ZIP_URL = "https://plvr.land.moi.gov.tw//Download?type=zip&fileName=lvr_landcsv.zip"
DATA_DIR = "real_estate_data"
ZIP_FILE_PATH = os.path.join(DATA_DIR, "lvr_landcsv.zip")

def download_and_extract_data():
    '''
    下載並解壓縮實價登錄資料
    '''
    # 確保實價登錄資料夾存在
    if not os.path.exists(DATA_DIR):
        print(f"建立{DATA_DIR}資料夾")
        os.makedirs(DATA_DIR)

    print("下載實價登錄資料中...")
    response = requests.get(ZIP_URL, timeout=30)
    with open(ZIP_FILE_PATH, "wb") as zip_file:
        zip_file.write(response.content)
    print("解壓縮資料...")
    with zipfile.ZipFile(ZIP_FILE_PATH, "r") as zip_ref:
        zip_ref.extractall(DATA_DIR)
    print("下載並解壓縮完成。")

def read_city_data(file_name):
    '''
    讀取指定城市的 CSV 資料
    '''
    file_path = os.path.join(DATA_DIR, file_name)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, encoding='utf-8')
        if df['總價元'].dtype not in {'int64', 'float64'}:
            df['總價元'] = pd.to_numeric(df['總價元'], errors='coerce')
        print(f"成功讀取 {file_name} 資料")
        return df

    print(f"找不到 {file_name} 的資料")
    return None

def generate_google_maps_link(address):
    '''
    生成 Google Maps 連結
    '''
    return f"https://www.google.com/maps/search/?api=1&query={address}"

def query_real_estate(city, min_price, max_price):
    '''
    查詢指定城市的房屋交易資料
    '''
    if city not in get_city_files():
        return f"抱歉，目前不支援 {city} 的資料查詢"

    # 讀取資料
    file_name = get_city_files()[city]
    df = read_city_data(file_name)
    if df is None:
        return f"抱歉，{city} 的 {file_name} 資料檔案不存在，請執行『下載實價登錄資訊』"

    # 將 "土地位置建物門牌" 欄位內容替換為 Google Maps 連結
    df['土地位置建物門牌'] = df['土地位置建物門牌'].apply(
        lambda x: f'<a href="{generate_google_maps_link(x)}" target="_blank">{x}</a>')

    # 將總價元轉換為帶千分位的格式
    df['總價'] = df['總價元'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')

    # 將單價元平方公尺轉換為帶千分位的格式
    if '單價元平方公尺' in df.columns:
        df['單價元平方公尺'] = pd.to_numeric(df['單價元平方公尺'], errors='coerce')
        df['單價元平方公尺'] = df['單價元平方公尺'].apply(lambda x: f'{x:,.0f}' if pd.notnull(x) else '')

    # 篩選價格範圍
    filtered_df = df[(df['總價元'] >= min_price * 1000000) & (df['總價元'] <= max_price * 1000000)]

    # 顯示篩選後的結果
    if not filtered_df.empty:
        # 自訂 CSS 樣式讓總價欄位靠右對齊
        table_html = filtered_df[['鄉鎮市區', '土地位置建物門牌', '總價', '單價元平方公尺']].to_html(
            escape=False, render_links=True, classes='table table-striped', index=False)

        # 加入自訂樣式讓總價欄位靠右對齊
        th_style = """
        <style>
            th, td { text-align: center; }
            td:nth-child(3) { text-align: right; } /* 讓第三欄總價靠右對齊 */
            td:nth-child(4) { text-align: right; } /* 讓第四欄單價靠右對齊 */
        </style>
        """

        # 加入 Bootstrap 樣式與列印按鈕
        bs_link = "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css"
        bs_html = f"<link href=\"{bs_link}\" rel=\"stylesheet\">{th_style}{table_html}"

        print("篩選到的結果已生成。")
        return bs_html

    print(f"沒有符合價格範圍 {min_price} - {max_price} 佰萬元的交易資料。")
    return f"沒有符合價格範圍 {min_price} - {max_price} 佰萬元的交易資料。"
