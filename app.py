import streamlit as st
import time
from datetime import datetime
import pytz

# --- 核心模組匯入 ---
from api365_utils import get_365_scoreboard
from ui_renderer import setup_cyber_css, get_table_html

st.set_page_config(page_title="365賽程抓爬網", layout="wide", initial_sidebar_state="expanded")
tw_tz = pytz.timezone('Asia/Taipei')

# 載入純淨版賽博視覺 CSS
setup_cyber_css()

# 狀態記憶初始化
default_toggles = {'toggle_nba':True, 'toggle_mlb':True, 'toggle_npb':False, 'toggle_kbo':False, 'toggle_tennis':False, 'toggle_nhl':False}
for key, val in default_toggles.items():
    if key not in st.session_state: st.session_state[key] = val

def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']: st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']: st.session_state[key] = False

with st.sidebar:
    st.markdown("## 🛰️ 賽程調度中心")
    selected_date = st.date_input("🗓️ 調閱日期", datetime.now(tw_tz).date())
    st.divider()
    st.markdown("### 🔌 板塊撥桿 (Toggle)")
    
    # 移除了容易引發衝突的 on_change，讓 Streamlit 原生接管狀態改變
    show_nba = st.toggle("🏀 NBA", key='toggle_nba')
    show_mlb = st.toggle("⚾ MLB", key='toggle_mlb')
    show_nhl = st.toggle("🏒 NHL", key='toggle_nhl')
    show_npb = st.toggle("⚾ NPB", key='toggle_npb')
    show_kbo = st.toggle("⚾ KBO", key='toggle_kbo')
    show_tennis = st.toggle("🎾 Tennis", key='toggle_tennis')
    
    active_leagues = [L for L, S in zip(
        ["NBA", "MLB", "NHL", "NPB", "KBO", "Tennis"], 
        [show_nba, show_mlb, show_nhl, show_npb, show_kbo, show_tennis]
    ) if S]
    
    st.divider()
    st.button("緊急重置看板", on_click=emergency_reset)

st.markdown(f"⏱️ <span class='update-timestamp'>SYSTEM_LIVE: {datetime.now(tw_tz).strftime('%H:%M:%S')}</span>", unsafe_allow_html=True)

# 建立乾淨的主畫面容器
main_board = st.empty()

with main_board.container():
    if active_leagues:
        # 1. 抓取資料
        league_data = {}
        for league in active_leagues:
            api_id = league.lower().split(' ')[0]
            league_data[league] = get_365_scoreboard(api_id, selected_date)
            
        num_cols = min(len(active_leagues), 3)
        cols = st.columns(num_cols)
        
        # 2. 空間自動填補演算法 (保留你最喜歡的智慧排版)
        col_heights = [0] * num_cols
        col_assignments = [[] for _ in range(num_cols)]
        
        for league in active_leagues:
            data = league_data[league]
            num_games = len(data)
            
            if num_games == 0:
                est_height = 150
            else:
                num_categories = len(set(r['League'] for r in data))
                est_height = 80 + (num_games * 55) + (num_categories * 35)
                
            # 找出最矮的欄位，優先塞進去
            shortest_col_idx = col_heights.index(min(col_heights))
            col_assignments[shortest_col_idx].append(league)
            col_heights[shortest_col_idx] += est_height
            
        # 3. 渲染
        for i in range(num_cols):
            with cols[i]:
                for league in col_assignments[i]:
                    icon = "🏀" if league == "NBA" else "🎾" if league == "Tennis" else "🏒" if league == "NHL" else "⚾"
                    html_content = get_table_html(f"{icon} {league}", league_data[league])
                    st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.warning("📡 請由左側面板啟動賽事數據鏈路...")

time.sleep(10)
st.rerun()
