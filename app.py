import streamlit as st
from datetime import datetime
import pytz
from streamlit_autorefresh import st_autorefresh

# --- 核心模組匯入 ---
from api365_utils import get_365_scoreboard
from ui_renderer import setup_cyber_css, get_table_html

st.set_page_config(page_title="365賽程抓爬網", layout="wide", initial_sidebar_state="expanded")
tw_tz = pytz.timezone('Asia/Taipei')

# 載入 CSS（只需一次）
setup_cyber_css()

# 狀態記憶初始化
default_toggles = {
    'toggle_nba': True,
    'toggle_mlb': True,
    'toggle_npb': False,
    'toggle_kbo': False,
    'toggle_tennis': False,
    'toggle_nhl': False
}
for key, val in default_toggles.items():
    if key not in st.session_state:
        st.session_state[key] = val


def emergency_reset():
    for key in ['toggle_nba', 'toggle_mlb']:
        st.session_state[key] = True
    for key in ['toggle_npb', 'toggle_kbo', 'toggle_tennis', 'toggle_nhl']:
        st.session_state[key] = False


@st.cache_data(ttl=10, show_spinner=False)
def fetch_league_data(active_leagues, selected_date):
    """只快取 10 秒，專門給 live score 使用"""
    result = {}
    for league in active_leagues:
        api_id = league.lower().split(' ')[0]
        result[league] = get_365_scoreboard(api_id, selected_date)
    return result


with st.sidebar:
    st.markdown("## 🛰️ 賽程調度中心")
    selected_date = st.date_input("🗓️ 調閱日期", datetime.now(tw_tz).date())
    st.divider()
    st.markdown("### 🔌 板塊撥桿 (Toggle)")

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

# 局部刷新區塊
scoreboard_container = st.container()

if active_leagues:
    league_data = fetch_league_data(tuple(active_leagues), selected_date)

    # 智慧判斷是否有 live game
    is_live = any(
        row.get("State") == "in"
        for league_rows in league_data.values()
        for row in league_rows
    )

    # 正在比賽 10 秒刷新，否則 60 秒
    refresh_ms = 10000 if is_live else 60000
    st_autorefresh(interval=refresh_ms, key="smart_live_refresh")

    st.markdown(
        f"⏱️ <span class='update-timestamp'>SYSTEM_LIVE: {datetime.now(tw_tz).strftime('%H:%M:%S')} | REFRESH: {refresh_ms//1000}s</span>",
        unsafe_allow_html=True
    )

    with scoreboard_container:
        num_cols = min(len(active_leagues), 3)
        cols = st.columns(num_cols)

        # 空間自動填補演算法
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

        # 只重畫比分區塊
        for i in range(num_cols):
            with cols[i]:
                for league in col_assignments[i]:
                    icon = "🏀" if league == "NBA" else "🎾" if league == "Tennis" else "🏒" if league == "NHL" else "⚾"
                    html_content = get_table_html(f"{icon} {league}", league_data[league])
                    st.markdown(html_content, unsafe_allow_html=True)
else:
    st.warning("📡 請由左側面板啟動賽事數據鏈路...")
