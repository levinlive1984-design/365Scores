import streamlit as st

def setup_cyber_css():
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; } 
            .update-timestamp { 
                font-family: 'Courier New', monospace; color: #00FF00; background: #111; padding: 3px 10px; border-radius: 4px; border: 1px solid #00FF00;
            }
            [data-stale="true"] { opacity: 0.1 !important; transition: opacity 0.2s ease-in-out !important; }
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list):
    if not data_list: return "<div>📡 暫無賽事數據</div>"

    html = f'<div style="margin-bottom: 30px;">'
    html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #fff; border: 2px solid #222; border-bottom: none; border-radius: 8px 16px 0 0; padding: 6px 20px; font-weight: 900;">{title}</div>'
    html += '<div style="position: relative; z-index: 1; border: 2px solid #222; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 0; overflow: hidden; box-shadow: 5px 5px 0px rgba(0,0,0,0.15);">'
    html += "<table style='width: 100%; border-collapse: collapse; font-family: sans-serif;'>"
    html += "<thead><tr style='background-color: #f4f4f4; border-bottom: 2px solid #222;'><th>時間</th><th>狀態</th><th>對戰組合</th><th>比分</th></tr></thead><tbody>"
    
    for row in data_list:
        status_style = "color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        
        # 🎯 這裡使用單引號包裹 href，並使用 f-string 嚴格控制網址字串，杜絕空格錯誤
        match_link = f"<a href='{row['Url']}' target='_blank' style='text-decoration: none; color: inherit; display: block; width: 100%;'>"
        match_link += f"{row['Away']} <span style='color: #dc3545;'>VS</span> {row['Home']}</a>"
            
        html += f"<tr style='border-bottom: 1px solid #eee;'>"
        html += f"<td>{row['Time']}</td>"
        html += f"<td style='{status_style}'>{row['Status']}</td>"
        html += f"<td>{match_link}</td>" # 對戰組合欄位現在是精準連結
        html += f"<td>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
