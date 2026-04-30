import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    target_date_iso = target_date.strftime('%Y-%m-%d')
    
    # 1. API 路由設定
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true&withTop=true&onlyMajorGames=true"
    else:
        comp_map = {'nba': 103, 'mlb': 438, 'npb': 5482, 'kbo': 7587, 'nhl': 366}
        comp_id = comp_map.get(league_type, 103)
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&competitions={comp_id}&startDate={date_str}&endDate={date_str}&showOdds=true"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        games = res.get('games', [])
        parsed_data = []
        
        for game in games:
            # 🎯 核心修復：精準獵殺「單場 ID」
            actual_game_id = None
            
            # 季後賽模式：比賽會嵌套在 'games' 列表內
            inner_games = game.get('games', [])
            if inner_games:
                for ig in inner_games:
                    # 檢查這場子比賽的日期是否為我們選擇的 target_date
                    if target_date_iso in ig.get('startTime', ''):
                        actual_game_id = ig.get('id')
                        break
                # 如果日期匹配失敗，退而求其次抓第一個
                if not actual_game_id: actual_game_id = inner_games[0].get('id')
            else:
                # 常規賽模式：直接使用頂層 ID 或 gameId
                actual_game_id = game.get('gameId') or game.get('id')

            # 抓取運動種類路徑 (用於連結跳轉)
            sport_id = game.get('sportId')
            sport_path_map = {1: 'football', 2: 'basketball', 3: 'tennis', 4: 'hockey'}
            sport_path = sport_path_map.get(sport_id, 'football')

            # --- 數據解析 ---
            status_group = game.get('statusGroup', 1)
            state = 'post' if status_group == 4 else ('in' if status_group == 3 else 'pre')
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            score = f"{int(away.get('score', 0))} - {int(home.get('score', 0))}" if state != 'pre' else "-"

            # 🎯 建立「終極跳轉網址」：使用單場 ID 配合 redirect 模式
            # 只要這個 ID 是 4703600，365Scores 就會自動帶你去正確的詳情頁
            match_url = f"https://www.365scores.com/zh-tw/match/redirect#id={actual_game_id}"

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
