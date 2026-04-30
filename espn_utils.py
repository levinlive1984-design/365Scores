import requests
from datetime import datetime, timedelta
import pytz

def get_espn_scoreboard(sport, league, target_date):
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    # 雙日抓取邏輯：抓取目標日與前一日，確保台灣時間 00:00 - 23:59 的比賽都能歸位
    date_list = [target_date - timedelta(days=1), target_date]
    all_events = []
    
    for d in date_list:
        params = {'dates': d.strftime('%Y%m%d')}
        try:
            res = requests.get(url, params=params, timeout=10).json()
            all_events.extend(res.get('events', []))
        except:
            continue

    parsed_data = []
    seen_ids = set()

    for ev in all_events:
        if ev['id'] in seen_ids:
            continue
            
        # 時間解析與時區歸位
        utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
        local_dt = utc_time.astimezone(tw_tz)
        
        # 過濾出確實落在台灣日期當天的場次
        if local_dt.date() != target_date:
            continue
            
        seen_ids.add(ev['id'])
        local_time_str = local_dt.strftime('%H:%M')
        
        # 狀態判定
        status_obj = ev['status']['type']
        state = status_obj['state']
        status_text = "已結束" if state == 'post' else ("進行中" if state == 'in' else "預計")
        
        if state == 'in' and 'detail' in status_obj:
            status_text = status_obj['detail']

        comp = ev['competitions'][0]
        away = comp['competitors'][0]['team']['displayName']
        home = comp['competitors'][1]['team']['displayName']
        
        # 比分處理
        away_score = comp['competitors'][0].get('score', '0')
        home_score = comp['competitors'][1].get('score', '0')

        parsed_data.append({
            "Time": local_time_str,
            "Status": status_text,
            "Match": f"{away} vs {home}",  # 已從 @ 改為 vs
            "Score": f"{away_score} - {home_score}" if state != 'pre' else "-"
        })
    
    return parsed_data
