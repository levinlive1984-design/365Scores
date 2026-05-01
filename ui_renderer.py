import streamlit as st

def setup_cyber_css():
    """賽博龐克 CSS 與優化版的過渡動畫"""
    st.markdown("""
        <style>
            .block-container { padding-top: 4rem !important; }

            /* ── 側邊欄內距縮減（不動寬度，避免自動收起）── */
            [data-testid="stSidebar"] > div:first-child {
                padding: 1rem 0.7rem 1rem 0.7rem !important;
            }

            /* 標題縮小 */
            [data-testid="stSidebar"] h2 {
                font-size: 0.95em !important;
                margin-bottom: 0.3rem !important;
            }
            [data-testid="stSidebar"] h3 {
                font-size: 0.8em !important;
                margin-bottom: 0.2rem !important;
                color: #888 !important;
                letter-spacing: 0.05em !important;
            }

            /* Toggle 文字縮小 + 行距壓縮 */
            [data-testid="stSidebar"] .stToggle label {
                font-size: 0.82em !important;
            }
            [data-testid="stSidebar"] .stToggle {
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }

            /* 日期選取壓縮 */
            [data-testid="stSidebar"] .stDateInput label {
                font-size: 0.78em !important;
                margin-bottom: 0 !important;
            }
            [data-testid="stSidebar"] .stDateInput input {
                font-size: 0.82em !important;
                padding: 4px 8px !important;
            }

            /* divider 間距壓縮 */
            [data-testid="stSidebar"] hr {
                margin: 0.4rem 0 !important;
            }
            
            /* 電子鐘樣式 */
            .update-timestamp { 
                font-family: 'Courier New', monospace; 
                color: #00FF00; 
                background: #111; 
                padding: 3px 10px; 
                border-radius: 4px; 
                border: 1px solid #00FF00;
                box-shadow: 0 0 5px rgba(0,255,0,0.3);
            }
            
            /* 幽靈過渡術：微閃即逝的殘影 */
            [data-stale="true"] {
                opacity: 0.1 !important;
                transition: opacity 0.2s ease-in-out !important;
            }
            
            /* 🔴 緊急重置開關：實體工業風 (Kill Switch) */
            /* 1. 消除 Streamlit 預設按鈕外觀，設定文字樣式 */
            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #d32f2f !important; /* 警告紅文字 */
                font-weight: 900 !important;
                font-size: 0.8em !important;
                letter-spacing: 1px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                padding: 5px 0 !important;
                transition: all 0.2s ease !important;
            }

            /* 2. 滑鼠懸浮時文字微動，增加操作手感 */
            [data-testid="stSidebar"] .stButton > button:hover {
                color: #ff0000 !important;
                transform: translateX(4px);
            }

            /* 3. 繪製獨立的「黑框白底紅圈」硬體按鈕圖示 */
            [data-testid="stSidebar"] .stButton > button::before {
                content: '🔴';
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
                border: 2px solid #111;       /* 粗黑外框 */
                border-radius: 6px;           /* 微圓角 */
                background-color: #f8f9fa;    /* 淺灰白底色 */
                margin-right: 12px;           /* 與文字的距離 */
                font-size: 12px;
                box-shadow: 3px 3px 0px #111; /* 賽博風無機質硬陰影 */
                transition: all 0.1s ease;
            }

            /* 4. 按下時的物理回饋 (按鈕被壓下去的感覺) */
            [data-testid="stSidebar"] .stButton > button:active::before {
                box-shadow: 0px 0px 0px #111;
                transform: translate(3px, 3px);
            }

            /* 5. 比賽列 hover 效果（純 CSS，避開 Streamlit JS 沙盒限制）*/
            tr.match-row:hover {
                background-color: #eef4ff !important;
                cursor: pointer;
            }
            tr.match-row:hover .match-cell {
                color: #1a73e8 !important;
            }
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list, selected_date=None):
    """生成帶有「戰術資料夾頁籤」外框的 HTML 賽事表，頁籤右側附 📋 複製即將開始賽程按鈕"""
    import re as _re

    # 過濾出「即將開始」的賽程，準備複製用文字
    pre_rows = [r for r in data_list if r.get('State') == 'pre']
    if pre_rows:
        lines = []
        for r in pre_rows:
            date_str = r.get('Date', '')
            lines.append(f"{date_str} {r['Time']} {r['Away']} vs {r['Home']}")
        copy_text = "\\n".join(lines).replace("`", "\\`").replace("${", "\\${")
        btn_id = "cpbtn_" + _re.sub(r'[^a-zA-Z0-9]', '_', title)
        copy_btn = (
            f'<button id="{btn_id}" '
            f'onclick="(function(){{'
            f'navigator.clipboard.writeText(`{copy_text}`).then(function(){{'
            f'var b=document.getElementById(\'{btn_id}\');'
            f'b.textContent=\'✅\';b.style.background=\'#22c55e\';b.style.color=\'#fff\';'
            f'setTimeout(function(){{b.textContent=\'📋\';b.style.background=\'#f8f9fa\';b.style.color=\'#333\';}},1500);'
            f'}});}})();" '
            f'title="複製 {len(pre_rows)} 場即將開始賽程" '
            f'style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:30px;height:30px;border:2px solid #222;border-radius:5px;'
            f'background:#f8f9fa;color:#333;font-size:13px;cursor:pointer;'
            f'box-shadow:2px 2px 0px #111;margin-left:10px;padding:0;flex-shrink:0;'
            f'vertical-align:middle;line-height:1;">'
            f'📋</button>'
        )
    else:
        copy_btn = ''

    if not data_list:
        html = '<div style="margin-bottom: 30px;">'
        html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #f8f9fa; border: 2px solid #555; border-bottom: none; border-radius: 8px 15px 0 0; padding: 6px 18px; font-weight: bold; color: #555; letter-spacing: 1px;">{title}</div>'
        html += '<div style="position: relative; z-index: 1; border: 2px solid #555; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 20px; box-shadow: 4px 4px 0px rgba(0,0,0,0.05);">'
        html += '📡 該日期暫無賽事數據，鏈路待命。'
        html += '</div></div>'
        return html

    html = '<div style="margin-bottom: 30px;">'
    html += (
        f'<div style="display:inline-flex;align-items:center;position:relative;top:2px;z-index:2;'
        f'background-color:#fff;border:2px solid #222;border-bottom:none;'
        f'border-radius:8px 16px 0 0;padding:6px 16px 6px 24px;font-size:1.1em;font-weight:900;'
        f'color:#111;letter-spacing:1px;box-shadow:2px -2px 0px rgba(0,0,0,0.05);min-width:140px;">'
        f'{title}{copy_btn}</div>'
    )
    html += "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif;'>"
    html += "<thead><tr style='background-color: #f4f4f4; border-bottom: 2px solid #222;'>"
    html += "<th style='text-align: left; padding: 10px 12px; width: 15%; font-size: 0.9em; color: #555;'>時間</th>"
    html += "<th style='text-align: left; padding: 10px 12px; width: 20%; font-size: 0.9em; color: #555;'>狀態</th>"
    html += "<th style='text-align: left; padding: 10px 12px; width: 45%; font-size: 0.9em; color: #555;'>對戰組合</th>"
    html += "<th style='text-align: left; padding: 10px 12px; width: 20%; font-size: 0.9em; color: #555;'>比分</th>"
    html += "</tr></thead><tbody>"
    
    current_league = None
    for row in data_list:
        if row['League'] != current_league:
            current_league = row['League']
            html += "<tr style='background-color: #e9ecef; font-weight: bold; color: #222;'>"
            html += f"<td colspan='4' style='padding: 6px 12px; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; font-size: 0.85em;'>{current_league}</td></tr>"

        if row['State'] == 'in':
            status_style = ""
            # 紅色粗體顯示節次 + 時間，例如「第二節 00:07」
            status_box = "<span style='color:#dc3545;font-weight:700;font-size:0.92em;white-space:nowrap;'>" + row['Status'] + "</span>"
        elif row['State'] == 'post':
            status_style = ""
            status_box = "<span style='background-color: #eee; color: #777; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;'>" + row['Status'] + "</span>"
        else:
            status_style = ""
            status_box = row['Status']

        
        match_url = row.get('URL', '')
        vs_span = "<span style='color: #dc3545; font-weight: 900; font-size: 0.8em; margin: 0 5px;'>VS</span>"
        serving = row.get('Serving', '')
        serve_dot = "<span style='display:inline-block;width:0;height:0;border-top:5px solid transparent;border-bottom:5px solid transparent;border-right:8px solid #22c55e;margin-right:5px;vertical-align:middle;'></span>"
        away_name = row['Away'] + (serve_dot if serving == 'away' else '')
        home_name = row['Home'] + (serve_dot if serving == 'home' else '')
        match_text = f"{away_name} {vs_span} {home_name}"

        if match_url:
            a_style = 'color:inherit;text-decoration:none;display:block'
            match_html = (
                f'<a href="{match_url}" target="_blank" rel="noopener" '
                f'style="{a_style}">'
                f'{match_text}</a>'
            )
        else:
            match_html = match_text

        html += "<tr class='match-row' style='border-bottom: 1px solid #eee;'>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em;'>{row['Time']}</td>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em; {status_style}'>{status_box}</td>"
        html += f"<td class='match-cell' style='padding: 10px 12px; font-size: 0.95em;'>{match_html}</td>"
        html += f"<td style='padding: 10px 12px; font-weight: bold; font-size: 1.05em;'>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
