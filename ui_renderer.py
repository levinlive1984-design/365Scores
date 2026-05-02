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
            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important;
                border: none !important;
                box-shadow: none !important;
                color: #d32f2f !important;
                font-weight: 900 !important;
                font-size: 0.8em !important;
                letter-spacing: 1px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                padding: 5px 0 !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover {
                color: #ff0000 !important;
                transform: translateX(4px);
            }
            [data-testid="stSidebar"] .stButton > button::before {
                content: '🔴';
                display: flex;
                align-items: center;
                justify-content: center;
                width: 32px;
                height: 32px;
                border: 2px solid #111;
                border-radius: 6px;
                background-color: #f8f9fa;
                margin-right: 12px;
                font-size: 12px;
                box-shadow: 3px 3px 0px #111;
                transition: all 0.1s ease;
            }
            [data-testid="stSidebar"] .stButton > button:active::before {
                box-shadow: 0px 0px 0px #111;
                transform: translate(3px, 3px);
            }

            /* 比賽列 hover 效果 */
            tr.match-row:hover {
                background-color: #eef4ff !important;
                cursor: pointer;
            }
            tr.match-row:hover .match-cell {
                color: #1a73e8 !important;
            }
        </style>
    """, unsafe_allow_html=True)


def get_memo_html(league_data):
    """
    生成浮動備忘錄抽屜 HTML（浮動按鈕 + 右側滑入抽屜）。
    透過 st.markdown(..., unsafe_allow_html=True) 注入主頁面 DOM。
    """
    import json, re as _re

    LEAGUE_ICONS = {
        "NBA": "🏀", "MLB": "⚾", "NHL": "🏒",
        "NPB": "⚾", "KBO": "⚾", "Tennis": "🎾"
    }

    # ── 收集各板塊即將開始的比賽，依板塊分群 ──
    groups = []
    for league, rows in league_data.items():
        pre_rows = [r for r in rows if r.get('State') == 'pre']
        if pre_rows:
            icon = LEAGUE_ICONS.get(league, '🏟️')
            groups.append((league, icon, pre_rows))

    # ── 產生抽屜內容 ──
    if not groups:
        inner_html = "<div class='memo-empty'>📭 目前無即將開始的比賽</div>"
    else:
        inner_html = ""
        for league, icon, pre_rows in groups:
            # 整組複製文字
            group_lines = [
                f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}"
                for r in pre_rows
            ]
            group_text_json = json.dumps("\n".join(group_lines))
            group_btn_id = "grp_" + _re.sub(r'[^a-zA-Z0-9]', '_', league)

            # 個別比賽列
            rows_html = ""
            for i, r in enumerate(pre_rows):
                line = f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}"
                line_json = json.dumps(line)
                row_btn_id = f"row_{_re.sub(r'[^a-zA-Z0-9]', '_', league)}_{i}"
                rows_html += f"""
                <div class='memo-row'>
                    <span class='memo-match'>{r.get('Date','')} {r['Time']}&nbsp;&nbsp;{r['Away']} vs {r['Home']}</span>
                    <button class='memo-copy-btn' id='{row_btn_id}'
                        onclick='copyMemo({line_json}, "{row_btn_id}")'>📋</button>
                </div>"""

            inner_html += f"""
            <div class='memo-group'>
                <div class='memo-group-header'>
                    <span>{icon} {league}</span>
                    <button class='memo-copy-btn' id='{group_btn_id}'
                        onclick='copyMemo({group_text_json}, "{group_btn_id}")'>📋</button>
                </div>
                <div class='memo-group-body'>{rows_html}</div>
            </div>"""

    return f"""
<style>
/* ── 浮動按鈕 ── */
#memo-fab {{
    position: fixed;
    top: 58px;
    right: 18px;
    z-index: 9999;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: #fff;
    border: 2px solid #222;
    box-shadow: 3px 3px 0px #111;
    cursor: pointer;
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s ease;
    padding: 0;
}}
#memo-fab:hover {{
    background: #f0f4ff;
    transform: translate(-1px, -1px);
    box-shadow: 4px 4px 0px #111;
}}

/* ── 右側抽屜 ── */
#memo-drawer {{
    position: fixed;
    top: 0;
    right: 0;
    width: 360px;
    height: 100vh;
    background: #fff;
    border-left: 2px solid #222;
    box-shadow: -6px 0 24px rgba(0,0,0,0.13);
    z-index: 9998;
    transform: translateX(100%);
    transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}}
