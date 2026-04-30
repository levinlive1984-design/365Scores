import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    # 針對網球啟動全域掃描 (sports=3)，其餘球種使用精確聯賽 ID
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true"
    else:
        comp_map = {'nba': 103, 'mlb': 438, 'npb': 5482, 'kbo': 7587}
        comp_id = comp_map.get(league_type, 103)
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
            # 雙重防護過濾
            if league_type == 'tennis':
                if game.get('sportId') != 3: continue
            else:
                if game.get('competitionId') != comp_id: continue

            status_group = game.get('statusGroup', 1)
            
            if status_group == 4:
                state = 'post'
                status_text = "已結束"
            elif status_group == 3:
                state = 'in'
                if league_type in ['mlb', 'npb', 'kbo', 'tennis']:
                    status_text = game.get('statusText', '')
                else:
                    status_text = f"{game.get('statusText', '')} {game.get('gameTimeDisplay', '')}".strip()
            else:
                state = 'pre'
                status_text = game.get('statusText', '預計')
                
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            
            # 戰略加強：網球進行中賽事，擷取細部局點 (如 40:15)
            extra_score = ""
            if league_type == 'tennis' and state == 'in':
                for stage in game.get('stages', []):
                    if stage.get('id') == 34:  # ID 34 為當前局點
                        a_pts = int(stage.get('awayCompetitorScore', 0))
                        h_pts = int(stage.get('homeCompetitorScore', 0))
                        extra_score = f" <span style='font-size:0.85em; color:#888;'>({a_pts}:{h_pts})</span>"
            
            start_time_str = game.get('startTime', '')
            time_display = start_time_str[11:16] if len(start_time_str) >= 16 else "--:--"
            
            main_score = f"{int(away.get('score', 0))} - {int(home.get('score', 0))}" if state != 'pre' else "-"
            
            parsed_data.append({
                "Time": time_display,
                "Status": status_text,
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": f"{main_score}{extra_score}" # 盤數 + 局點
            })
        return parsed_data
    except Exception:
        return []
