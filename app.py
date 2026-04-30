import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
from espn_utils import get_espn_scoreboard

# --- 戰情系統配置 ---
st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

# --- 側邊欄：僅保留日期調閱 ---
with st.sidebar:
    st.markdown("### 🛡️ 戰情系統 2.0")
    # 根據你的指令，資產與版本資訊在後端運行
    # 當前資產: 853 元, 策略: V5.0
    now_tw = datetime.now(tw_tz)
    selected_date = st.date_input("📅 調閱賽事日期 (台灣時間)", now_tw.date())

# --- 主頁面 ---
st.title("🏆 體育戰情即時監控中心")
st.success(f"📊 目前顯示：**{selected_date.strftime('%Y-%m-%d')}** (全日台灣時間賽程)")

st.divider()

# --- 數據顯示區 ---
col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("#### 🏀 NBA")
    # 此處已套用自動日期歸位邏輯
    nba = get_espn_scoreboard('basketball', 'nba', selected_date)
    if nba:
        st.table(pd.DataFrame(nba).sort_values(by="Time"))
    else:
        st.write("該日期暫無台灣時間賽事。")

with col_mlb:
    st.markdown("#### ⚾ MLB")
    mlb = get_espn_scoreboard('baseball', 'mlb', selected_date)
    if mlb:
        st.table(pd.DataFrame(mlb).sort_values(by="Time"))
    else:
        st.write("該日期暫無台灣時間賽事。")

# 頁尾資訊
st.sidebar.divider()
st.sidebar.caption(f"資產狀況：853 元") #
st.sidebar.caption(f"策略版本：V5.0") #
