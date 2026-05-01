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

def get_table_html(title, data_list):
    """生成完整獨立 HTML（含 <style>），供 components.html() 使用。
    回傳 (html_str, estimated_height)"""
    import json, re as _re

    # ── 複製按鈕資料 ──
    pre_rows = [r for r in data_list if r.get('State') == 'pre']
    copy_lines = [f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}" for r in pre_rows]
    copy_text_json = json.dumps("\n".join(copy_lines))
    btn_id = "cpbtn_" + _re.sub(r'[^a-zA-Z0-9]', '_', title)

    if pre_rows:
        copy_btn = (
            f'<button id="{btn_id}" class="copy-btn">📋</button>'
        )
        copy_script = f"""
        <script>
        document.getElementById('{btn_id}').onclick = function() {{
            var text = {copy_text_json};
            navigator.clipboard.writeText(text).then(function() {{
                var b = document.getElementById('{btn_id}');
                b.textContent = '✅';
                b.style.background = '#22c55e';
                b.style.color = '#fff';
                setTimeout(function() {{
                    b.textContent = '📋';
                    b.style.background = '#f8f9fa';
                    b.style.color = '#333';
                }}, 2000);
            }});
        }};
        </script>
        """
    else:
        copy_btn = ''
        copy_script = ''

    # ── 空資料 ──
    if not data_list:
        body = f"""
        <div class="tab-label">{title}</div>
        <div class="card-empty">📡 該日期暫無賽事數據，鏈路待命。</div>
        """
        rows_html = ''
        est_height = 120
    else:
        # ── 表格列 ──
        rows_html = ""
        current_league = None
        for row in data_list:
            if row['League'] != current_league:
                current_league = row['League']
                rows_html += f"<tr class='league-header'><td colspan='4'>{current_league}</td></tr>"

            if row['State'] == 'in':
                status_box = f"<span class='status-live'>{row['Status']}</span>"
            elif row['State'] == 'post':
                status_box = f"<span class='status-post'>{row['Status']}</span>"
            else:
                status_box = row['Status']

            vs_span = "<span class='vs'>VS</span>"
            serving = row.get('Serving', '')
            serve_dot = "<span class='serve-dot'></span>"
            away_name = row['Away'] + (serve_dot if serving == 'away' else '')
            home_name = row['Home'] + (serve_dot if serving == 'home' else '')
            match_text = f"{away_name} {vs_span} {home_name}"

            match_url = row.get('URL', '')
            if match_url:
                match_cell = f'<a href="{match_url}" target="_blank" rel="noopener" class="match-link">{match_text}</a>'
            else:
                match_cell = match_text

            rows_html += f"""
            <tr class='match-row'>
                <td class='col-time'>{row['Time']}</td>
                <td class='col-status'>{status_box}</td>
                <td class='col-match'>{match_cell}</td>
                <td class='col-score'>{row['Score']}</td>
            </tr>"""

        num_games = len(data_list)
        num_cats  = len(set(r['League'] for r in data_list))
        # 每列高度更寬裕，加上頁籤+表頭+底部 padding
        est_height = 60 + 44 + (num_cats * 38) + (num_games * 56) + 24
        body = f"""
        <div class="tab-row">
            <div class="tab-label">{title}{copy_btn}</div>
        </div>
        <div class="card">
            <table>
                <thead>
                    <tr>
                        <th class='col-time'>時間</th>
                        <th class='col-status'>狀態</th>
                        <th class='col-match'>對戰組合</th>
                        <th class='col-score'>比分</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>"""

    # 自動量高腳本：渲染後把實際 scrollHeight 傳給父頁面
    auto_height_script = """
<script>
function _expandFrame() {
    var h = document.body.scrollHeight || document.documentElement.scrollHeight;
    try {
        window.parent.postMessage({type:'streamlit:setFrameHeight', height: h + 20}, '*');
    } catch(e) {}
    try {
        var frames = window.parent.document.querySelectorAll('iframe');
        for (var i = 0; i < frames.length; i++) {
            if (frames[i].contentWindow === window) {
                frames[i].style.height = (h + 20) + 'px';
                frames[i].style.minHeight = (h + 20) + 'px';
                break;
            }
        }
    } catch(e) {}
}
document.addEventListener('DOMContentLoaded', _expandFrame);
window.addEventListener('load', _expandFrame);
setTimeout(_expandFrame, 100);
setTimeout(_expandFrame, 400);
if (window.ResizeObserver) {
    new ResizeObserver(function() { setTimeout(_expandFrame, 50); }).observe(document.body);
}
</script>"""

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: sans-serif; background: transparent; padding: 4px 2px 8px 2px; overflow: hidden; }}

        .tab-row {{ display: flex; align-items: flex-end; }}
        .tab-label {{
            display: inline-flex; align-items: center;
            position: relative; top: 2px; z-index: 2;
            background: #fff;
            border: 2px solid #222; border-bottom: none;
            border-radius: 8px 16px 0 0;
            padding: 6px 16px 6px 20px;
            font-size: 1.05em; font-weight: 900;
            color: #111; letter-spacing: 1px;
            box-shadow: 2px -2px 0px rgba(0,0,0,0.05);
            min-width: 120px;
        }}
        .card {{
            position: relative; z-index: 1;
            border: 2px solid #222;
            border-radius: 0 8px 8px 8px;
            background: #fff;
            box-shadow: 4px 4px 0px rgba(0,0,0,0.07);
            overflow: hidden;
        }}
        .card-empty {{
            border: 2px solid #555;
            border-radius: 0 8px 8px 8px;
            padding: 20px; color: #888;
        }}
        table {{ width: 100%; border-collapse: collapse; }}
        thead tr {{ background: #f4f4f4; border-bottom: 2px solid #222; }}
        th {{ text-align: left; padding: 10px 12px; font-size: 0.88em; color: #555; font-weight: 600; }}
        td {{ padding: 10px 12px; font-size: 0.93em; vertical-align: middle; }}
        .col-time   {{ width: 14%; white-space: nowrap; }}
        .col-status {{ width: 20%; }}
        .col-match  {{ width: 46%; }}
        .col-score  {{ width: 20%; font-weight: 700; font-size: 1.0em; white-space: nowrap; }}

        tr.league-header td {{
            background: #e9ecef; font-weight: 700; color: #222;
            font-size: 0.84em; padding: 6px 12px;
            border-top: 1px solid #ccc; border-bottom: 1px solid #ccc;
        }}
        tr.match-row {{ border-bottom: 1px solid #eee; }}
        tr.match-row:hover {{ background: #eef4ff; cursor: pointer; }}
        tr.match-row:hover .col-match {{ color: #1a73e8; }}

        .status-live {{ color: #dc3545; font-weight: 700; font-size: 0.92em; white-space: nowrap; }}
        .status-post {{ background: #eee; color: #777; padding: 3px 6px; border-radius: 4px; font-size: 0.85em; }}
        .vs {{ color: #dc3545; font-weight: 900; font-size: 0.8em; margin: 0 4px; }}
        .serve-dot {{
            display: inline-block; width: 0; height: 0;
            border-top: 5px solid transparent; border-bottom: 5px solid transparent;
            border-right: 8px solid #22c55e;
            margin: 0 4px; vertical-align: middle;
        }}
        .match-link {{ color: inherit; text-decoration: none; }}
        .match-link:hover {{ color: #1a73e8; }}

        .copy-btn {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px;
            border: 2px solid #222; border-radius: 5px;
            background: #f8f9fa; color: #333;
            font-size: 13px; cursor: pointer;
            box-shadow: 2px 2px 0px #111;
            margin-left: 8px; padding: 0; flex-shrink: 0;
            transition: all 0.1s ease;
        }}
        .copy-btn:active {{ box-shadow: 0 0 0 #111; transform: translate(2px,2px); }}
    </style>
    {body}
    {copy_script}
    {auto_height_script}
    """
    # est_height 給足夠寬裕的初始值，之後由 JS 動態修正
    # 用較大係數避免第一幀就截斷
    return full_html, est_height + 80
