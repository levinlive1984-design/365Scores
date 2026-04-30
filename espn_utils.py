import requests
from datetime import datetime
import pytz

def get_espn_scoreboard(sport, league, target_date=None):
    """
    從 ESPN 抓取指定賽事與日期的數據
    """
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    # 透過參數指定日期 YYYYMMDD
    params = {}
    if target_date:
        params['dates'] = target_date.strftime('%Y%m%d')
    
    try:
        res = requests.get(url, params=params, timeout=10).json()
        events = res.get('events', [])
        parsed_data = []
        
        for ev in events:
            # 1. 時間轉換
            utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            # 2. 狀態判定 (使用 state 欄位避開 description 誤差)
            # state 類型: pre (預計), in (進行中), post (已結束)
            state = ev['status']['type']['state']
            if state == 'post':
                status_text = "已結束"
            elif state == 'in':
                status_text = "進行中"
            else:
                status_text = "預計"

            comp = ev['competitions'][0]
            away = comp['competitors'][0]
            home = comp['competitors'][1]
            
            # 3. 比分獲取
            away_score = away.get('score', '0')
            home_score = home.get('score', '0')

            parsed_data.append({
                "Time": local_time,
                "Status": status_text,
                "Match": f"{away['team']['displayName']} @ {home['team']['displayName']}",
                "Score": f"{away_score} - {home_score}" if state != 'pre' else "-"
            })
        return parsed_data
    except:
        return []
