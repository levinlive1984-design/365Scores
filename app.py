import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

# --- 戰情系統配置 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0 - 數據監控中心", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# 側邊欄：戰情參數與資產
st.sidebar.markdown("### 🛡️ 戰情系統 2.0")
st.sidebar.markdown(f"**當前資產：** 853 元")
st.sidebar.markdown(f"**戰情指令：** V5.0 (Cross-ball optimization)")
st.sidebar.markdown(f"**更新時間：** {datetime.now(tw_tz).strftime('%H:%M:%S')}")

st.title("🏆 今日全賽程自動抓取 (Yahoo 全球數據源)")

def fetch_yahoo_scores(league):
    """
    獲取 Yahoo Sports 的賽事數據
    league slugs: nba, mlb, npb, tennis
    """
    # 這是 Yahoo 的公開 Scoreboard 資源 API 模式
    url = f"https://ws-api.sports.yahoo.com/v1/editorial/s/scoreboard?leagues={league}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        games_raw = data.get('service', {}).get('scoreboard', {}).get('games', {})
        
        parsed_data = []
        for g_id, g in games_raw.items():
            # 時間處理：Yahoo 是 ISO 格式字串
            start_time_str = g.get('startTime')
            utc_time = datetime.strptime(start_time_str, "%a, %d %b %Y %H:%M:%S %z")
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            status = g.get('status', {}).get('type')
            # 簡化狀態顯示
            status_map = {"final": "已結束", "scheduled": "預計", "in_progress": "進行中", "postponed": "延賽"}
            display_status = status_map.get(status, status)
            
            teams = g.get('teams', {})
            home = teams.get('home', {})
            away = teams.get('away', {})
            
            parsed_data.append({
                "Time": local_time,
                "Status": display_status,
                "Match": f"{away.get('abbrName')} @ {home.get('abbrName')}",
                "Score": f"{away.get('score', 0)} - {home.get('score', 0)}" if status != "scheduled" else "-"
            })
        return parsed_data
    except Exception as e:
        return []

# --- 分門別列顯示 ---
categories = {
    "🏀 NBA (美國職籃)": "nba",
    "⚾ MLB (美國職棒)": "mlb",
    "⚾ NPB (日本職棒)": "npb",
    "🎾 網球 (ATP/WTA 職業賽)": "tennis"
}

for label, slug in categories.items():
    st.header(label)
    res = fetch_yahoo_scores(slug)
    if res:
        df = pd.DataFrame(res).sort_values(by="Time")
        st.table(df)
    else:
        st.info(f"目前無 {label} 數據更新，或賽季未處於當前時段。")

st.markdown("---")
st.caption("提示：若場次未顯示，請確認當前日期是否有正式賽事安排。網球數據涵蓋 ATP、WTA 主要巡迴賽。")
