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

# --- 側邊欄：戰略調度中心 ---
with st.sidebar:
    st.markdown("## 🛡️ 戰情調度中心")
    selected_date = st.date_input("調閱日期", datetime.now(tw_tz).date())
    st.divider()
    
    # 擴展後的選單，預先加入 KBO 與 網球 待命
    active_leagues = st.multiselect(
        "看板顯示內容",
        ["NBA", "MLB", "NPB", "KBO (韓職)", "Tennis (網球)"],
        default=["NBA", "MLB"],
        help="勾選後，畫面將自動調整欄位數量與位置"
    )

# --- 頁面主體預留區 (防止殘影) ---
main_container = st.empty()

# --- HTML 渲染引擎 ---
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

# --- 戰情邏輯與顯示 ---
with main_container.container():
    st.markdown("<style>.block-container { padding-top: 1rem !important; }</style>", unsafe_allow_html=True)
    
    current_time = datetime.now(tw_tz).strftime('%H:%M:%S')
    st.caption(f"⏱️ 直連 365Scores | 每 10s 自動更新 | 最後更新：{current_time}")

    # --- 關鍵修正：彈性網格佈局 ---
    num_leagues = len(active_leagues)
    
    if num_leagues > 0:
        # 動態計算欄位：如果是 1 個就 1 欄，如果是 2 個以上，為了版面美觀，最多切成 3 欄
        # 這能徹底解決「塞不下往下擠」的殘影問題
        num_cols = min(num_leagues, 3) 
        cols = st.columns(num_cols)

        for i, league in enumerate(active_leagues):
            # 確保內容正確對應到對應的欄位，超過 3 個則自動折行到下一排
            with cols[i % num_cols]:
                if league == "NBA":
                    st.markdown(get_table_html("🏀 NBA", get_365_scoreboard('nba', selected_date)), unsafe_allow_html=True)
                elif league == "MLB":
                    st.markdown(get_table_html("⚾ MLB", get_365_scoreboard('mlb', selected_date)), unsafe_allow_html=True)
                elif league == "NPB":
                    st.markdown(get_table_html("⚾ NPB (日職)", get_365_scoreboard('npb', selected_date)), unsafe_allow_html=True)
                # 這裡預留了 KBO 與 網球的接孔，未來你抓到 ID 後就能直接填入
                elif league == "KBO (韓職)":
                    st.markdown("*(等待 KBO 模組接上)*", unsafe_allow_html=True)
                elif league == "Tennis (網球)":
                    st.markdown("*(等待網球模組接上)*", unsafe_allow_html=True)

# --- 戰情心跳 ---
time.sleep(10)
st.rerun()
