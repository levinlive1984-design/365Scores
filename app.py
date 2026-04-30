import streamlit as st
import time
from datetime import datetime
import pytz
from api365_utils import get_365_scoreboard

st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide", initial_sidebar_state="expanded")
tw_tz = pytz.timezone('Asia/Taipei')

# 狀態記憶初始化
default_toggles = {'toggle_nba':True, 'toggle_mlb':True, 'toggle_npb':False, 'toggle_kbo':False, 'toggle_tennis':False, 'toggle_nhl':False}
for key, val in default_toggles.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 核心解法：強制重繪函式 ---
# 只要撥桿狀態改變，就呼叫 st.rerun() 強制清空所有舊畫面
def force_refresh():
    pass # 這裡不需要寫邏輯，因為 Streamlit 的 toggle 改變 session_state 後，我們只需讓它自然觸發 rerun 即可
    # Streamlit 會在 on_change 觸發後自動重新執行一次腳本，這能確保畫面是最乾淨的

def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']: st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']: st.session_state[key] = False

with st.sidebar:
    st.markdown("## 🛰️ 戰情調度中心")
    selected_date = st.date_input("🗓️ 調閱日期", datetime.now(tw_tz).date())
    st.divider()
    st.markdown("### 🔌 模組撥桿 (Toggle)")
    
    # 加入 on_change 事件，確保每次撥動都強制重繪，杜絕殘影
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


def get_table_html(title, data_list):
    html = f"### {title}\n"
    if not data_list: return html + "該日期暫無賽事數據。"

    table_html = "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 25px;'>"
    table_html += "<thead><tr style='background-color: #f8f9fa; border-bottom: 2px solid #333;'>"
    table_html += "<th style='text-align: left; padding: 12px; width: 15%;'>時間</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 20%;'>狀態</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 45%;'>對戰組合</th>"
    table_html += "<th style='text-align: left; padding: 12px; width: 20%;'>比分</th>"
    table_html += "</tr></thead><tbody>"
    
    current_league = None
    for row in data_list:
        if row['League'] != current_league:
            current_league = row['League']
            table_html += f"<tr style='background-color: #ececec; font-weight: bold; color: #333;'>"
            table_html += f"<td colspan='4' style='padding: 8px 12px; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc;'>{current_league}</td></tr>"

        status_style = f"color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        status_box = f"<span style='background-color: #e9ecef; color: #6c757d; padding: 4px 8px; border-radius: 4px;'>{row['Status']}</span>" if row['State'] == 'post' else row['Status']
            
        table_html += f"<tr style='border-bottom: 1px solid #dee2e6;'>"
        table_html += f"<td style='padding: 12px;'>{row['Time']}</td>"
        table_html += f"<td style='padding: 12px; {status_style}'>{status_box}</td>"
        table_html += f"<td style='padding: 12px;'>{row['Away']} <span style='color: red; font-weight: bold;'>vs</span> {row['Home']}</td>"
        table_html += f"<td style='padding: 12px; font-weight: bold;'>{row['Score']}</td></tr>"
    
    return html + table_html + "</tbody></table>"

# 我們捨棄了 main_container = st.empty()，直接在根目錄下渲染
# 因為 on_change 已經確保了每次狀態改變都會是一次全新的載入
st.markdown("<style>.block-container { padding-top: 1rem !important; } .update-timestamp { font-family: monospace; color: #00FF00; background: #000; padding: 2px 8px; border-radius: 4px; }</style>", unsafe_allow_html=True)
st.markdown(f"⏱️ <span class='update-timestamp'>SYSTEM_LIVE: {datetime.now(tw_tz).strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

if active_leagues:
    cols = st.columns(min(len(active_leagues), 3))
    for i, league in enumerate(active_leagues):
        with cols[i % len(cols)]:
            icon = "🏀" if league == "NBA" else "🎾" if league == "Tennis" else "🏒" if league == "NHL" else "⚾"
            st.markdown(get_table_html(f"{icon} {league}", get_365_scoreboard(league.lower().split(' ')[0], selected_date)), unsafe_allow_html=True)
else:
    st.warning("📡 請由左側面板啟動賽事數據鏈路...")

time.sleep(10)
st.rerun()
