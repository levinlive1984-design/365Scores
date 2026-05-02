import streamlit as st

def setup_cyber_css():
    """賽博龐克 CSS 與優化版的過渡動畫"""
    st.markdown("""
        <style>
            .block-container { padding-top: 4rem !important; }

            [data-testid="stSidebar"] > div:first-child {
                padding: 1rem 0.7rem 1rem 0.7rem !important;
            }
            [data-testid="stSidebar"] h2 { font-size: 0.95em !important; margin-bottom: 0.3rem !important; }
            [data-testid="stSidebar"] h3 {
                font-size: 0.8em !important; margin-bottom: 0.2rem !important;
                color: #888 !important; letter-spacing: 0.05em !important;
            }
            [data-testid="stSidebar"] .stToggle label { font-size: 0.82em !important; }
            [data-testid="stSidebar"] .stToggle { margin-bottom: 0 !important; padding-bottom: 0 !important; }
            [data-testid="stSidebar"] .stDateInput label { font-size: 0.78em !important; margin-bottom: 0 !important; }
            [data-testid="stSidebar"] .stDateInput input { font-size: 0.82em !important; padding: 4px 8px !important; }
            [data-testid="stSidebar"] hr { margin: 0.4rem 0 !important; }

            .update-timestamp {
                font-family: 'Courier New', monospace; color: #00FF00;
                background: #111; padding: 3px 10px; border-radius: 4px;
                border: 1px solid #00FF00; box-shadow: 0 0 5px rgba(0,255,0,0.3);
            }
            [data-stale="true"] { opacity: 0.1 !important; transition: opacity 0.2s ease-in-out !important; }

            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important; border: none !important;
                box-shadow: none !important; color: #d32f2f !important;
                font-weight: 900 !important; font-size: 0.8em !important;
                letter-spacing: 1px !important; display: flex !important;
                align-items: center !important; justify-content: flex-start !important;
                padding: 5px 0 !important; transition: all 0.2s ease !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover {
                color: #ff0000 !important; transform: translateX(4px);
            }
            [data-testid="stSidebar"] .stButton > button::before {
                content: '🔴'; display: flex; align-items: center; justify-content: center;
                width: 32px; height: 32px; border: 2px solid #111; border-radius: 6px;
                background-color: #f8f9fa; margin-right: 12px; font-size: 12px;
                box-shadow: 3px 3px 0px #111; transition: all 0.1s ease;
            }
            [data-testid="stSidebar"] .stButton > button:active::before {
                box-shadow: 0px 0px 0px #111; transform: translate(3px, 3px);
            }
            tr.match-row:hover { background-color: #eef4ff !important; cursor: pointer; }
            tr.match-row:hover .match-cell { color: #1a73e8 !important; }
        </style>
    """, unsafe_allow_html=True)


# ── 共用複製 JS（在 components.html iframe 內執行，execCommand 不需要剪貼簿權限）──
_COPY_JS = """
<script>
function _execCopy(text, cb) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none;';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try { document.execCommand('copy'); if (cb) cb(); } catch(e) { console.warn('copy failed', e); }
    document.body.removeChild(ta);
}
function doCopy(text, btnId) {
    var b = document.getElementById(btnId);
    if (!b) return;
    var prev = b.textContent;
    function onSuccess() {
        b.textContent = '✅';
        b.style.background = '#22c55e';
        b.style.borderColor = '#22c55e';
        b.style.color = '#fff';
        setTimeout(function() {
            b.textContent = prev;
            b.style.background = '';
            b.style.borderColor = '';
            b.style.color = '';
        }, 2000);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(onSuccess).catch(function() {
            _execCopy(text, onSuccess);
        });
    } else {
        _execCopy(text, onSuccess);
    }
}
</script>
"""


