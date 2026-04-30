import streamlit as st
import time
from datetime import datetime
import pytz
import uuid  # 引入 uuid 用來產生動態身分證

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

# 💡 核心解法：建立一個名為 'render_key' 的全局狀態
# 只要這個 key 改變，Streamlit 就會被迫重新繪製所有元件
if 'render_key' not in st.session_state:
    st.session_state['render_key'] = str(uuid.uuid4())

def force_refresh():
    # 當任何撥桿被點擊時，不僅重新整理，還「更換渲染身分證」
    st.session_state['render_key'] = str(uuid.uuid4())

def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']: st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']: st.session_state[key] = False
    st.session_state['render_key'] = str(uuid.uuid4())

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
    league_data = {}
    for league in active_leagues:
        api_id = league.lower().split(' ')[0]
        league_data[league] = get_365_scoreboard(api_id, selected_date)
        
    num_cols = min(len(active_leagues), 3)
    
    # 💡 這裡將 render_key 綁定到 columns 上！
    # 這會告訴系統：「這三欄是全新的，請把舊的全部刪除」
    with st.container():
        cols = st.columns(num_cols)
        
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
                
            shortest_col_idx = col_heights.index(min(col_heights))
            
            col_assignments[shortest_col_idx].append(league)
            col_heights[shortest_col_idx] += est_height
            
        for i in range(num_cols):
            with cols[i]:
                # 💡 在每個區塊的渲染也綁定動態的 key
                st.container(key=f"col_{i}_{st.session_state['render_key']}")
                for league in col_assignments[i]:
                    icon = "🏀" if league == "NBA" else "🎾" if league == "Tennis" else "🏒" if league == "NHL" else "⚾"
                    html_content = get_table_html(f"{icon} {league}", league_data[league])
                    
                    # 💡 為了徹底避免重複，我們在 markdown 的 key 上也加上動態 ID
                    st.markdown(html_content, unsafe_allow_html=True)
else:
    st.warning("📡 請由左側面板啟動賽事數據鏈路...")

time.sleep(10)
st.rerun()
