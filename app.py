import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from espn_utils import get_espn_scoreboard

# --- 戰情系統初始化 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄：基礎資訊 ---
st.sidebar.markdown(f"### 🛡️ 戰情系統 2.0")
st.sidebar.markdown(f"**當前資產：** 853 元")
st.sidebar.markdown(f"**策略版本：** V5.0 (Cross-ball)")

# --- 主頁面日期選擇區 ---
st.title("🏆 體育戰情即時監控中心")

# 將日期選擇器放在主頁面頂部，確保 100% 可見
selected_date = st.date_input("📅 請選擇欲調閱的賽事日期", datetime.now(tw_tz).date())
st.success(f"🔍 目前調閱日期：**{selected_date.strftime('%Y-%m-%d')}**")

st.divider()

# --- 穩定數據區 (NBA & MLB) ---
col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("#### 🏀 NBA")
    nba = get_espn_scoreboard('basketball', 'nba', selected_date)
    if nba:
        st.table(pd.DataFrame(nba).sort_values(by="Time"))
    else:
        st.write("該日期暫無 NBA 數據。")

with col_mlb:
    st.markdown("#### ⚾ MLB")
    mlb = get_espn_scoreboard('baseball', 'mlb', selected_date)
    if mlb:
        st.table(pd.DataFrame(mlb).sort_values(by="Time"))
    else:
        st.write("該日期暫無 MLB 數據。")

# --- 研究開發區 ---
st.divider()
st.subheader("🧪 數據抓取研究區 (NPB & Tennis)")
t_npb, t_tennis = st.tabs(["⚾ 日本職棒 (NPB)", "🎾 網球 (Tennis)"])

with t_npb:
    st.write("正在開發對接 TheScore API，解決日本職棒數據涵蓋問題...")

with t_tennis:
    st.write("正在開發全場次網球解析器...")
