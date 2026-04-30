import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- 系統初始化 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0 - SofaScore 核心", layout="wide")

# 你的戰情系統基礎資訊
st.sidebar.title("🛡️ 戰情系統 2.0")
st.sidebar.info(f"當前資產：853 元\n策略版本：V5.0 (Moneyline/Spread)")

def fetch_sofa_data(sport, date_str):
    """
    sport: 'basketball', 'baseball', 'tennis'
    date_str: '2026-04-30'
    """
    url = f"https://api.sofascore.com/api/v1/sport/{sport}/scheduled-events/{date_str}"
    
    # 模擬瀏覽器 Header，這是繞過阻斷的關鍵
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.sofascore.com/',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('events', [])
        return []
    except:
        return []

def process_events(events, filter_keywords=None):
    results = []
    for ev in events:
        league_name = ev.get('tournament', {}).get('name', '')
        
        # 如果有設定關鍵字過濾 (例如日本職棒)
        if filter_keywords and not any(k in league_name for k in filter_keywords):
            continue
            
        # 取得時間並轉換為台灣時區 (API 通常是 UTC)
        start_ts = ev.get('startTimestamp')
        dt_object = datetime.fromtimestamp(start_ts)
        time_str = dt_object.strftime('%H:%M')
        
        status = ev.get('status', {}).get('description', '未知')
        home_team = ev.get('homeTeam', {}).get('name')
        away_team = ev.get('awayTeam', {}).get('name')
        home_score = ev.get('homeScore', {}).get('display', 0)
        away_score = ev.get('awayScore', {}).get('display', 0)

        results.append({
            "Time": time_str,
            "League": league_name,
            "Status": status,
            "Match": f"{away_team} @ {home_team}",
            "Score": f"{away_score} - {home_score}" if status != "Not started" else "-"
        })
    return results

# --- 介面呈現 ---
st.title("🏆 今日全賽程自動抓取 (SofaScore 數據源)")
target_date = "2026-04-30"

# 1. NBA 抓取
with st.expander("🏀 NBA 賽程 (含已結束)", expanded=True):
    nba_raw = fetch_sofa_data('basketball', target_date)
    nba_list = process_events(nba_raw, filter_keywords=["NBA"])
    if nba_list:
        st.table(pd.DataFrame(nba_list).sort_values(by="Time"))
    else:
        st.write("目前無 NBA 數據")

# 2. MLB 抓取
with st.expander("⚾ MLB 賽程 (含已結束)", expanded=True):
    mlb_raw = fetch_sofa_data('baseball', target_date)
    mlb_list = process_events(mlb_raw, filter_keywords=["MLB"])
    if mlb_list:
        st.table(pd.DataFrame(mlb_list).sort_values(by="Time"))
    else:
        st.write("目前無 MLB 數據")

# 3. 日本職棒 (NPB) 抓取
with st.expander("⚾ 日本職棒 賽程", expanded=True):
    # NPB 同樣屬於 baseball 分類
    npb_list = process_events(mlb_raw, filter_keywords=["NPB", "Professional Baseball", "Japan"])
    if npb_list:
        st.table(pd.DataFrame(npb_list).sort_values(by="Time"))
    else:
        st.write("目前無 NPB 數據")

# 4. 網球 抓取 (這部分場次會非常多)
with st.expander("🎾 網球 全賽程 (ATP/WTA/ITF)", expanded=True):
    tennis_raw = fetch_sofa_data('tennis', target_date)
    tennis_list = process_events(tennis_raw)
    if tennis_list:
        st.table(pd.DataFrame(tennis_list).sort_values(by="Time"))
    else:
        st.write("目前無網球數據")
