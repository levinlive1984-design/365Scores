import requests
from datetime import datetime, timedelta
import pytz

def get_espn_scoreboard(sport, league, target_date):
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
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
            
        utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
        local_dt = utc_time.astimezone(tw_tz)
        
        if local_dt.date() != target_date:
            continue
            
        seen_ids.add(ev['id'])
        local_time_str = local_dt.strftime('%H:%M')
        
        status_obj = ev['status']['type']
        state = status_obj['state']
        
        # 狀態處理邏輯
        status_text = "已結束" if state == 'post' else ("進行中" if state == 'in' else "預計")
        if state == 'in' and 'detail' in status_obj:
            status_text = status_obj['detail']

        comp = ev['competitions'][0]
        away = comp['competitors'][0]['team']['displayName']
        home = comp['competitors'][1]['team']['displayName']
        
        away_score = comp['competitors'][0].get('score', '0')
        home_score = comp['competitors'][1].get('score', '0')

        # 針對 vs 顏色與 Status 邏輯在 DataFrame 顯示時處理
        parsed_data.append({
            "Time": local_time_str,
            "Status": status_text,
            "State": state, # 用於後續判斷底色
            "Match": f"{away} <span style='color:red;'>vs</span> {home}",
            "Score": f"{away_score} - {home_score}" if state != 'pre' else "-"
        })
    
    return parsed_data
