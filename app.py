import streamlit as st
import time
from datetime import datetime
import pytz
# 導入我們最新的 365 API 模組
from api365_utils import get_365_scoreboard

st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄 ---
with st.sidebar:
    st.markdown("## 🏆 體育戰情監控")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    st.divider()
    # 輪詢頻率設定
    refresh_rate = st.selectbox("自動更新頻率", [5, 10, 30], index=1, format_func=lambda x: f"每 {x} 秒刷新")

# --- HTML 渲染引擎 ---
def render_html_table(data_list):
    if not data_list:
        st.write("該日期暫無賽事數據。")
        return

    html = ""
    html += "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px;'>"
    html += "<thead>"
    html += "<tr style='background-color: #f8f9fa; border-bottom: 2px solid #333;'>"
    html += "<th style='text-align: left; padding: 12px; width: 10%;'>時間</th>"
    html += "<th style='text-align: left; padding: 12px; width: 20%;'>狀態</th>"
    html += "<th style='text-align: left; padding: 12px; width: 50%;'>對戰組合</th>"
    html += "<th style='text-align: left; padding: 12px; width: 20%;'>比分</th>"
    html += "</tr>"
    html += "</thead>"
    html += "<tbody>"
    
    for row in data_list:
        if row['State'] == 'post':
            status_html = f"<span style='background-color: #e9ecef; color: #6c757d; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;'>{row['Status']}</span>"
        elif row['State'] == 'in':
            status_html = f"<span style='color: #dc3545; font-weight: bold;'>{row['Status']}</span>"
        else:
            status_html = row['Status']
            
        match_html = f"{row['Away']} <span style='color: red; font-weight: bold; margin: 0 5px;'>vs</span> {row['Home']}"
            
        html += "<tr style='border-bottom: 1px solid #dee2e6;'>"
        html += f"<td style='padding: 12px;'>{row['Time']}</td>"
        html += f"<td style='padding: 12px;'>{status_html}</td>"
        html += f"<td style='padding: 12px;'>{match_html}</td>"
        html += f"<td style='padding: 12px; font-weight: bold; font-size: 1.1em;'>{row['Score']}</td>"
        html += "</tr>"
        
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# --- 版面優化與更新時間戳記 ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
st.caption(f"⏱️ 365Scores 直連中 | 最後更新：{current_time} (系統每 {refresh_rate} 秒抓取)")

# --- 雙欄位佈局 ---
col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("### 🏀 NBA")
    # 使用 365 API 抓取籃球
    nba_data = get_365_scoreboard('nba', selected_date)
    render_html_table(nba_data)

with col_mlb:
    st.markdown("### ⚾ MLB")
    # 使用 365 API 抓取棒球
    mlb_data = get_365_scoreboard('mlb', selected_date)
    render_html_table(mlb_data)

# --- 戰情心跳 ---
time.sleep(refresh_rate)
st.rerun()
