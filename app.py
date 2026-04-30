import streamlit as st
from datetime import datetime
import pytz
from espn_utils import get_espn_scoreboard

st.set_page_config(page_title="Gemini 體育戰情系統 2.0", layout="wide")
tw_tz = pytz.timezone('Asia/Taipei')

with st.sidebar:
    st.markdown("### 📅 賽事管理")
    selected_date = st.date_input("調閱賽事日期 (台灣時間)", datetime.now(tw_tz).date())
    st.divider()

st.title("🏆 體育戰情即時監控中心")
st.success(f"📊 目前顯示：**{selected_date.strftime('%Y-%m-%d')}** (全日台灣時間賽程)")

# --- 強制 HTML 渲染引擎 (若你看到英文標題，代表這段沒被執行) ---
def render_html_table(data_list):
    if not data_list:
        st.write("該日期暫無賽事數據。")
        return

    # 直接寫死 CSS 樣式在 HTML 內，強制瀏覽器聽話
    html = """
    <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; margin-bottom: 20px;">
        <thead>
            <tr style="background-color: #f8f9fa; border-bottom: 2px solid #333;">
                <th style="text-align: left; padding: 12px; width: 10%;">時間</th>
                <th style="text-align: left; padding: 12px; width: 20%;">狀態</th>
                <th style="text-align: left; padding: 12px; width: 50%;">對戰組合</th>
                <th style="text-align: left; padding: 12px; width: 20%;">比分</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for row in data_list:
        # 狀態處理
        if row['State'] == 'post':
            status_html = f'<span style="background-color: #e9ecef; color: #6c757d; padding: 4px 8px; border-radius: 4px; font-size: 0.9em;">{row["Status"]}</span>'
        elif row['State'] == 'in':
            status_html = f'<span style="color: #dc3545; font-weight: bold;">{row["Status"]}</span>'
        else:
            status_html = row['Status']
            
        # 對戰組合處理 (vs 紅字)
        match_html = f"{row['Away']} <span style='color: red; font-weight: bold; margin: 0 5px;'>vs</span> {row['Home']}"
            
        html += f"""
        <tr style="border-bottom: 1px solid #dee2e6;">
            <td style="padding: 12px;">{row['Time']}</td>
            <td style="padding: 12px;">{status_html}</td>
            <td style="padding: 12px;">{match_html}</td>
            <td style="padding: 12px; font-weight: bold;">{row['Score']}</td>
        </tr>
        """
    html += "</tbody></table>"
    
    # 這是渲染關鍵
    st.markdown(html, unsafe_allow_html=True)

st.divider()
col_nba, col_mlb = st.columns(2)

with col_nba:
    st.markdown("### 🏀 NBA")
    nba_data = get_espn_scoreboard('basketball', 'nba', selected_date)
    render_html_table(nba_data)

with col_mlb:
    st.markdown("### ⚾ MLB")
    mlb_data = get_espn_scoreboard('baseball', 'mlb', selected_date)
    render_html_table(mlb_data)
