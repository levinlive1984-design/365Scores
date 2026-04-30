import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 系統配置 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# 戰情系統標頭
st.title("🛡️ 今日全賽程自動抓取 (ESPN 核心數據引擎)")
st.sidebar.markdown(f"### 體育戰情系統 2.0\n**當前資產：** 853 元\n**系統時間：** {datetime.now(tw_tz).strftime('%H:%M:%S')}")

def get_espn_data(sport, league):
    """
    sport: basketball, baseball, tennis
    league: nba, mlb, npb, atp, wta
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    try:
        res = requests.get(url, timeout=10)
        data = res.json()
        events = data.get('events', [])
        
        parsed_data = []
        for ev in events:
            # 時間轉換 (UTC -> 台北時間)
            utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            # 對戰組合與比分
            comp = ev['competitions'][0]
            away = comp['competitors'][0]
            home = comp['competitors'][1]
            
            status = ev['status']['type']['description']
            # 簡化狀態名稱
            if status == "Final": status = "已結束"
            elif status == "Scheduled": status = "預計"
            elif "In Progress" in status or "Half" in status: status = "進行中"

            parsed_data.append({
                "Time": local_time,
                "Status": status,
                "Match": f"{away['team']['displayName']} @ {home['team']['displayName']}",
                "Score": f"{away['score']} - {home['score']}" if status != "預計" else "-"
            })
        return parsed_data
    except:
        return []

# --- 抓取邏輯 ---
# 1. NBA
st.header("🏀 NBA (美國職棒)")
nba = get_espn_data('basketball', 'nba')
if nba:
    st.table(pd.DataFrame(nba).sort_values(by="Time"))
else:
    st.info("目前無 NBA 數據")

# 2. MLB
st.header("⚾ MLB (美國職棒)")
mlb = get_espn_data('baseball', 'mlb')
if mlb:
    st.table(pd.DataFrame(mlb).sort_values(by="Time"))
else:
    st.info("目前無 MLB 數據")

# 3. 日本職棒 (NPB)
st.header("⚾ 日本職棒 (NPB)")
npb = get_espn_data('baseball', 'npb')
if npb:
    st.table(pd.DataFrame(npb).sort_values(by="Time"))
else:
    st.info("目前無 NPB 數據")

# 4. 網球 (ATP + WTA 聯賽)
st.header("🎾 網球 (ATP/WTA 職業巡迴賽)")
atp = get_espn_data('tennis', 'atp')
wta = get_espn_data('tennis', 'wta')
tennis_all = atp + wta
if tennis_all:
    st.table(pd.DataFrame(tennis_all).sort_values(by="Time"))
else:
    st.info("目前無網球數據")

# 戰意值評估區 (系統 2.0 預留位)
st.sidebar.markdown("---")
st.sidebar.subheader("戰意值評估 (Motivation)")
st.sidebar.write("數據已同步，可開始市場誘盤解析。")
