import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true&withTop=true&onlyMajorGames=true"
    else:
        comp_map = {'nba': 103, 'mlb': 438, 'npb': 5482, 'kbo': 7587, 'nhl': 366}
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
        country_dict = {c['id']: c.get('name', '') for c in res.get('countries', [])}
        comp_tour_dict = {comp['id']: country_dict.get(comp.get('countryId'), '') for comp in res.get('competitions', [])}
            
        games = res.get('games', [])
        parsed_data = []
        
        for game in games:
            game_id = game.get('id')
            sport_id = game.get('sportId')
            
            if league_type == 'tennis':
                if sport_id != 3: continue
                tour_type = comp_tour_dict.get(game.get('competitionId'), '')
                if 'ATP' not in tour_type and 'WTA' not in tour_type: continue
                league_display_name = f"{tour_type} - {game.get('competitionDisplayName', '').split(' - ')[0]}"
            else:
                league_display_name = game.get('competitionDisplayName', '其他賽事')

            status_group = game.get('statusGroup', 1)
            if status_group == 4:
                state, status_text = 'post', "已結束"
            elif status_group == 3:
                state, status_text = 'in', game.get('statusText', '')
            else:
                state, status_text = 'pre', game.get('statusText', '預計')
            
            if status_text == "胚胎移植後": status_text = "延長賽 (OT)"
                
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            
            extra_score = ""
            if sport_id == 3 and state == 'in':
                for stage in game.get('stages', []):
                    if stage.get('id') == 34:
                        extra_score = f" ({int(away.get('score', 0))}:{int(home.get('score', 0))})"
            
            score_display = f"{int(away.get('score', 0))} - {int(home.get('score', 0))}{extra_score}" if state != 'pre' else "-"

            # 🎯 終極修正：使用 365Scores 萬用跳轉網址，並使用 .strip() 確保絕對沒有空格
            match_url = f"https://www.365scores.com/game/{game_id}".strip()

            parsed_data.append({
                "League": league_display_name,
                "Time": (game.get('startTime', '')[11:16] if len(game.get('startTime', '')) >= 16 else "--:--"),
                "Status": status_text,
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": score_display,
                "Url": match_url
            })
        return parsed_data
    except Exception:
        return []
