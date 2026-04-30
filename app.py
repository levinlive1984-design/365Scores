import streamlit as st
import time
from datetime import datetime
import pytz
from api365_utils import get_365_scoreboard

st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄 ---
with st.sidebar:
    st.markdown("## 🏆 戰情監控中心")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    st.divider()
    st.caption("資產狀況：853 元")
    st.caption("策略版本：V5.0")

# --- HTML 渲染引擎 ---
def render_html_table(data_list):
    if not data_list:
        st.write("該日期暫無賽事數據。")
        return

    html = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px; font-size: 0.95em;'>"
    html += "<thead><tr style='background-color: #f8f9fa; border-bottom: 2px solid #333;'>"
    html += "<th style='text-align: left; padding: 10px;'>時間</th>"
    html += "<th style='text-align: left; padding: 10px;'>狀態</th>"
    html += "<th style='text-align: left; padding: 10px;'>對戰組合</th>"
    html += "<th style='text-align: left; padding: 10px;'>比分</th>"
    html += "</tr></thead><tbody>"
    
    for row in data_list:
        if row['State'] == 'post':
            status_html = f"<span style='background-color: #e9ecef; color: #6c757d; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;'>{row['Status']}</span>"
        elif row['State'] == 'in':
            status_html = f"<span style='color: #dc3545; font-weight: bold;'>{row['Status']}</span>"
        else:
            status_html = row['Status']
            
        match_html = f"{row['Away']} <span style='color: red; font-weight: bold;'>vs</span> {row['Home']}"
            
        html += "<tr style='border-bottom: 1px solid #dee2e6;'>"
        html += f"<td style='padding: 10px;'>{row['Time']}</td>"
        html += f"<td style='padding: 10px;'>{status_html}</td>"
        html += f"<td style='padding: 10px;'>{match_html}</td>"
        html += f"<td style='padding: 10px; font-weight: bold;'>{row['Score']}</td>"
        html += "</tr>"
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# 介面優化
st.markdown("<style>.block-container { padding-top: 1rem !important; } header { visibility: hidden; }</style>", unsafe_allow_html=True)

current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
st.caption(f"⏱️ 365Scores 直連 | 監控中 | 最後更新：{current_time}")

# --- 三欄位佈局 ---
col_nba, col_mlb, col_npb = st.columns(3)

with col_nba:
    st.markdown("### 🏀 NBA")
    render_html_table(get_365_scoreboard('nba', selected_date))

with col_mlb:
    st.markdown("### ⚾ MLB")
    render_html_table(get_365_scoreboard('mlb', selected_date))

with col_npb:
    st.markdown("### ⚾ NPB (日職)")
    render_html_table(get_365_scoreboard('npb', selected_date))

# --- 戰情心跳 ---
time.sleep(10)
st.rerun()
