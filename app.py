import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
# 導入我們建立的模組
from espn_utils import get_espn_scoreboard

# --- 戰情系統初始化 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# 側邊欄資產監控
st.sidebar.markdown(f"### 🛡️ 戰情系統 2.0")
st.sidebar.markdown(f"**當前資產：** 853 元")
st.sidebar.markdown(f"**系統時區：** Asia/Taipei")
st.sidebar.markdown(f"**更新時間：** {datetime.now(tw_tz).strftime('%H:%M:%S')}")

st.title("🏆 體育戰情即時監控中心")

# --- 第一區：穩定抓取區 (NBA & MLB) ---
st.subheader("✅ 穩定數據源 (ESPN)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏀 NBA")
    nba_list = get_espn_scoreboard('basketball', 'nba')
    if nba_list:
        st.table(pd.DataFrame(nba_list).sort_values(by="Time"))
    else:
        st.info("目前無 NBA 賽事")

with col2:
    st.markdown("#### ⚾ MLB")
    mlb_list = get_espn_scoreboard('baseball', 'mlb')
    if mlb_list:
        st.table(pd.DataFrame(mlb_list).sort_values(by="Time"))
    else:
        st.info("目前無 MLB 賽事")

st.divider()

# --- 第二區：研究開發區 (日本職棒 & 網球) ---
st.subheader("🧪 數據抓取研究區 (NPB & Tennis)")

# 這裡我們接下來要填入新的爬蟲邏輯
tab1, tab2 = st.tabs(["⚾ 日本職棒 (NPB)", "🎾 網球 (Tennis)"])

with tab1:
    st.write("🔍 正在研究 NPB 穩定抓取方案...")
    # 預留顯示區
    st.info("目前 NPB 數據抓取測試中，尚未對接。")

with tab2:
    st.write("🔍 正在研究 網球 (ATP/WTA) 全場次抓取方案...")
    st.info("目前網球數據抓取測試中，尚未對接。")
