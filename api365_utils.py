import requests
from datetime import datetime
import pytz

def get_365_scoreboard(sport_type, target_date):
    # 365Scores 運動代碼對應：籃球=2, 棒球=5
    sport_id_map = {'nba': 2, 'mlb': 5}
    sport_id = sport_id_map.get(sport_type, 2)
    
    # 365Scores 要求的日期格式為 DD/MM/YYYY
    date_str = target_date.strftime('%d/%m/%Y')
    
    # 核心 API URL，直接鎖定 Asia/Taipei 時區與 zh-tw 語言
    url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports={sport_id}&startDate={date_str}&endDate={date_str}&showOdds=true&onlyMajorGames=true&withTop=true"
    
    # 偽裝成瀏覽器，突破基本的防禦機制
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Origin': 'https://www.365scores.com',
        'Referer': 'https://www.365scores.com/'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        games = res.get('games', [])
        
        parsed_data = []
        for game in games:
            # 狀態分級：4 為結束, 3 為進行中
            status_group = game.get('statusGroup', 1)
            
            if status_group == 4:
                state = 'post'
                status_text = game.get('statusText', '已結束')
            elif status_group == 3:
                state = 'in'
                # 精確捕捉進行中的節數與時間 (例如：第3節 02:54)
                status_text = f"{game.get('statusText', '')} {game.get('gameTimeDisplay', '')}".strip()
            else:
                state = 'pre'
                status_text = game.get('statusText', '預計')
                
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            
            # 時間處理：API 的 startTime 格式如 2026-04-30T10:00:00+08:00
            start_time_str = game.get('startTime', '')
            time_display = start_time_str[11:16] if len(start_time_str) >= 16 else "--:--"
            
            parsed_data.append({
                "Time": time_display,
                "Status": status_text,
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": f"{int(away.get('score', 0))} - {int(home.get('score', 0))}" if state != 'pre' else "-"
            })
            
        return parsed_data
    except Exception as e:
        return []
