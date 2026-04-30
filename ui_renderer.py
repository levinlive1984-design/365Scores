import streamlit as st

def setup_cyber_css():
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; } 
            .update-timestamp { font-family: 'Courier New', monospace; color: #00FF00; background: #111; padding: 3px 10px; border-radius: 4px; }
            [data-stale="true"] { opacity: 0.1 !important; transition: opacity 0.2s ease-in-out !important; }
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list):
    if not data_list: return "<div>📡 無數據</div>"

    html = f'<div style="margin-bottom: 30px;">'
    html += f'<div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #fff; border: 2px solid #222; border-bottom: none; border-radius: 8px 16px 0 0; padding: 6px 20px; font-weight: 900;">{title}</div>'
    html += '<div style="position: relative; z-index: 1; border: 2px solid #222; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 0; overflow: hidden; box-shadow: 5px 5px 0px rgba(0,0,0,0.15);">'
    html += "<table style='width: 100%; border-collapse: collapse;'>"
    html += "<tr style='background-color: #f4f4f4; border-bottom: 2px solid #222;'><th>時間</th><th>狀態</th><th>對戰組合</th><th>比分</th></tr>"
    
    for row in data_list:
        status_style = "color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        
        # 🎯 嚴格鎖定連結字串，不留任何讓瀏覽器誤判的空格
        match_link = f"<a href='{row['Url']}' target='_blank' style='text-decoration: none; color: inherit; display: block;'>"
        match_link += f"{row['Away']} <span style='color: #dc3545;'>VS</span> {row['Home']}</a>"
            
        html += f"<tr style='border-bottom: 1px solid #eee;'>"
        html += f"<td>{row['Time']}</td>"
        html += f"<td style='{status_style}'>{row['Status']}</td>"
        html += f"<td>{match_link}</td>"
        html += f"<td>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
