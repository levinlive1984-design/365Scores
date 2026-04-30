import streamlit as st

def setup_cyber_css():
    """封裝所有賽博龐克風格與系統核心 CSS"""
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem !important; } 
            
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
            
            /* 視覺抹除術：防止殘影 */
            [data-stale="true"] { opacity: 0 !important; display: none !important; }
            div[data-testid="stVerticalBlock"] { transition: opacity 0s !important; }
        </style>
    """, unsafe_allow_html=True)

def get_table_html(title, data_list):
    """生成帶有「戰術資料夾頁籤」外框的 HTML 賽事表"""
    
    # --- 無資料時的空殼樣式 ---
    if not data_list:
        return f"""
        <div style="margin-bottom: 30px;">
            <div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #f8f9fa; border: 2px solid #555; border-bottom: none; border-radius: 8px 15px 0 0; padding: 6px 18px; font-weight: bold; color: #555; letter-spacing: 1px;">
                {title}
            </div>
            <div style="position: relative; z-index: 1; border: 2px solid #555; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 20px; box-shadow: 4px 4px 0px rgba(0,0,0,0.05);">
                📡 該日期暫無賽事數據，鏈路待命。
            </div>
        </div>
        """

    # --- 戰術頁籤外框設計 ---
    # 利用 top: 2px 與 z-index 讓頁籤完美與下方的邊框融合，形成資料夾視覺
    html = f"""
    <div style="margin-bottom: 30px;">
        <!-- 頁籤標題 (Tab) -->
        <div style="display: inline-block; position: relative; top: 2px; z-index: 2; background-color: #fff; border: 2px solid #222; border-bottom: none; border-radius: 8px 16px 0 0; padding: 6px 20px; font-size: 1.1em; font-weight: 900; color: #111; letter-spacing: 1px; box-shadow: 2px -2px 0px rgba(0,0,0,0.05);">
            {title}
        </div>
        
        <!-- 主資料夾框體 (Container) -->
        <div style="position: relative; z-index: 1; border: 2px solid #222; border-radius: 0 8px 8px 8px; background-color: #fff; padding: 0; overflow: hidden; box-shadow: 5px 5px 0px rgba(0,0,0,0.15);">
            <table style='width: 100%; border-collapse: collapse; font-family: sans-serif;'>
                <thead>
                    <tr style='background-color: #f4f4f4; border-bottom: 2px solid #222;'>
                        <th style='text-align: left; padding: 10px 12px; width: 15%; font-size: 0.9em; color: #555;'>時間</th>
                        <th style='text-align: left; padding: 10px 12px; width: 20%; font-size: 0.9em; color: #555;'>狀態</th>
                        <th style='text-align: left; padding: 10px 12px; width: 45%; font-size: 0.9em; color: #555;'>對戰組合</th>
                        <th style='text-align: left; padding: 10px 12px; width: 20%; font-size: 0.9em; color: #555;'>比分</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    current_league = None
    for row in data_list:
        # 分類橫桿
        if row['League'] != current_league:
            current_league = row['League']
            html += f"<tr style='background-color: #e9ecef; font-weight: bold; color: #222;'>"
            html += f"<td colspan='4' style='padding: 6px 12px; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; font-size: 0.85em;'>{current_league}</td></tr>"

        # 狀態顏色
        status_style = f"color: #dc3545; font-weight: bold;" if row['State'] == 'in' else ""
        status_box = f"<span style='background-color: #eee; color: #777; padding: 3px 6px; border-radius: 4px; font-size: 0.85em;'>{row['Status']}</span>" if row['State'] == 'post' else row['Status']
        
        # 賽博風 "VS" 標示
        match_html = f"{row['Away']} <span style='color: #dc3545; font-weight: 900; font-size: 0.8em; margin: 0 5px;'>VS</span> {row['Home']}"
            
        html += f"<tr style='border-bottom: 1px solid #eee;'>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em;'>{row['Time']}</td>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em; {status_style}'>{status_box}</td>"
        html += f"<td style='padding: 10px 12px; font-size: 0.95em;'>{match_html}</td>"
        html += f"<td style='padding: 10px 12px; font-weight: bold; font-size: 1.05em;'>{row['Score']}</td></tr>"
    
    html += "</tbody></table></div></div>"
    return html
