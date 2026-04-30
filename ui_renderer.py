import streamlit as st

def setup_cyber_css():
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; } 
            .update-timestamp { 
                font-family: 'Courier New', monospace; 
                color: #00FF00; background: #111; 
                padding: 3px 10px; border-radius: 4px; 
                border: 1px solid #00FF00;
                box-shadow: 0 0 5px rgba(0,255,0,0.3);
            }
            [data-stale="true"] {
                opacity: 0.1 !important;
                transition: opacity 0.2s ease-in-out !important;
            }
            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important;
                border: none !important;
                color: #d32f2f !important; 
                font-weight: 900 !important;
                font-size: 1.15em !important;
                letter-spacing: 2px !important;
                display: flex !important;
                align-items: center !important;
                padding: 5px 0 !important;
            }
            [data-testid="stSidebar"] .stButton > button::before {
                content: '🔴';
                display: flex; align-items: center; justify-content: center;
                width: 32px; height: 32px; border: 2px solid #111; border-radius: 6px;           
                background-color: #f8f9fa; margin-right: 12px; box-shadow: 3px 3px 0px #111; font-size: 12px;
            }
            [data-testid="stSidebar"] .stButton > button:active::before {
                box-shadow: 0px 0px 0px #111; transform: translate(3px, 3px);
            }
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list):
    if not data_list:
        html = '<div style="margin-bottom: 30px;">'
        html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #f8f9fa; border: 2px solid #555; border-bottom: none; border-radius: 8px 15px 0 0; padding: 6px 18px; font-weight: bold; color: #555;">{title}</div>'
        html += '<div style="position: relative; z-index: 1; border: 2px solid #555; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 20px;">📡 該日期暫無數據</div></div>'
        return html

    html = '<div style="margin-bottom: 30px;">'
    html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #fff; border: 2px solid #222; border-bottom: none; border-radius: 8px 16px 0 0; padding: 6px 20px; font-size: 1.1em; font-weight: 900; color: #111;">{title}</div>'
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
            html += f"<tr style='background-color: #e9ecef; font-weight: bold;'><td colspan='4' style='padding: 6px 12px; border-top: 1px solid #ccc; font-size: 0.85em;'>{current_league}</td></tr>"

        status_style = "color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        status_box = f"<span style='background-color: #eee; color: #777; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;'>{row['Status']}</span>" if row['State'] == 'post' else row['Status']
        
        # 🎯 使用 href='...' 雙引號包單引號，確保網址字串純淨
        match_link = f"<a href='{row['Url']}' target='_blank' style='text-decoration: none; color: inherit; display: block; width: 100%;'>"
        match_link += f"{row['Away']} <span style='color: #dc3545; font-weight: 900; font-size: 0.8em; margin: 0 5px;'>VS</span> {row['Home']}</a>"
            
        html += f"<tr style='border-bottom: 1px solid #eee;'>"
        html += f"<td style='padding: 10px 12px;'>{row['Time']}</td>"
        html += f"<td style='padding: 10px 12px; {status_style}'>{status_box}</td>"
        html += f"<td style='padding: 10px 12px;'>{match_link}</td>"
        html += f"<td style='padding: 10px 12px; font-weight: bold;'>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
