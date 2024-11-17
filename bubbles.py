'''
# 作者: 102120085 李佳慧
# 描述: 繪制泡泡圖
'''

import base64
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm
from realestate import read_city_data
from cities import get_city_files

# 設定字體路徑
font_path = os.path.abspath('fonts/NotoSansCJKtc-Black.otf')
zh_font = fm.FontProperties(fname=font_path)

# 設定中文字體
rcParams['font.sans-serif'] = ['Source Han Serif TW VF']  # 確保安裝了相應的字體
rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

def query_real_estate(city, min_price, max_price):
    '''
    #資料預處理
    '''
    if city not in get_city_files():
        print(f"抱歉，目前不支援 {city} 的資料查詢")
        return None

    # 讀取資料
    file_name = get_city_files()[city]
    df = read_city_data(file_name)
    if df is None:
        return None

    # 篩選價格範圍
    filtered_df = df[(df['總價元'] >= min_price * 1000000) & (df['總價元'] <= max_price * 1000000)]

    # 返回篩選後的結果
    return filtered_df


def plot_bubble_chart(df, city):
    '''
    # 繪製泡泡圖的函數
    '''
    # 清理數據：移除缺失或無效的數據
    df = df.dropna(subset=['總價元', '建物移轉總面積平方公尺', '鄉鎮市區'])

    # 確保總價元和建物移轉總面積平方公尺是數字類型，並過濾出大於 0 的值
    df['總價元'] = pd.to_numeric(df['總價元'], errors='coerce')
    df['建物移轉總面積平方公尺'] = pd.to_numeric(df['建物移轉總面積平方公尺'], errors='coerce')
    df = df[(df['總價元'] > 0) & (df['建物移轉總面積平方公尺'] > 0)].dropna(subset=['總價元', '建物移轉總面積平方公尺'])

    # 計算單價元平方公尺
    df['單價元平方公尺'] = df['總價元'] / df['建物移轉總面積平方公尺']

    # 確保有有效的數據
    if df.empty:
        print("無有效數據，無法繪製泡泡圖。")
        return None

    # 按區域分組，計算每個區域的交易總數
    area_count = df['鄉鎮市區'].value_counts()

    # 將每個房屋的區域交易總數作為泡泡大小
    df['泡泡大小'] = df['鄉鎮市區'].apply(lambda x: area_count.get(x, 0))

    # 繪製泡泡圖
    plt.figure(figsize=(11, 7))

    # 使用不同顏色繪製每個區域的泡泡
    unique_areas = df['鄉鎮市區'].unique()
    colors = plt.cm.get_cmap('tab20', len(unique_areas))  # 使用 'tab20' 顏色映射
    color_map = {area: colors(i) for i, area in enumerate(unique_areas)}

    for area in unique_areas:
        area_data = df[df['鄉鎮市區'] == area]
        plt.scatter(
            area_data['建物移轉總面積平方公尺'] / 3.3058,  # X 軸：將平方公尺轉換為坪
            area_data['單價元平方公尺'] / 10000 ,  # Y 軸：單價萬元平方公尺
            s=area_data['泡泡大小'] * 10,     # 泡泡大小：區域交易總數
            alpha=0.5,
            color=color_map[area],         # 區域顏色
            label=area
        )

    # 設定圖表標題與軸標籤
    plt.title(f"{city} --> 各區域房屋_交易數據", fontproperties=zh_font)
    plt.xlabel('建物移轉總面積 (坪)', fontproperties=zh_font)
    plt.ylabel('單價 (萬/平方公尺)', fontproperties=zh_font)

    # 添加圖例
    plt.legend(
        loc='upper right',
        bbox_to_anchor=(1.2, 1),
        title="區域",
        title_fontproperties=zh_font, prop=zh_font
        )

    # 顯示圖表
    plt.tight_layout()

    # 將圖片保存到記憶體中
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)

    # 將圖片轉換為 base64 編碼的字符串
    img_base64 = base64.b64encode(img.getvalue()).decode('utf-8')

    return img_base64

def print_bubbles(city, min_price, max_price):
    '''
    # 繪製泡泡圖
    '''
    filtered_df = query_real_estate(city, min_price, max_price)
    # 確認 df 不為空
    if filtered_df is not None and not filtered_df.empty:
        # 繪製泡泡圖
        img_base64 = plot_bubble_chart(filtered_df, city)
        img_tag = f'<img src="data:image/png;base64,{img_base64}" alt="Bubble Chart">'
        return img_tag

    return f"沒有符合價格範圍 {min_price} - {max_price} 萬元的交易資料。"
