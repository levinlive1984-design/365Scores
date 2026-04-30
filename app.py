import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 戰情系統初始化 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# 側邊欄：資產監控與系統狀態
st.sidebar.markdown(f"### 🛡️ 戰情系統 2.0")
st.sidebar.markdown(f"**當前資產：** 853 元")
st.sidebar.markdown(f"**系統指令：** V5.0 (Cross-ball optimization)")
st.sidebar.markdown(f"**系統時區：** Asia/Taipei")
st.sidebar.markdown(f"**更新時間：** {datetime.now(tw_tz).strftime('%H:%M:%S')}")

st.title("🏆 今日全賽程自動抓取 (多源專業數據引擎)")

def get_mlb_api_data(sport_id, label):
    """
    使用 MLB 官方 Stats API
    sport_id: 1 (MLB), 51 (NPB 日本職棒)
    """
    date_str = datetime.now(tw_tz).strftime('%Y-%m-%d')
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId={sport_id}&date={date_str}"
    try:
        res = requests.get(url, timeout=10).json()
        games = res.get('dates', [{}])[0].get('games', [])
        parsed = []
        for g in games:
            # 轉換為台北時間
            utc_time = datetime.strptime(g['gameDate'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            status = g['status']['detailedState']
            home = g['teams']['home']
            away = g['teams']['away']
            
            parsed.append({
                "Time": local_time,
                "Status": "已結束" if status == "Final" else ("進行中" if "In Progress" in status else "預計"),
                "Match": f"{away['team']['name']} @ {home['team']['name']}",
                "Score": f"{away.get('score', 0)} - {home.get('score', 0)}" if status != "Scheduled" else "-"
            })
        return parsed
    except:
        return []

def get_espn_data(sport, league):
    """ 使用 ESPN API 作為 NBA 與 網球的補充源 """
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    try:
        res = requests.get(url, timeout=10).json()
        events = res.get('events', [])
        parsed = []
        for ev in events:
            utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            comp = ev['competitions'][0]
            away = comp['competitors'][0]['team']['displayName']
            home = comp['competitors'][1]['team']['displayName']
            status = ev['status']['type']['description']
            parsed.append({
                "Time": local_time,
                "Status": "已結束" if status == "Final" else ("進行中" if "In Progress" in status else "預計"),
                "Match": f"{away} @ {home}",
                "Score": f"{comp['competitors'][0]['score']} - {comp['competitors'][1]['score']}" if status != "Scheduled" else "-"
            })
        return parsed
    except:
        return []

# --- 數據抓取與顯示 ---

# 1. NBA
st.header("🏀 NBA (美國職籃)")
nba_data = get_espn_data('basketball', 'nba')
if nba_data:
    st.table(pd.DataFrame(nba_data).sort_values(by="Time"))
else:
    st.info("目前無 NBA 數據更新")

# 2. MLB
st.header("⚾ MLB (美國職棒)")
mlb_data = get_mlb_api_data(1, "MLB")
if mlb_data:
    st.table(pd.DataFrame(mlb_data).sort_values(by="Time"))
else:
    st.info("目前無 MLB 數據更新")

# 3. 日本職棒 (NPB) - 使用官方 SportId 51
st.header("⚾ 日本職棒 (NPB)")
npb_data = get_mlb_api_data(51, "NPB")
if npb_data:
    st.table(pd.DataFrame(npb_data).sort_values(by="Time"))
else:
    st.info("目前無 NPB 數據更新 (請確認今日是否有賽程)")

# 4. 網球 (ATP/WTA)
st.header("🎾 網球 (ATP/WTA 職業巡迴賽)")
tennis_data = get_espn_data('tennis', 'atp') + get_espn_data('tennis', 'wta')
if tennis_data:
    st.table(pd.DataFrame(tennis_data).sort_values(by="Time"))
else:
    st.info("目前無網球數據更新 (馬德里公開賽可能尚未開打)")

st.sidebar.markdown("---")
st.sidebar.write("💡 **INTJ 專業提示**：若 NPB 顯示為空，可能是因為今日為日職休賽日或官方 API 尚未更新數據。")
