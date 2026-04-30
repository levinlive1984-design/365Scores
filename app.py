import streamlit as st
import time  # 引入時間模組
from datetime import datetime
import pytz
from espn_utils import get_espn_scoreboard

# 系統配置
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄：極簡控制與頻率設定 ---
with st.sidebar:
    st.markdown("## 🏆 體育戰情監控")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    st.divider()
    # 新增：讓你可以自由控制多久去 ESPN 抓一次資料
    refresh_rate = st.selectbox("自動更新頻率", [10, 30, 60], index=1, format_func=lambda x: f"每 {x} 秒刷新")

# --- 強制 HTML 渲染引擎 ---
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
        html += f"<td style='padding: 12px; font-weight: bold;'>{row['Score']}</td>"
        html += "</tr>"
        
    html += "</tbody></table>"
    st.markdown(html, unsafe_allow_html=True)

# --- 主畫面空間優化 ---
st.markdown("""
    <style>
        .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }
        header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# 顯示最後更新時間，證明系統正在自動跳動
current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
st.caption(f"⏱️ 最後更新時間：{current_time} (系統將每 {refresh_rate} 秒自動抓取最新比分)")

col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("### 🏀 NBA")
    nba_data = get_espn_scoreboard('basketball', 'nba', selected_date)
    render_html_table(nba_data)

with col_mlb:
    st.markdown("### ⚾ MLB")
    mlb_data = get_espn_scoreboard('baseball', 'mlb', selected_date)
    render_html_table(mlb_data)

# --- 戰情心跳：自動刷新邏輯 ---
# 放置於代碼最底層，確保畫面渲染完畢後才開始倒數
time.sleep(refresh_rate)
st.rerun()
