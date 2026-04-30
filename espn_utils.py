import requests
from datetime import datetime, timedelta
import pytz

def get_espn_scoreboard(sport, league, target_date):
    tw_tz = pytz.timezone('Asia/Taipei')
    url = f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard"
    
    # 執行雙日抓取確保台灣時間歸位
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
        if ev['id'] in seen_ids: continue
        utc_time = datetime.strptime(ev['date'], "%Y-%m-%dT%H:%MZ").replace(tzinfo=pytz.utc)
        local_dt = utc_time.astimezone(tw_tz)
        
        # 僅保留台灣日期當天的場次
        if local_dt.date() != target_date: continue
        seen_ids.add(ev['id'])
        
        status_obj = ev['status']['type']
        state = status_obj['state']
        status_text = "已結束" if state == 'post' else ("進行中" if state == 'in' else "預計")
        
        # 若是進行中，顯示詳細進度（如 Top 9th）
        if state == 'in' and 'detail' in status_obj:
            status_text = status_obj['detail']

        comp = ev['competitions'][0]
        away = comp['competitors'][0]['team']['displayName']
        home = comp['competitors'][1]['team']['displayName']
        
        # 建立 Match HTML
        vs_html = f"{away} <span style='color:red; font-weight:bold;'>vs</span> {home}"
        
        parsed_data.append({
            "Time": local_dt.strftime('%H:%M'),
            "Status": status_text,
            "State": state,
            "Match": vs_html,
            "Score": f"{comp['competitors'][0].get('score', '0')} - {comp['competitors'][1].get('score', '0')}" if state != 'pre' else "-"
        })
    return parsed_data
