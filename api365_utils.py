import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    # 核心降維打擊：精確鎖定「聯賽 ID (Competition ID)」
    # 103 = NBA, 438 = MLB
    comp_id = 103 if league_type == 'nba' else 438
    
    # 移除了大範圍的 sports 參數，改用 competitions 精確索取
    url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&competitions={comp_id}&startDate={date_str}&endDate={date_str}&showOdds=true"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Origin': 'https://www.365scores.com',
        'Referer': 'https://www.365scores.com/'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        games = res.get('games', [])
        
        parsed_data = []
        for game in games:
            # 雙重防護：過濾掉任何非指定聯賽的雜訊 (以防 API 塞入廣告賽事)
            if game.get('competitionId') != comp_id:
                continue

            status_group = game.get('statusGroup', 1)
            
            # 狀態邏輯 (4:已結束, 3:進行中, 1/2:預計)
            if status_group == 4:
                state = 'post'
                status_text = game.get('statusText', '已結束')
            elif status_group == 3:
                state = 'in'
                status_text = f"{game.get('statusText', '')} {game.get('gameTimeDisplay', '')}".strip()
            else:
                state = 'pre'
                status_text = game.get('statusText', '預計')
                
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            
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
