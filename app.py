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
    # 獲取正確的台北今日日期
    now_tw = datetime.now(tw_tz)
    selected_date = st.date_input("📅 調閱賽事日期", now_tw.date())

# --- 主頁面 ---
st.title("🏆 體育戰情即時監控中心")
st.success(f"📊 目前調閱日期：**{selected_date.strftime('%Y-%m-%d')}** (台灣時間)")

# 重要提示：關於台美換日線
if selected_date == now_tw.date() and now_tw.hour < 14:
    st.warning("💡 提示：台灣上午正在進行的 NBA/MLB 賽事（如你截圖所示），在美國 API 中歸類於前一天。若搜尋不到特定早場比賽，請將日期往前調閱一天。")

st.divider()

# --- 穩定數據區 (NBA & MLB) ---
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
        st.write("該日期暫無 MLB 數據。")

# --- 研究開發區 ---
st.divider()
st.subheader("🧪 數據抓取研究區 (NPB & Tennis)")
t_npb, t_tennis = st.tabs(["⚾ 日本職棒 (NPB)", "🎾 網球 (Tennis)"])

with t_npb:
    st.write("正在開發對接新的數據接口，解決 17:00 開賽的日本職棒問題...")

with t_tennis:
    st.write("正在開發全場次網球解析器...")
