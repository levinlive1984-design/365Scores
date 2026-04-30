import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    target_iso = target_date.strftime('%Y-%m-%d')
    
    # 1. API 路由設定 (維持系統 5.0 規格)
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true&withTop=true&onlyMajorGames=true"
    else:
        comp_map = {'nba': 103, 'mlb': 438, 'npb': 5482, 'kbo': 7587, 'nhl': 366}
        comp_id = comp_map.get(league_type, 103)
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&competitions={comp_id}&startDate={date_str}&endDate={date_str}&showOdds=true"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        games = res.get('games', [])
        parsed_data = []
        
        for game in games:
            # 🎯 核心修復：獵殺單場比賽 ID
            actual_game_id = None
            inner_games = game.get('games', []) # 檢查是否有系列賽子列表
            
            if inner_games:
                # 遍歷子比賽，找到日期相符的那一場 (例如活塞隊 4/30 那場)
                for ig in inner_games:
                    if target_iso in ig.get('startTime', ''):
                        actual_game_id = ig.get('id') # 這就會抓到 4703600
                        break
                if not actual_game_id: actual_game_id = inner_games[0].get('id')
            else:
                actual_game_id = game.get('id')

            # --- 數據解析 (維持戰情系統 2.0 邏輯) ---
            status_group = game.get('statusGroup', 1)
            state = 'post' if status_group == 4 else ('in' if status_group == 3 else 'pre')
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            score = f"{int(away.get('score', 0))} - {int(home.get('score', 0))}" if state != 'pre' else "-"

            # 🎯 建立「終極自動跳轉網址」
            # 只要 ID 是正確的單場 ID，這個連結會自動 301 跳轉到你要的那串長網址
            match_url = f"https://www.365scores.com/zh-tw/game/{actual_game_id}"

            parsed_data.append({
                "League": game.get('competitionDisplayName', ''),
                "Time": (game.get('startTime', '')[11:16] if len(game.get('startTime', '')) >= 16 else "--:--"),
                "Status": game.get('statusText', ''),
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": score,
                "Url": match_url
            })
        return parsed_data
    except Exception:
        return []
