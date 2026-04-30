import requests
from datetime import datetime, timedelta
import pytz

def get_espn_scoreboard(sport, league, target_date):
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    # 為了實現歸位邏輯，我們抓取目標日期與前一天的資料
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
    seen_ids = set() # 避免跨日抓取重複場次

    for ev in all_events:
        if ev['id'] in seen_ids:
            continue
            
        # 1. 解析 UTC 時間並轉換為台灣時間
        utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
        local_dt = utc_time.astimezone(tw_tz)
        
        # 2. 核心邏輯：僅保留台灣日期與使用者選擇日期相同的場次
        if local_dt.date() != target_date:
            continue
            
        seen_ids.add(ev['id'])
        local_time_str = local_dt.strftime('%H:%M')
        
        # 3. 狀態判定
        status_obj = ev['status']['type']
        state = status_obj['state']
        status_text = "已結束" if state == 'post' else ("進行中" if state == 'in' else "預計")
        
        # 顯示更詳細的進度（例如第幾節或局數）
        if state == 'in' and 'detail' in status_obj:
            status_text = status_obj['detail']

        comp = ev['competitions'][0]
        away = comp['competitors'][0]
        home = comp['competitors'][1]
        
        parsed_data.append({
            "Time": local_time_str,
            "Status": status_text,
            "Match": f"{away['team']['displayName']} @ {home['team']['displayName']}",
            "Score": f"{away.get('score', '0')} - {home.get('score', '0')}" if state != 'pre' else "-"
        })
    
    return parsed_data
