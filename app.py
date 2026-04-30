import streamlit as st
import time
from datetime import datetime
import pytz

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

def force_refresh():
    pass 

def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']: st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']: st.session_state[key] = False

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
    # 1. 戰情預載：先抓取所有已啟動模組的數據
    league_data = {}
    for league in active_leagues:
        api_id = league.lower().split(' ')[0] # 將字串轉成 api 的代號 (nba, mlb)
        league_data[league] = get_365_scoreboard(api_id, selected_date)
        
    # 2. 動態計算欄位數量 (最多 3 欄)
    num_cols = min(len(active_leagues), 3)
    cols = st.columns(num_cols)
    
    # 3. 🎯 核心邏輯升級：空間自動填補演算法 (Greedy Allocation)
    col_heights = [0] * num_cols
    col_assignments = [[] for _ in range(num_cols)]
    
    for league in active_leagues:
        data = league_data[league]
        num_games = len(data)
        
        # 依照賽事數量，精準估算這張表在螢幕上會佔用多少「高度 (px)」
        if num_games == 0:
            est_height = 150 # 無賽事空殼的高度
        else:
            num_categories = len(set(r['League'] for r in data))
            # 基礎框體高度 + 每場比賽高度 + 分類橫桿高度
            est_height = 80 + (num_games * 55) + (num_categories * 35)
            
        # 掃描雷達：找出目前高度最矮 (最空) 的欄位
        shortest_col_idx = col_heights.index(min(col_heights))
        
        # 將該球種指派給最空的欄位，並將高度累加進去
        col_assignments[shortest_col_idx].append(league)
        col_heights[shortest_col_idx] += est_height
        
    # 4. 依照智能分配的結果渲染畫面
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
