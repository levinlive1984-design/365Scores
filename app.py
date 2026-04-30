import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

# 設定網頁標題
st.set_page_config(page_title="今日棒球賽程", page_icon="⚾", layout="wide")
st.title("⚾ 今日棒球賽程：MLB & 日本職棒")
st.write("資料來源：365scores | 自動轉換為台灣時間並排序")

@st.cache_data(ttl=1800) # 快取 30 分鐘，避免每次重整都重新爬取導致被鎖 IP
def fetch_and_process_data():
    # 1. 設定 Selenium 隱藏模式 (適用於 Streamlit Cloud)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        # 啟動瀏覽器
        driver = webdriver.Chrome(options=chrome_options)
        # 前往 365scores 棒球頁面
        driver.get("https://www.365scores.com/zh-tw/baseball")
        
        # 等待 5 秒讓 JavaScript 載入賽程資料
        time.sleep(5) 
        
        # 取得渲染後的 HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        
        # 2. 解析網頁資料
        # ⚠️ 注意：365scores 的 class name 可能會隨機變動，請使用 F12 開發者工具確認實際的 class
        data =[]
        
        # --- 以下為解析邏輯框架，需根據實際 HTML 結構微調 ---
        # 假設賽事區塊的 class 包含 'game-card' 或類似名稱
        # for game in soup.find_all('div', class_='game-card'):
        #     league = game.find('div', class_='league-name').text
        #     away = game.find('div', class_='away-team').text
        #     home = game.find('div', class_='home-team').text
        #     match_time = game.find('div', class_='match-time').text
        #     data.append({"聯盟": league, "客隊": away, "主隊": home, "時間": match_time})
        
        # -----------------------------------------------------------
        # 💡 模擬資料區塊 (確保你在還沒抓對 class 前，網頁依然能運行測試)
        if not data:
            data =[
                {"聯盟": "MLB", "客隊": "洛杉磯道奇", "主隊": "紐約洋基", "時間": "08:05"},
                {"聯盟": "日本職棒", "客隊": "讀賣巨人", "主隊": "阪神虎", "時間": "17:00"},
                {"聯盟": "MLB", "客隊": "聖地牙哥教士", "主隊": "芝加哥小熊", "時間": "02:10"},
                {"聯盟": "韓國職棒", "客隊": "三星獅", "主隊": "起亞虎", "時間": "17:30"},
                {"聯盟": "日本職棒", "客隊": "軟銀鷹", "主隊": "歐力士", "時間": "13:00"}
            ]
            st.info("提示：目前顯示為測試資料。請使用 F12 檢查 365scores 的 HTML 結構並解除 app.py 中爬蟲程式碼的註解。")
        # -----------------------------------------------------------

        df = pd.DataFrame(data)
        
        # 3. 過濾出「日本」與「MLB」
        # 使用正則表達式匹配包含 "日本" 或 "MLB" 的聯盟
        df = df[df["聯盟"].str.contains("日本|MLB", na=False, case=False)]
        
        # 4. 處理時間與排序 (台灣時間)
        # 雲端伺服器通常在美國 (UTC)，如果爬到的時間是 UTC，需要 +8 小時
        # 這裡假設抓下來的時間格式為 "HH:MM"
        def convert_to_taiwan_time(time_str):
            try:
                # 將字串轉為時間物件
                t = datetime.strptime(time_str, "%H:%M")
                # 如果需要加 8 小時 (視 365scores 抓到的時區而定)
                # t = t + timedelta(hours=8) 
                return t.strftime("%H:%M")
            except:
                return time_str

        df["台灣時間"] = df["時間"].apply(convert_to_taiwan_time)
        
        # 依照時間排序
        df = df.sort_values(by="台灣時間").reset_index(drop=True)
        
        # 整理顯示欄位
        df = df[["台灣時間", "聯盟", "客隊", "主隊"]]
        
        return df
        
    except Exception as e:
        st.error(f"爬蟲執行失敗: {e}")
        return pd.DataFrame()

# 執行爬蟲並顯示資料
with st.spinner('正在從 365scores 抓取最新賽程...'):
    df_schedule = fetch_and_process_data()

if not df_schedule.empty:
    # 使用 Streamlit 的 dataframe 顯示，並隱藏 index
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)
else:
    st.warning("今日目前沒有符合的賽程資料。")
