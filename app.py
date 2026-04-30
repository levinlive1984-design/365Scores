import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 設定網頁標題
st.set_page_config(page_title="365Scores 自動抓取看板", layout="wide")

def fetch_365scores_data():
    """
    自動從 365Scores 的 API 抓取今日所有賽事
    """
    # 取得今日日期 (格式: DD/MM/YYYY)
    today = datetime.now().strftime("%d/%m/%Y")
    
    # 365Scores 官方 Web API (langId 10 為繁體中文)
    api_url = f"https://webapi.365scores.com/web/games/current/?langId=10&timezoneId=24&userCountryId=6"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(api_url, headers=headers)
        data = response.json()
        games = data.get('games', [])
        competitions = {c['id']: c['name'] for c in data.get('competitions', [])}
        
        parsed_list = []
        for game in games:
            comp_id = game.get('competitionId')
            comp_name = competitions.get(comp_id, "其他")
            
            # 取得對戰組合
            home_team = game.get('homeCompetitor', {}).get('name')
            away_team = game.get('awayCompetitor', {}).get('name')
            
            # 取得狀態與分數
            status = game.get('statusText', '未開始')
            home_score = game.get('homeCompetitor', {}).get('score', 0)
            away_score = game.get('awayCompetitor', {}).get('score', 0)
            
            # 取得開賽時間
            start_time_raw = game.get('startTime')
            start_time = datetime.fromisoformat(start_time_raw.replace('Z', '+00:00')).strftime('%H:%M')
            
            parsed_list.append({
                "Category": comp_name,
                "Time": start_time,
                "Status": status,
                "Match": f"{away_team} vs {home_team}",
                "Score": f"{away_score} - {home_score}" if home_score != -1 else "-",
                "CompID": comp_id
            })
            
        return pd.DataFrame(parsed_list)
    except Exception as e:
        st.error(f"抓取失敗: {e}")
        return pd.DataFrame()

# --- Streamlit 介面 ---
st.title("🚀 365Scores 實時自動抓取系統")
st.write(f"當前系統時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if st.button('立即刷新數據'):
    st.rerun()

all_data = fetch_365scores_data()

if not all_data.empty:
    # 1:1 分類邏輯 (精確匹配 ID 或 名稱)
    # 常用 ID 參考：NBA (7), MLB (10), NPB (17)
    categories = {
        "NBA": all_data[all_data['Category'].str.contains('NBA', na=False)],
        "MLB": all_data[all_data['Category'].str.contains('MLB', na=False)],
        "日本棒球": all_data[all_data['CompID'] == 17],
        "網球": all_data[all_data['Category'].str.contains('網球|ATP|WTA|ITF', na=False)]
    }

    for label, df in categories.items():
        st.header(f"📌 {label}")
        if not df.empty:
            # 按照時間由早到晚排序
            df_sorted = df.sort_values(by="Time")
            st.table(df_sorted[['Time', 'Status', 'Match', 'Score']])
        else:
            st.info(f"目前無 {label} 賽事資訊")
else:
    st.warning("無法取得賽事資料，請檢查網路或 API 狀態。")
