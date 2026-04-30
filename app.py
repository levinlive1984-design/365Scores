import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

st.set_page_config(page_title="今日棒球賽程", page_icon="⚾", layout="wide")
st.title("⚾ 今日棒球賽程：MLB & 日本職棒")
st.write("資料來源：365scores 即時 API | 自動轉換為台灣時間並排序")

@st.cache_data(ttl=60) # 快取 1 分鐘，確保比分是即時的
def fetch_and_process_data():
    try:
        # 1. 設定時區與今天日期
        tz = pytz.timezone('Asia/Taipei')
        today = datetime.now(tz).strftime("%d/%m/%Y")
        
        # 2. 呼叫 365scores 的隱藏 API 
        # sports=5 代表棒球，langId=27 代表繁體中文
        url = f"https://webws.365scores.com/web/games/?langId=27&timezoneName=Asia/Taipei&userCountryId=-1&appTypeId=5&sports=5&startDate={today}&endDate={today}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            st.error("無法連接到 365scores API")
            return pd.DataFrame()
            
        data = response.json()
        
        # 3. 解析 JSON 資料
        games = data.get("games", [])
        competitions = {comp["id"]: comp["name"] for comp in data.get("competitions",[])}
        competitors = {comp["id"]: comp["name"] for comp in data.get("competitors",[])}
        
        games_list =[]
        
        for game in games:
            # 取得聯盟名稱
            comp_id = game.get("competitionId")
            league = competitions.get(comp_id, "未知聯盟")
            
            # 取得主客隊名稱
            home_id = game.get("homeCompetitorId")
            away_id = game.get("awayCompetitorId")
            home_team = competitors.get(home_id, "未知主隊")
            away_team = competitors.get(away_id, "未知客隊")
            
            # 取得比賽時間並轉換為台灣時間
            start_time_str = game.get("startTime", "")
            try:
                dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
                dt = dt.astimezone(tz)
                time_display = dt.strftime("%H:%M")
            except:
                time_display = start_time_str
                
            # 取得比賽狀態與比分 (包含已結束、進行中)
            status = game.get("justifiedStatusText", game.get("statusText", "未知"))
            
            home_score = game.get("homeCompetitor", {}).get("score", -1)
            away_score = game.get("awayCompetitor", {}).get("score", -1)
            
            if home_score != -1 and away_score != -1:
                score_display = f"{away_score} - {home_score}"
            else:
                score_display = "尚未開始"
                
            games_list.append({
                "台灣時間": time_display,
                "聯盟": league,
                "狀態": status,
                "客隊": away_team,
                "比分 (客-主)": score_display,
                "主隊": home_team,
                "原始時間": start_time_str # 隱藏欄位，用來精準排序
            })
            
        df = pd.DataFrame(games_list)
        
        if df.empty:
            return df
            
        # 4. 過濾出「日本」與「MLB/美國」的賽事
        # 365scores 的聯盟名稱通常包含 "日本" 或 "美國"
        df = df[df["聯盟"].str.contains("日本|MLB|美國|大聯盟", na=False, case=False)]
        
        # 5. 依照時間排序
        if "原始時間" in df.columns:
            df = df.sort_values(by="原始時間").reset_index(drop=True)
            df = df.drop(columns=["原始時間"])
            
        return df
        
    except Exception as e:
        st.error(f"解析資料失敗: {e}")
        return pd.DataFrame()

# 執行抓取並顯示資料
with st.spinner('正在從 365scores API 抓取最新賽程與比分...'):
    df_schedule = fetch_and_process_data()

if not df_schedule.empty:
    # 顯示資料表
    st.dataframe(df_schedule, use_container_width=True, hide_index=True)
else:
    st.warning("今日目前沒有符合的賽程資料。")