def get_memo_html(league_data):
    """
    生成備忘錄 HTML，以 JS inject 方式寫入主頁面 document.body。
    透過 st.markdown(..., unsafe_allow_html=True) 注入。
    Streamlit 雖然過濾 <script>，但 <img onerror> trick 可執行 JS，
    最可靠的做法是用一個隱藏的 components.html iframe 傳訊息給自己。
    ─── 實際做法：直接把所有 DOM 和 CSS 用 JS 字串動態建立並 inject 到 parent ───
    回傳純 HTML 字串（給 st.markdown 用）。
    """
    import json, re as _re

    LEAGUE_ICONS = {
        "NBA": "🏀", "MLB": "⚾", "NHL": "🏒",
        "NPB": "⚾", "KBO": "⚾", "Tennis": "🎾"
    }

    groups = []
    for league, rows in league_data.items():
        pre_rows = [r for r in rows if r.get('State') == 'pre']
        if pre_rows:
            groups.append((league, LEAGUE_ICONS.get(league, '🏟️'), pre_rows))

    # ── 把備忘錄內容序列化成 JSON 傳給 JS ──
    memo_groups = []
    for league, icon, pre_rows in groups:
        group_lines = "\n".join(
            f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}"
            for r in pre_rows
        )
        matches = [
            {"text": f"{r.get('Date','')} {r['Time']}  {r['Away']} vs {r['Home']}",
             "copy": f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}"}
            for r in pre_rows
        ]
        memo_groups.append({
            "league": league,
            "icon": icon,
            "groupCopy": group_lines,
            "matches": matches
        })

    memo_data_json = json.dumps(memo_groups, ensure_ascii=False)

    # ── 整段邏輯放在 components.html iframe 裡，用 postMessage 通知父頁面 ──
    # 但最簡單可靠的是：直接在 iframe 裡操控 window.parent.document
    # Streamlit Cloud 同源，所以可以存取 parent DOM。
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8">
<style>
html, body {{ margin:0; padding:0; overflow:hidden; background:transparent; }}
</style>
</head>
<body>
<script>
(function() {{
    var p = window.parent.document;

    // 避免重複注入
    if (p.getElementById('_memo_style')) {{
        // 已存在：只更新內容
        var bodyEl = p.getElementById('memo-body-inner');
        if (bodyEl) bodyEl.innerHTML = buildInner();
        return;
    }}

    // ── 注入 CSS ──
    var style = p.createElement('style');
    style.id = '_memo_style';
    style.textContent = `
        #memo-fab {{
            position: fixed !important; bottom: 24px !important; right: 24px !important;
            z-index: 99999 !important; width: 52px; height: 52px; border-radius: 12px;
            background: #fff; border: 2px solid #222; box-shadow: 3px 3px 0px #111;
            cursor: pointer; font-size: 22px; display: flex !important;
            align-items: center; justify-content: center;
            transition: all 0.15s ease;
        }}
        #memo-fab:hover {{ background: #f0f4ff; transform: translate(-1px,-1px); }}
        #memo-drawer {{
            position: fixed !important; top: 0 !important; right: 0 !important;
            width: 360px; height: 100vh; background: #fff;
            border-left: 2px solid #222; box-shadow: -6px 0 24px rgba(0,0,0,0.18);
            z-index: 99998 !important; transform: translateX(100%);
            transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
            display: flex; flex-direction: column; overflow: hidden;
            font-family: sans-serif;
        }}
        #memo-drawer.memo-open {{ transform: translateX(0) !important; }}
        .memo-header {{
            display: flex; align-items: center; justify-content: space-between;
            padding: 14px 16px; border-bottom: 2px solid #222;
            font-weight: 900; font-size: 1em; background: #f8f9fa; flex-shrink: 0;
        }}
        .memo-close {{
            width: 32px; height: 32px; border: 2px solid #222; border-radius: 6px;
            background: #fff; cursor: pointer; font-size: 15px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 2px 2px 0 #111; font-weight: 900; padding: 0;
        }}
        #memo-body-inner {{ flex:1; overflow-y:auto; padding:12px 14px; background:#fafafa; }}
        .memo-empty {{ color:#aaa; text-align:center; padding:48px 0; font-size:0.95em; }}
        .memo-group {{ margin-bottom:12px; border:2px solid #222; border-radius:8px; overflow:hidden; background:#fff; }}
        .memo-group-header {{
            display:flex; align-items:center; justify-content:space-between;
            background:#f0f0f0; padding:8px 12px; font-weight:800; font-size:0.9em;
            border-bottom:1px solid #ddd;
        }}
        .memo-row {{
            display:flex; align-items:center; justify-content:space-between;
            padding:8px 12px; border-bottom:1px solid #eee; gap:8px;
        }}
        .memo-row:last-child {{ border-bottom:none; }}
        .memo-match {{ flex:1; color:#333; font-size:0.85em; line-height:1.5; font-family:"SF Mono","Fira Code",monospace; }}
        .memo-copy-btn {{
            flex-shrink:0; width:28px; height:28px; border:1.5px solid #bbb;
            border-radius:5px; background:#f8f9fa; cursor:pointer; font-size:13px;
            display:inline-flex; align-items:center; justify-content:center; padding:0;
            box-shadow:1px 1px 0 #ccc; transition:all 0.1s;
        }}
        .memo-copy-btn:hover {{ background:#e8f0fe; border-color:#4a90d9; }}
    `;
    p.head.appendChild(style);

    // ── 複製函數（注入到 parent window）──
    if (!window.parent._memoCopy) {{
        window.parent._execCopy = function(text, cb) {{
            var ta = p.createElement('textarea');
            ta.value = text;
            ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0;pointer-events:none;';
            p.body.appendChild(ta);
            ta.focus(); ta.select();
            try {{ p.execCommand('copy'); if(cb) cb(); }} catch(e) {{}}
            p.body.removeChild(ta);
        }};
        window.parent._memoCopy = function(text, btnEl) {{
            var prev = btnEl.textContent;
            function ok() {{
                btnEl.textContent = '✅';
                btnEl.style.background = '#22c55e';
                btnEl.style.borderColor = '#22c55e';
                btnEl.style.color = '#fff';
                setTimeout(function() {{
                    btnEl.textContent = prev;
                    btnEl.style.cssText = '';
                }}, 2000);
            }}
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(ok).catch(function(){{ window.parent._execCopy(text, ok); }});
            }} else {{
                window.parent._execCopy(text, ok);
            }}
        }};
    }}

    function buildInner() {{
        var groups = {memo_data_json};
        if (!groups || groups.length === 0) {{
            return "<div class='memo-empty'>📭 目前無即將開始的比賽</div>";
        }}
        var html = '';
        groups.forEach(function(g) {{
            var groupCopy = g.groupCopy;
            var rowsHtml = g.matches.map(function(m) {{
                return "<div class='memo-row'>" +
                    "<span class='memo-match'>" + m.text + "</span>" +
                    "<button class='memo-copy-btn' onclick=\"window.parent._memoCopy(" + JSON.stringify(m.copy) + ", this)\">📋</button>" +
                    "</div>";
            }}).join('');
            html += "<div class='memo-group'>" +
                "<div class='memo-group-header'>" +
                    "<span>" + g.icon + " " + g.league + "</span>" +
                    "<button class='memo-copy-btn' onclick=\"window.parent._memoCopy(" + JSON.stringify(groupCopy) + ", this)\">📋</button>" +
                "</div>" +
                "<div>" + rowsHtml + "</div>" +
                "</div>";
        }});
        return html;
    }}

    // ── 建立 FAB 按鈕 ──
    var fab = p.createElement('button');
    fab.id = 'memo-fab';
    fab.title = '即將開始備忘錄';
    fab.textContent = '📝';
    fab.onclick = function() {{
        p.getElementById('memo-drawer').classList.toggle('memo-open');
    }};
    p.body.appendChild(fab);

    // ── 建立抽屜 ──
    var drawer = p.createElement('div');
    drawer.id = 'memo-drawer';
    drawer.innerHTML =
        "<div class='memo-header'>" +
            "<span>📋 即將開始備忘錄</span>" +
            "<button class='memo-close' id='memo-close-btn'>✕</button>" +
        "</div>" +
        "<div id='memo-body-inner'></div>";
    p.body.appendChild(drawer);

    p.getElementById('memo-close-btn').onclick = function() {{
        p.getElementById('memo-drawer').classList.remove('memo-open');
    }};

    p.getElementById('memo-body-inner').innerHTML = buildInner();
}})();
</script>
</body>
</html>"""


def get_table_html(title, data_list):
    """生成完整獨立 HTML（含 <style>），供 components.html() 使用。
    回傳 (html_str, estimated_height)"""
    import json, re as _re

    pre_rows = [r for r in data_list if r.get('State') == 'pre']
    copy_lines = [f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}" for r in pre_rows]
    copy_text_json = json.dumps("\n".join(copy_lines))
    btn_id = "cpbtn_" + _re.sub(r'[^a-zA-Z0-9]', '_', title)

    if pre_rows:
        copy_btn = f'<button id="{btn_id}" class="copy-btn" onclick="_cp(this,{copy_text_json})">&#128203;</button>'
        copy_script = f"""<script>
