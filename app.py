import streamlit as st
import time
from datetime import datetime
import pytz

# --- 核心模組匯入 ---
from api365_utils import get_365_scoreboard
from ui_renderer import setup_cyber_css, get_table_html

st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide", initial_sidebar_state="expanded")
tw_tz = pytz.timezone('Asia/Taipei')

# 載入賽博視覺與防殘影 CSS
setup_cyber_css()

# 狀態記憶初始化
default_toggles = {'toggle_nba':True, 'toggle_mlb':True, 'toggle_npb':False, 'toggle_kbo':False, 'toggle_tennis':False, 'toggle_nhl':False}
for key, val in default_toggles.items():
    if key not in st.session_state: st.session_state[key] = val

def force_refresh():
    pass 

def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']: st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']: st.session_state[key] = False

with st.sidebar:
    st.markdown("## 🛰️ 戰情調度中心")
    selected_date = st.date_input("🗓️ 調閱日期", datetime.now(tw_tz).date())
    st.divider()
    st.markdown("### 🔌 模組撥桿 (Toggle)")
    
    show_nba = st.toggle("🏀 NBA 數據鏈路", key='toggle_nba', on_change=force_refresh)
    show_mlb = st.toggle("⚾ MLB 數據鏈路", key='toggle_mlb', on_change=force_refresh)
    show_nhl = st.toggle("🏒 NHL 冰球鏈路", key='toggle_nhl', on_change=force_refresh)
    show_npb = st.toggle("⚾ NPB 日職模組", key='toggle_npb', on_change=force_refresh)
    show_kbo = st.toggle("⚾ KBO 韓職模組", key='toggle_kbo', on_change=force_refresh)
    show_tennis = st.toggle("🎾 Tennis 網球監控", key='toggle_tennis', on_change=force_refresh)
    
    active_leagues = [L for L, S in zip(
        ["NBA", "MLB", "NHL", "NPB", "KBO", "Tennis"], 
        [show_nba, show_mlb, show_nhl, show_npb, show_kbo, show_tennis]
    ) if S]
    
    st.divider()
    st.button("🔴 緊急重置看板", on_click=emergency_reset)

# --- 主戰情螢幕渲染 ---
st.markdown(f"⏱️ <span class='update-timestamp'>SYSTEM_LIVE: {datetime.now(tw_tz).strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

if active_leagues:
    cols = st.columns(min(len(active_leagues), 3))
    for i, league in enumerate(active_leagues):
        with cols[i % len(cols)]:
            icon = "🏀" if league == "NBA" else "🎾" if league == "Tennis" else "🏒" if league == "NHL" else "⚾"
            
            # 呼叫外部的 get_table_html 來套用頁籤設計
            html_content = get_table_html(f"{icon} {league}", get_365_scoreboard(league.lower().split(' ')[0], selected_date))
            st.markdown(html_content, unsafe_allow_html=True)
else:
    st.warning("📡 請由左側面板啟動賽事數據鏈路...")

time.sleep(10)
st.rerun()
