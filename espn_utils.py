import requests
from datetime import datetime
import pytz

def get_espn_scoreboard(sport, league):
    """
    從 ESPN 抓取指定的賽事數據
    """
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    try:
        res = requests.get(url, timeout=10).json()
        events = res.get('events', [])
        parsed_data = []
        
        for ev in events:
            # 1. 時間解析與轉換
            utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
            local_time = utc_time.astimezone(tw_tz).strftime('%H:%M')
            
            # 2. 狀態判定 (改用 state 狀態機，更精確)
            state = ev['status']['type']['state'] # pre, in, post
            if state == 'post':
                status_text = "已結束"
            elif state == 'in':
                status_text = "進行中"
            elif state == 'pre':
                status_text = "預計"
            else:
                status_text = ev['status']['type']['description']

            # 3. 隊伍與比分
            comp = ev['competitions'][0]
            away = comp['competitors'][0]
            home = comp['competitors'][1]
            
            # 取得比分，若尚未開始則顯示 "-"
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