function _cp(btn, text) {{
    var prev = btn.innerHTML;
    function ok() {{
        btn.innerHTML = '&#9989;';
        btn.style.background = '#22c55e';
        btn.style.color = '#fff';
        setTimeout(function() {{
            btn.innerHTML = prev;
            btn.style.background = '';
            btn.style.color = '';
        }}, 2000);
    }}
    if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(ok).catch(function() {{ _ec(text, ok); }});
    }} else {{ _ec(text, ok); }}
}}
function _ec(text, cb) {{
    var ta = document.createElement('textarea');
    ta.value = text; ta.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
    document.body.appendChild(ta); ta.focus(); ta.select();
    try {{ document.execCommand('copy'); if(cb) cb(); }} catch(e) {{}}
    document.body.removeChild(ta);
}}
</script>"""
    else:
        copy_btn = ''
        copy_script = ''

    if not data_list:
        body = f"""
        <div class="tab-label">{title}</div>
        <div class="card-empty">📡 該日期暫無賽事數據，鏈路待命。</div>
        """
        est_height = 120
    else:
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
            background: #fff; border: 2px solid #222; border-bottom: none;
            border-radius: 8px 16px 0 0; padding: 6px 16px 6px 20px;
            font-size: 1.05em; font-weight: 900; color: #111; letter-spacing: 1px;
            box-shadow: 2px -2px 0px rgba(0,0,0,0.05); min-width: 120px;
        }}
        .card {{
            position: relative; z-index: 1; border: 2px solid #222;
            border-radius: 0 8px 8px 8px; background: #fff;
            box-shadow: 4px 4px 0px rgba(0,0,0,0.07); overflow: hidden;
        }}
        .card-empty {{ border: 2px solid #555; border-radius: 0 8px 8px 8px; padding: 20px; color: #888; }}
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
            border-right: 8px solid #22c55e; margin: 0 4px; vertical-align: middle;
        }}
        .match-link {{ color: inherit; text-decoration: none; }}
        .match-link:hover {{ color: #1a73e8; }}
        .copy-btn {{
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; border: 2px solid #222; border-radius: 5px;
            background: #f8f9fa; color: #333; font-size: 13px; cursor: pointer;
            box-shadow: 2px 2px 0px #111; margin-left: 8px; padding: 0; flex-shrink: 0;
            transition: all 0.1s ease;
        }}
        .copy-btn:active {{ box-shadow: 0 0 0 #111; transform: translate(2px,2px); }}
    </style>
    {body}
    {copy_script}
    {auto_height_script}
    """
    return full_html, est_height + 80
