import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 網頁標題與樣式設定
st.set_page_config(page_title="365Scores 賽事看板 1:1", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stTable { background-color: white; border-radius: 10px; }
    .league-header { background-color: #1a1a1a; color: white; padding: 10px; border-radius: 5px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 今日賽事總覽 (365Scores 模擬版)")
st.write(f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 模擬資料抓取函數 (實務上建議使用 API，此處以邏輯展示)
def get_match_data():
    # 這裡預設為今日 2026-04-30 的結構化資料
    # 在 GitHub Actions 中，你可以串接 selenium 或 requests 抓取真實 HTML
    data = [
        {"Category": "NBA", "Time": "07:30", "Status": "已結束", "Match": "紐約尼克 vs 費城 76 人", "Score": "102 - 108"},
        {"Category": "NBA", "Time": "10:00", "Status": "進行中", "Match": "克里夫蘭騎士 vs 奧蘭多魔術", "Score": "56 - 48"},
        {"Category": "MLB", "Time": "07:10", "Status": "第 9 局", "Match": "紐約洋基 vs 巴爾的摩金鶯", "Score": "2 - 4"},
        {"Category": "MLB", "Time": "09:40", "Status": "第 1 局", "Match": "洛杉磯道奇 vs 亞利桑那響尾蛇", "Score": "1 - 0"},
        {"Category": "日本職棒", "Time": "17:00", "Status": "預計", "Match": "廣島東洋鯉魚 vs 阪神虎", "Score": "-"},
        {"Category": "日本職棒", "Time": "17:00", "Status": "預計", "Match": "讀賣巨人 vs 橫濱 DeNA 海灣之星", "Score": "-"},
        {"Category": "網球", "Time": "17:00", "Status": "預計", "Match": "萊巴金娜 vs 普丁塞娃", "Score": "Madrid Open"},
        {"Category": "網球", "Time": "18:30", "Status": "預計", "Match": "魯布列夫 vs 阿爾卡拉斯", "Score": "Madrid Open"},
        {"Category": "網球", "Time": "20:00", "Status": "預計", "Match": "安德烈耶娃 vs 莎巴蓮卡", "Score": "Madrid Open"},
        {"Category": "網球", "Time": "21:30", "Status": "預計", "Match": "梅德維夫 vs 佛里茲", "Score": "Madrid Open"},
    ]
    return pd.DataFrame(data)

df = get_match_data()

# 分門別列顯示
categories = ["NBA", "MLB", "日本職棒", "網球"]

for cat in categories:
    st.markdown(f"<div class='league-header'><h3>{cat}</h3></div>", unsafe_allow_html=True)
    subset = df[df['Category'] == cat].sort_values(by="Time")
    
    if not subset.empty:
        # 使用表格呈現 1:1 邏輯
        st.table(subset[['Time', 'Status', 'Match', 'Score']])
    else:
        st.write("目前無賽事資訊")

st.sidebar.info("系統提示：此看板已根據 365Scores 結構優化。")
