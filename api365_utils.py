import requests
from datetime import datetime

# 運動類型對應路徑
SPORT_PATH = {
    'nba': 'basketball', 'mlb': 'baseball', 'npb': 'baseball',
    'kbo': 'baseball',   'nhl': 'hockey',   'tennis': 'tennis'
}

def _slug(name):
    """把球隊名稱轉成 URL slug，例如 Detroit Pistons → detroit-pistons"""
    import re
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

def _build_match_url(league_type, comp_id, away, home, game_id, comp_slug=None):
    """組合出 365scores 比賽頁超連結
    comp_slug: 可手動傳入（網球用），否則自動用 league_type-comp_id
    """
    sport  = SPORT_PATH.get(league_type, 'sport')
    c_slug = comp_slug if comp_slug else f"{league_type}-{comp_id}"
    teams  = f"{_slug(away.get('name',''))}-{_slug(home.get('name',''))}"
    ids    = f"{away.get('id','')}-{home.get('id','')}-{comp_id}"
    return f"https://www.365scores.com/zh-tw/{sport}/match/{c_slug}/{teams}-{ids}#id={game_id}"

def get_365_scoreboard(league_type, target_date):
    date_str = target_date.strftime('%d/%m/%Y')
    
    if league_type == 'tennis':
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&sports=3&startDate={date_str}&endDate={date_str}&showOdds=true"
    else:
        comp_map = {'nba': 103, 'mlb': 438, 'npb': 5482, 'kbo': 7587, 'nhl': 366}
        comp_id = comp_map.get(league_type)
        if comp_id is None:
            return []  # 未知聯賽，明確回傳空清單，不亂顯示假資料
        url = f"https://webws.365scores.com/web/games/allscores/?appTypeId=5&langId=199&timezoneName=Asia%2FTaipei&userCountryId=163&competitions={comp_id}&startDate={date_str}&endDate={date_str}&showOdds=true"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9',
        'Origin': 'https://www.365scores.com',
        'Referer': 'https://www.365scores.com/'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10).json()
        
        # --- 戰略級過濾：建立網球賽事血統圖譜 ---
        country_dict = {c['id']: c.get('name', '') for c in res.get('countries', [])}
        comp_tour_dict = {}
        comp_slug_dict = {}  # comp_id → URL slug（例如 240 → "madrid"）
        for comp in res.get('competitions', []):
            cid = comp['id']
            comp_tour_dict[cid] = country_dict.get(comp.get('countryId'), '')
            # 優先用 nameForURL，沒有就從 name 自己 slug
            raw = comp.get('nameForURL') or comp.get('name', '')
            comp_slug_dict[cid] = _slug(raw.split(' - ')[0]) if raw else str(cid)
            
        games = res.get('games', [])
        parsed_data = []
        
        for game in games:
            if league_type == 'tennis':
                if game.get('sportId') != 3: continue
                
                # 取得該比賽的真實血統 (ATP, WTA)
                tour_type = comp_tour_dict.get(game.get('competitionId'), '')
                
                # 絕對鐵血紀律：不是 ATP 也不是 WTA 的賽事，一律捨棄不顯示
                if 'ATP' not in tour_type and 'WTA' not in tour_type:
                    continue
                    
                # 重組分類橫桿名稱：捨棄後面的 " - Round of 16" 等贅字
                # 組合出乾淨俐落的 "ATP - Madrid"
                raw_name = game.get('competitionDisplayName', '網球賽事')
                clean_name = raw_name.split(' - ')[0] 
                league_display_name = f"{tour_type} - {clean_name}"
                
            else:
                if game.get('competitionId') != comp_id: continue
                league_display_name = game.get('competitionDisplayName', '其他賽事')

            status_group = game.get('statusGroup', 1)
            
            if status_group == 4:
                state, status_text = 'post', "已結束"
            elif status_group == 3:
                state = 'in'
                period = game.get('statusText', '')
                clock  = game.get('gameTime', '') or game.get('clock', '')
                # 組合「第二節 00:07」，沒有時間就只顯示節次
                status_text = f"{period} {clock}".strip() if clock else period
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
            
            if status_text == "胚胎移植後":
                status_text = "延長賽 (OT)"
            
            # 組合比賽超連結
            game_id  = game.get('id', '')
            if league_type == 'tennis':
                t_comp_id = game.get('competitionId', '')
                t_slug    = f"{comp_slug_dict.get(t_comp_id, str(t_comp_id))}-{t_comp_id}"
                match_url = _build_match_url('tennis', t_comp_id, away, home, game_id, comp_slug=t_slug)
            else:
                match_url = _build_match_url(league_type, comp_id, away, home, game_id)

            parsed_data.append({
                "League": league_display_name,
                "Time": time_display,
                "Status": status_text,
                "State": state,
                "Away": away.get('name', 'TBD'),
                "Home": home.get('name', 'TBD'),
                "Score": f"{int(away.get('score', 0))} - {int(home.get('score', 0))}{extra_score}" if state != 'pre' else "-",
                "URL": match_url
            })
        return parsed_data
    except Exception:
        return []
