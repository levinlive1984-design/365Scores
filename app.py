import streamlit as st
import time
from datetime import datetime
import pytz
from api365_utils import get_365_scoreboard

st.set_page_config(
    page_title="Gemini 體育戰情系統 2.0", 
    layout="wide",
    initial_sidebar_state="expanded" 
)
tw_tz = pytz.timezone('Asia/Taipei')

if 'toggle_nba' not in st.session_state: st.session_state.toggle_nba = True
if 'toggle_mlb' not in st.session_state: st.session_state.toggle_mlb = True
if 'toggle_npb' not in st.session_state: st.session_state.toggle_npb = False
if 'toggle_kbo' not in st.session_state: st.session_state.toggle_kbo = False
if 'toggle_tennis' not in st.session_state: st.session_state.toggle_tennis = False

def emergency_reset():
    st.session_state.toggle_nba = True
    st.session_state.toggle_mlb = True
    st.session_state.toggle_npb = False
    st.session_state.toggle_kbo = False
    st.session_state.toggle_tennis = False

with st.sidebar:
    st.markdown("## 🛰️ 戰情調度中心")
    selected_date = st.date_input("🗓️ 調閱日期", datetime.now(tw_tz).date())
    st.divider()
    
    st.markdown("### 🔌 模組撥桿 (Toggle)")
    
    show_nba = st.toggle("🏀 NBA 數據鏈路", key='toggle_nba')
    show_mlb = st.toggle("⚾ MLB 數據鏈路", key='toggle_mlb')
    show_npb = st.toggle("⚾ NPB 日職模組", key='toggle_npb')
    show_kbo = st.toggle("⚾ KBO 韓職模組", key='toggle_kbo')
    show_tennis = st.toggle("🎾 Tennis 網球監控", key='toggle_tennis')
    
    active_leagues = []
    if show_nba: active_leagues.append("NBA")
    if show_mlb: active_leagues.append("MLB")
    if show_npb: active_leagues.append("NPB")
    if show_kbo: active_leagues.append("KBO")
    if show_tennis: active_leagues.append("Tennis")

    st.divider()
    st.button("🔴 緊急重置看板", on_click=emergency_reset, help="將所有模組恢復至預設狀態")

main_container = st.empty()

def get_table_html(title, data_list):
    html = f"### {title}\n"
    if not data_list:
        return html + "該日期暫無賽事數據。"

    table_html = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 25px;'>"
    table_html += "<thead><tr style='background-color: #f8f9fa; border-bottom: 2px solid #333;'>"
    table_html += "<th style='text-align: left; padding: 12px; width: 15%;'>時間</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 20%;'>狀態</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 45%;'>對戰組合</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 20%;'>比分</th>"
    table_html += "</tr></thead><tbody>"
    
    for row in data_list:
        if row['State'] == 'post':
            status_html = f"<span style='background-color: #e9ecef; color: #6c757d; padding: 4px 8px; border-radius: 4px;'>{row['Status']}</span>"
        elif row['State'] == 'in':
            status_html = f"<span style='color: #dc3545; font-weight: bold;'>{row['Status']}</span>"
        else:
            status_html = row['Status']
            
        match_html = f"{row['Away']} <span style='color: red; font-weight: bold;'>vs</span> {row['Home']}"
            
        table_html += "<tr style='border-bottom: 1px solid #dee2e6;'>"
        table_html += f"<td style='padding: 12px;'>{row['Time']}</td>"
        table_html += f"<td style='padding: 12px;'>{status_html}</td>"
        table_html += f"<td style='padding: 12px;'>{match_html}</td>"
        table_html += f"<td style='padding: 12px; font-weight: bold;'>{row['Score']}</td>"
        table_html += "</tr>"
    table_html += "</tbody></table>"
    return html + table_html

with main_container.container():
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; }
            .update-timestamp { font-family: 'Courier New', monospace; color: #00FF00; background: #000; padding: 2px 8px; border-radius: 4px; }
        </style>
    """, unsafe_allow_html=True)
    
    current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
    st.markdown(f"⏱️ <span class='update-timestamp'>SYSTEM_LIVE: {current_time}</span>", unsafe_allow_html=True)

    num_leagues = len(active_leagues)
    
    if num_leagues > 0:
        num_cols = min(num_leagues, 3) 
        cols = st.columns(num_cols)

        for i, league in enumerate(active_leagues):
            with cols[i % num_cols]:
                if league == "NBA":
                    st.markdown(get_table_html("🏀 NBA", get_365_scoreboard('nba', selected_date)), unsafe_allow_html=True)
                elif league == "MLB":
                    st.markdown(get_table_html("⚾ MLB", get_365_scoreboard('mlb', selected_date)), unsafe_allow_html=True)
                elif league == "NPB":
                    st.markdown(get_table_html("⚾ NPB (日職)", get_365_scoreboard('npb', selected_date)), unsafe_allow_html=True)
                elif league == "KBO":
                    st.markdown(get_table_html("⚾ KBO (韓職)", get_365_scoreboard('kbo', selected_date)), unsafe_allow_html=True)
                elif league == "Tennis":
                    # 網球模組正式上線
                    st.markdown(get_table_html("🎾 Tennis (網球)", get_365_scoreboard('tennis', selected_date)), unsafe_allow_html=True)
    else:
        st.warning("📡 請由左側面板啟動賽事數據鏈路...")

time.sleep(10)
st.rerun()