#memo-drawer.open {{
    transform: translateX(0);
}}

/* ── 抽屜標頭 ── */
.memo-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-bottom: 2px solid #222;
    font-weight: 900;
    font-size: 1.0em;
    letter-spacing: 0.5px;
    background: #f8f9fa;
    flex-shrink: 0;
}}
.memo-close {{
    width: 32px;
    height: 32px;
    border: 2px solid #222;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
    font-size: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 2px 2px 0px #111;
    transition: all 0.1s ease;
    font-weight: 900;
    padding: 0;
}}
.memo-close:active {{
    box-shadow: 0 0 0 #111;
    transform: translate(2px, 2px);
}}

/* ── 抽屜內容 ── */
.memo-body {{
    flex: 1;
    overflow-y: auto;
    padding: 12px 14px;
    background: #fafafa;
}}
.memo-empty {{
    color: #aaa;
    text-align: center;
    padding: 48px 0;
    font-size: 0.95em;
}}

/* ── 板塊群組 ── */
.memo-group {{
    margin-bottom: 12px;
    border: 2px solid #222;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
    box-shadow: 2px 2px 0px rgba(0,0,0,0.06);
}}
.memo-group-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #f0f0f0;
    padding: 8px 12px;
    font-weight: 800;
    font-size: 0.9em;
    border-bottom: 1px solid #ddd;
    letter-spacing: 0.3px;
}}

/* ── 比賽列 ── */
.memo-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid #eee;
    gap: 8px;
}}
.memo-row:last-child {{
    border-bottom: none;
}}
.memo-match {{
    flex: 1;
    color: #333;
    font-size: 0.86em;
    line-height: 1.5;
    font-family: "SF Mono", "Fira Code", monospace;
}}

/* ── 複製按鈕（共用） ── */
.memo-copy-btn {{
    flex-shrink: 0;
    width: 28px;
    height: 28px;
    border: 1.5px solid #bbb;
    border-radius: 5px;
    background: #f8f9fa;
    cursor: pointer;
    font-size: 13px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.1s ease;
    padding: 0;
    box-shadow: 1px 1px 0px #ccc;
}}
.memo-copy-btn:hover {{
    background: #e8f0fe;
    border-color: #4a90d9;
}}
.memo-copy-btn:active {{
    transform: scale(0.92);
    box-shadow: none;
}}
</style>

<!-- 浮動按鈕 -->
<button id="memo-fab" onclick="toggleMemo()" title="開啟即將開始備忘錄">📝</button>

<!-- 右側抽屜 -->
<div id="memo-drawer">
    <div class="memo-header">
        <span>📋 即將開始備忘錄</span>
        <button class="memo-close" onclick="toggleMemo()" title="關閉">✕</button>
    </div>
    <div class="memo-body">
        {inner_html}
    </div>
</div>

<script>
function toggleMemo() {{
    document.getElementById('memo-drawer').classList.toggle('open');
}}

function copyMemo(text, btnId) {{
    navigator.clipboard.writeText(text).then(function() {{
        var b = document.getElementById(btnId);
        var prev = b.textContent;
        b.textContent = '✅';
        b.style.background = '#22c55e';
        b.style.borderColor = '#22c55e';
        b.style.color = '#fff';
        setTimeout(function() {{
            b.textContent = prev;
            b.style.background = '';
            b.style.borderColor = '';
            b.style.color = '';
        }}, 2000);
    }});
}}
</script>
"""


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
        copy_btn = f'<button id="{btn_id}" class="copy-btn">📋</button>'
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
                status_box = f"<span class='status-pre'>{row['Status']}</span>"

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

    auto_height_script = """
<script>
function _reportH() {
    var h = document.body.scrollHeight || document.documentElement.scrollHeight;
    window.parent.postMessage({type:'streamlit:setFrameHeight', height: h + 16}, '*');
}
document.addEventListener('DOMContentLoaded', _reportH);
if (document.readyState !== 'loading') { setTimeout(_reportH, 50); }
if (window.ResizeObserver) { new ResizeObserver(_reportH).observe(document.body); }
</script>"""

    full_html = f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: sans-serif; background: transparent; padding: 4px 2px 8px 2px; }}

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
        .status-pre  {{ background: #e6f4ea; color: #1e7e34; padding: 3px 6px; border-radius: 4px; font-size: 0.85em; font-weight: 600; }}
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
    return full_html, est_height + 80
