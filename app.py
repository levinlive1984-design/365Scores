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

# --- 側邊欄：看板調度中心 ---
with st.sidebar:
    st.markdown("## 🛡️ 戰情調度中心")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    
    st.divider()
    
    # 實現「拖曳式頁籤」功能的替代方案：側邊欄掛載區
    # 預設僅選中 NBA 與 MLB，NPB 則待命於選單中
    active_leagues = st.multiselect(
        "看板顯示內容 (勾選後自動占用欄位)",
        ["NBA", "MLB", "NPB"],
        default=["NBA", "MLB"],
        help="勾選後賽事將自動填補主畫面空白處"
    )

# --- HTML 渲染引擎 ---
def render_html_table(title, data_list):
    st.markdown(f"### {title}")
    if not data_list:
        st.write("該日期暫無賽事數據。")
        return

    html = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 25px; font-size: 0.95em;'>"
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

# --- 主畫面佈局 (動態欄位計算) ---
st.markdown("<style>.block-container { padding-top: 1rem !important; }</style>", unsafe_allow_html=True)

# 顯示同步資訊
current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
st.caption(f"⏱️ 365Scores 直連 | 10s 自動刷新中 | 最後更新：{current_time}")

# 動態生成欄位：維持 2 欄位佈局，實現「下方自動占用」
cols = st.columns(2)

# 根據側邊欄的選擇順序，動態分配到左 (col1) 或右 (col2)
# 如果你選了 NBA, MLB, NPB -> NBA 在左, MLB 在右, NPB 會在左(NBA下面)
for i, league in enumerate(active_leagues):
    with cols[i % 2]:
        if league == "NBA":
            render_html_table("🏀 NBA", get_365_scoreboard('nba', selected_date))
        elif league == "MLB":
            render_html_table("⚾ MLB", get_365_scoreboard('mlb', selected_date))
        elif league == "NPB":
            render_html_table("⚾ NPB (日職)", get_365_scoreboard('npb', selected_date))

# --- 戰情心跳 ---
time.sleep(10)
st.rerun()
