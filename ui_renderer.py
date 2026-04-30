import streamlit as st

def setup_cyber_css():
    """賽博龐克 CSS 與優化版的過渡動畫"""
    st.markdown("""
        <style>
            .block-container { padding-top: 4rem !important; } 
            
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
                font-size: 1.15em !important;
                letter-spacing: 2px !important;
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
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list):
    """生成帶有「戰術資料夾頁籤」外框的 HTML 賽事表"""
    
    if not data_list:
        html = '<div style="margin-bottom: 30px;">'
        html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #f8f9fa; border: 2px solid #555; border-bottom: none; border-radius: 8px 15px 0 0; padding: 6px 18px; font-weight: bold; color: #555; letter-spacing: 1px;">{title}</div>'
        html += '<div style="position: relative; z-index: 1; border: 2px solid #555; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 20px; box-shadow: 4px 4px 0px rgba(0,0,0,0.05);">'
        html += '📡 該日期暫無賽事數據，鏈路待命。'
        html += '</div></div>'
        return html

    html = '<div style="margin-bottom: 30px;">'
    html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #fff; border: 2px solid #222; border-bottom: none; border-radius: 8px 16px 0 0; padding: 6px 20px; font-size: 1.1em; font-weight: 900; color: #111; letter-spacing: 1px; box-shadow: 2px -2px 0px rgba(0,0,0,0.05);">{title}</div>'
    html += '<div style="position: relative; z-index: 1; border: 2px solid #222; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 0; overflow: hidden; box-shadow: 5px 5px 0px rgba(0,0,0,0.15);">'
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

        status_style = "color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        status_box = f"<span style='background-color: #eee; color: #777; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;'>{row['Status']}</span>" if row['State'] == 'post' else row['Status']
        
        match_url = row.get('URL', '')
        vs_span = "<span style='color: #dc3545; font-weight: 900; font-size: 0.8em; margin: 0 5px;'>VS</span>"
        match_text = f"{row['Away']} {vs_span} {row['Home']}"

        if match_url:
            a_style = 'color:inherit;text-decoration:none;display:block'
            a_over  = "this.style.color='#1a73e8'"
            a_out   = "this.style.color='inherit'"
            arrow   = '<span style="font-size:0.75em;color:#bbb;margin-left:4px">↗</span>'
            match_html = (
                f'<a href="{match_url}" target="_blank" rel="noopener" '
                f'style="{a_style}" '
                f'onmouseover="{a_over}" '
                f'onmouseout="{a_out}">'
                f'{match_text} {arrow}</a>'
            )
        else:
            match_html = match_text

        html += "<tr style='border-bottom: 1px solid #eee;'>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em;'>{row['Time']}</td>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em; {status_style}'>{status_box}</td>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em;'>{match_html}</td>"
        html += f"<td style='padding: 10px 12px; font-weight: bold; font-size: 1.05em;'>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
