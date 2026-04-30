import streamlit as st
import time
from datetime import datetime
import pytz
from api365_utils import get_365_scoreboard

# --- 系統配置 ---
st.set_page_config(
    page_title="Gemini 體育戰情系統 2.0", 
    layout="wide",
    initial_sidebar_state="expanded" 
)
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄：調度中心 ---
with st.sidebar:
    st.markdown("## 🛡️ 戰情調度中心")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    st.divider()
    
    active_leagues = st.multiselect(
        "看板顯示內容",
        ["NBA", "MLB", "NPB"],
        default=["NBA", "MLB"],
        help="勾選後賽事將自動填補主畫面空白處"
    )

# --- 頁面主體預留區 (防止殘影) ---
main_container = st.empty()

# --- HTML 渲染引擎 ---
def get_table_html(title, data_list):
    html = f"### {title}\n"
    if not data_list:
        return html + "該日期暫無賽事數據。"

    # 移除了所有強制縮小字體的 CSS，讓字體回歸清晰標準尺寸
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

# --- 戰情邏輯與顯示 ---
with main_container.container():
    st.markdown("<style>.block-container { padding-top: 1rem !important; }</style>", unsafe_allow_html=True)
    
    current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
    st.caption(f"⏱️ 直連 365Scores | 每 10s 自動更新 | 最後更新：{current_time}")

    cols = st.columns(2)

    for i, league in enumerate(active_leagues):
        with cols[i % 2]:
            if league == "NBA":
                st.markdown(get_table_html("🏀 NBA", get_365_scoreboard('nba', selected_date)), unsafe_allow_html=True)
            elif league == "MLB":
                st.markdown(get_table_html("⚾ MLB", get_365_scoreboard('mlb', selected_date)), unsafe_allow_html=True)
            elif league == "NPB":
                st.markdown(get_table_html("⚾ NPB (日職)", get_365_scoreboard('npb', selected_date)), unsafe_allow_html=True)

# --- 戰情心跳 ---
time.sleep(10)
st.rerun()
