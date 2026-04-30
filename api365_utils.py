import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    # 邏輯分流：網球使用 sports=3 全域掃描，其餘使用 competitions ID
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true&withTop=true&onlyMajorGames=true"
    else:
        # 新增 NHL = 366 進入核心映射表
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
        games = res.get('games', [])
        
        parsed_data = []
        for game in games:
            # 狀態分級
            status_group = game.get('statusGroup', 1)
            if status_group == 4:
                state, status_text = 'post', "已結束"
            elif status_group == 3:
                state, status_text = 'in', game.get('statusText', '')
            else:
                state, status_text = 'pre', game.get('statusText', '預計')
                
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            
            # 網球專屬局點處理
            extra_score = ""
            if league_type == 'tennis' and state == 'in':
                for stage in game.get('stages', []):
                    if stage.get('id') == 34:
                        extra_score = f" <span style='font-size:0.85em; color:#888;'>({int(away.get('score', 0))}:{int(home.get('score', 0))})</span>"
            
            start_time_str = game.get('startTime', '')
            time_display = start_time_str[11:16] if len(start_time_str) >= 16 else "--:--"
            
            # 將 365Scores 荒謬的 "胚胎移植後" 修正回正常的 "延長賽"
            if status_text == "胚胎移植後":
                status_text = "延長賽 (OT)"
            
            parsed_data.append({
                "League": game.get('competitionDisplayName', '其他賽事'),
                "Time": time_display,
                "Status": status_text,
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": f"{int(away.get('score', 0))} - {int(home.get('score', 0))}{extra_score}" if state != 'pre' else "-"
            })
        return parsed_data
    except Exception:
        return []
