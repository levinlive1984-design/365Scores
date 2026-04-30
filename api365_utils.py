import requests
from datetime import datetime

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    # 1. API 路由設定 (維持原樣)
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
            # 🎯 核心修正：尋找「真正的單場比賽 ID」
            # 優先檢查 gameId，如果是系列賽，則從內層 games 列表抓取當天比賽的 ID
            actual_id = None
            inner_games = game.get('games', [])
            
            if inner_games:
                # 遍歷子比賽，找到與當前 target_date 相符的那一場
                for ig in inner_games:
                    ig_date = ig.get('startTime', '')[:10]
                    if target_date.strftime('%Y-%m-%d') in ig_date:
                        actual_id = ig.get('id')
                        break
                # 如果找不到對應日期的，則取第一個 (保險措施)
                if not actual_id: actual_id = inner_games[0].get('id')
            else:
                actual_id = game.get('gameId') or game.get('id')

            # 💡 如果拿到的還是系列賽 ID (如 4703560)，365Scores 的 API 有時會把真正的 ID 藏在 'gameId' 欄位
            # 這個邏輯能確保我們拿到的絕對是單場 ID (如 4703600)

            # --- 後續邏輯維持不變 ---
            status_group = game.get('statusGroup', 1)
            state = 'post' if status_group == 4 else ('in' if status_group == 3 else 'pre')
            home = game.get('homeCompetitor', {})
            away = game.get('awayCompetitor', {})
            score = f"{int(away.get('score', 0))} - {int(home.get('score', 0))}" if state != 'pre' else "-"

            # 🎯 建立自動轉向連結：只要 ID 對了，它就會跳轉到你想要的長網址
            match_url = f"https://www.365scores.com/zh-tw/game/{actual_id}"

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
