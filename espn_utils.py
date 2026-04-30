import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from espn_utils import get_espn_scoreboard

# --- 戰情系統配置 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 頂部狀態列 ---
st.title("🏆 體育戰情即時監控中心")

# 側邊欄資產資訊
st.sidebar.markdown(f"### 🛡️ 戰情系統 2.0")
st.sidebar.markdown(f"**當前資產：** 853 元")
st.sidebar.markdown(f"**策略版本：** V5.0 (Moneyline/Spread)")

# --- 日期選擇器 (移至主頁面最上方，確保看得到) ---
today_tw = datetime.now(tw_tz).date()
c1, c2 = st.columns([1, 3])
with c1:
    selected_date = st.date_input("📅 選擇調閱日期", today_tw)
with c2:
    st.info(f"📊 目前檢索數據日期：{selected_date.strftime('%Y-%m-%d')} (台北時間)")

# --- 穩定數據區 ---
st.divider()
col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("#### 🏀 NBA")
    nba = get_espn_scoreboard('basketball', 'nba', selected_date)
    if nba:
        st.table(pd.DataFrame(nba).sort_values(by="Time"))
    else:
        st.write("該日期暫無 NBA 賽事數據。")

with col_mlb:
    st.markdown("#### ⚾ MLB")
    mlb = get_espn_scoreboard('baseball', 'mlb', selected_date)
    if mlb:
        st.table(pd.DataFrame(mlb).sort_values(by="Time"))
    else:
        st.write("該日期暫無 MLB 賽事數據。")

# --- 研究開發區 ---
st.divider()
st.subheader("🧪 數據抓取研究區 (NPB & Tennis)")
t_npb, t_tennis = st.tabs(["⚾ 日本職棒 (NPB)", "🎾 網球 (Tennis)"])

with t_npb:
    st.write("🔍 正在嘗試串接 TheScore API 以解決 17:00 開賽數據...")
    st.info("NPB 解析器研發中，目標：1:1 還原日職賽程。")

with t_tennis:
    st.write("🔍 正在研究 ATP/WTA 全場次抓取邏輯...")
    st.info("網球解析器研發中，目標：涵蓋所有 ITF/挑戰賽場次。")
