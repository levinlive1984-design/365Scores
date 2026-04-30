import requests
from datetime import datetime
import pytz

def get_espn_scoreboard(sport, league, target_date=None):
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    params = {}
    if target_date:
        params['dates'] = target_date.strftime('%Y%m%d')
        
    try:
        res = requests.get(url, params=params, timeout=10).json()
        events = res.get('events', [])
        parsed_data = []
        
        for ev in events:
            # 時間解析
            utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            # 狀態判定
            state = ev['status']['type']['state']
            status_text = "已結束" if state == 'post' else ("進行中" if state == 'in' else "預計")
            
            comp = ev['competitions'][0]
            away = comp['competitors'][0]
            home = comp['competitors'][1]
            
            # 比分處理
            away_score = away.get('score', '0')
            home_score = home.get('score', '0')

            parsed_data.append({
                "Time": local_time,
                "Status": status_text,
                "Match": f"{away['team']['displayName']} @ {home['team']['displayName']}",
                "Score": f"{away_score} - {home_score}" if state != 'pre' else "-"
            })
        return parsed_data
    except Exception as e:
        return []
