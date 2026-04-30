import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import time

# 設定網頁標題
st.set_page_config(page_title="Gemini 體育戰情系統 2.0 - 數據採集器", layout="wide")

def fetch_data_with_retry(url, max_retries=3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Referer': 'https://www.365scores.com/',
        'Origin': 'https://www.365scores.com'
    }
    for i in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if i == max_retries - 1:
                st.error(f"連線失敗（最後嘗試）: {e}")
                return None
            time.sleep(2) # 失敗後等待 2 秒重試

def get_365_live_all():
    # 使用 365Scores 網頁端最核心的 API
    # 移除日期限制，改抓取當前系統全量數據
    api_url = "https://webapi.365scores.com/web/games/current/?langId=10&timezoneId=24&userCountryId=6"
    
    data = fetch_data_with_retry(api_url)
    if not data:
        return pd.DataFrame()

    games = data.get('games', [])
    # 建立賽事與聯賽的對照表
    competitions = {c['id']: c['name'] for c in data.get('competitions', [])}
    
    all_events = []
    for g in games:
        comp_id = g.get('competitionId')
        comp_name = competitions.get(comp_id, "未知聯賽")
        
        # 獲取隊伍與比分
        home = g.get('homeCompetitor', {})
        away = g.get('awayCompetitor', {})
        
        # 抓取狀態 (包含已結束、進行中、預計)
        status = g.get('statusText', '未知')
        
        # 獲取時間並轉換 (處理 API 內的 ISO 時間)
        raw_time = g.get('startTime')
        try:
            clean_time = datetime.fromisoformat(raw_time.replace('Z', '+00:00')).strftime('%H:%M')
        except:
            clean_time = "N/A"

        all_events.append({
            "Category": comp_name,
            "CompID": comp_id,
            "Time": clean_time,
            "Status": status,
            "Match": f"{away.get('name')} @ {home.get('name')}",
            "Score": f"{away.get('score')} - {home.get('score')}" if away.get('score') != -1 else "-"
        })
    
    return pd.DataFrame(all_events)

# --- 介面呈現 ---
st.title("🛡️ Gemini 體育戰情系統 2.0 (數據實時抓取)")
st.write(f"系統狀態：數據同步中 | 當前資產：853 元")

if st.sidebar.button('🔄 強制刷新全量數據'):
    st.cache_data.clear()
    st.rerun()

df = get_365_live_all()

if not df.empty:
    # 依據你的要求進行精確分類，不遺漏任何「已結束」場次
    target_categories = {
        "NBA": df[df['Category'].str.contains('NBA', na=False)],
        "MLB": df[df['Category'].str.contains('MLB', na=False)],
        "日本棒球": df[df['CompID'] == 17], # 日職固定 ID 為 17
        "網球 (ATP/WTA/ITF)": df[df['Category'].str.contains('網球|ATP|WTA|ITF|馬德里', na=False)]
    }

    for label, sub_df in target_categories.items():
        st.subheader(f"📍 {label}")
        if not sub_df.empty:
            # 1:1 按照時間排序輸出
            output = sub_df.sort_values(by="Time")
            st.table(output[['Time', 'Status', 'Match', 'Score']])
        else:
            st.info(f"今日目前無 {label} 賽事數據。")
else:
    st.warning("目前無法解析 365Scores 數據，請確認網域連線狀態或稍後重試。")
