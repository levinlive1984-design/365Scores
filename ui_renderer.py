import streamlit as st

def setup_cyber_css():
    
    
    # Toggle 標籤文字大小
    st.markdown("""
    <style>
    /* Toggle 開關旁的文字 */
    div[data-testid="stToggle"] label p {
        font-size: 0.75rem !important;  /* ← 改這裡 */
    }

    /* 緊急重置看板 按鈕文字 */
    div[data-testid="stButton"] button p {
        font-size: 0.75rem !important;  /* ← 改這裡 */
    }
    </style>
    """, unsafe_allow_html=True)    
    
    st.markdown("""
        <style>
            /* 讓主內容區淡入，避免硬閃爍 */
            [data-testid="stMainBlockContainer"] {
                animation: fadeIn 3s ease-in-out;
            }

            @keyframes fadeIn {
                from { opacity: 1; }
                to   { opacity: 1; }
            }            
            
            /* 只有在側邊欄展開時，才強制縮窄為 170px */
            [data-testid="stSidebar"][aria-expanded="true"] {
                min-width: 170px !important;
                max-width: 170px !important;
                width: 170px !important;
            }
                       
            .block-container { padding-top: 2.5rem !important;
            padding-left: 1.5rem !important; 
            padding-right: 1.5rem !important; 
            }
            [data-testid="stSidebar"] > div:first-child { padding: 1rem 0.7rem 1rem 0.7rem !important; }
            [data-testid="stSidebar"] h2 { font-size: 0.95em !important; margin-bottom: 0.3rem !important; }
            [data-testid="stSidebar"] h3 { font-size: 0.8em !important; margin-bottom: 0.2rem !important; color: #888 !important; letter-spacing: 0.05em !important; }
            [data-testid="stSidebar"] .stToggle label { font-size: 0.82em !important; }
            [data-testid="stSidebar"] .stToggle { margin-bottom: 0 !important; padding-bottom: 0 !important; }
            [data-testid="stSidebar"] .stDateInput label { font-size: 0.78em !important; margin-bottom: 0 !important; }
            [data-testid="stSidebar"] .stDateInput input { font-size: 0.82em !important; padding: 4px 8px !important; }
            [data-testid="stSidebar"] hr { margin: 0.4rem 0 !important; }
            [data-stale="true"] { opacity: 0.1 !important; transition: opacity 0.2s ease-in-out !important; }
            [data-testid="stSidebar"] .stButton > button {
                background: transparent !important; border: none !important; box-shadow: none !important;
                color: #d32f2f !important; font-weight: 900 !important; font-size: 0.8em !important;
                letter-spacing: 1px !important; display: flex !important; align-items: center !important;
                justify-content: flex-start !important; padding: 5px 0 !important; transition: all 0.2s ease !important;
            }
            [data-testid="stSidebar"] .stButton > button:hover { color: #ff0000 !important; transform: translateX(4px); }
            [data-testid="stSidebar"] .stButton > button::before {
                content: '🔴'; display: flex; align-items: center; justify-content: center;
                width: 32px; height: 32px; border: 2px solid #111; border-radius: 6px;
                background-color: #f8f9fa; margin-right: 12px; font-size: 12px;
                box-shadow: 3px 3px 0px #111; transition: all 0.1s ease;
            }
            [data-testid="stSidebar"] .stButton > button:active::before { box-shadow: 0px 0px 0px #111; transform: translate(3px, 3px); }
            tr.match-row:hover { background-color: #eef4ff !important; cursor: pointer; }
            tr.match-row:hover .match-cell { color: #1a73e8 !important; }
        </style>
    """, unsafe_allow_html=True)


def get_memo_html(league_data):
    import json

    LEAGUE_ICONS = {"NBA": "🏀", "MLB": "⚾", "NHL": "🏒", "NPB": "⚾", "KBO": "⚾", "Tennis": "🎾"}

    groups_json = []
    for league, rows in league_data.items():
        pre_rows = [r for r in rows if r.get('State') == 'pre']
        if pre_rows:
            icon = LEAGUE_ICONS.get(league, '🏟️')
            games = [f"{r.get('Date','')} {r['Time']} {r['Away']} vs {r['Home']}" for r in pre_rows]
            groups_json.append({"league": league, "icon": icon, "games": games})

    groups_data = json.dumps(groups_json, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:transparent;">
<script>
(function() {{
    var DATA = {groups_data};

    // ── 複製函式：先試 clipboard API，失敗用 textarea fallback ──
    function doCopy(text, btn) {{
        function flashOK() {{
            var prev = btn.innerHTML;
            btn.innerHTML = '✅';
            btn.style.background = '#22c55e';
            btn.style.borderColor = '#22c55e';
            btn.style.color = '#fff';
            setTimeout(function() {{
                btn.innerHTML = prev;
                btn.style.background = '';
                btn.style.borderColor = '';
                btn.style.color = '';
            }}, 2000);
        }}

        // 方法1：clipboard API
        if (navigator.clipboard && navigator.clipboard.writeText) {{
            navigator.clipboard.writeText(text).then(flashOK).catch(function() {{
                fallbackCopy(text, btn, flashOK);
            }});
        }} else {{
            fallbackCopy(text, btn, flashOK);
        }}
    }}

    // textarea execCommand fallback（在父頁面建立）
    function fallbackCopy(text, btn, cb) {{
        try {{
            var p = window.parent.document;
            var ta = p.createElement('textarea');
            ta.value = text;
            ta.style.cssText = 'position:fixed;top:-9999px;left:-9999px;opacity:0;';
            p.body.appendChild(ta);
            ta.focus();
            ta.select();
            p.execCommand('copy');
            p.body.removeChild(ta);
            if (cb) cb();
        }} catch(e) {{
            console.warn('[Memo] copy fallback failed:', e);
        }}
    }}

    function inject() {{
        try {{
            var p = window.parent.document;

            // 清除舊版元素
            ['memo-fab','memo-drawer','memo-style'].forEach(function(id) {{
                var el = p.getElementById(id);
                if (el) el.remove();
            }});

            // ── 注入 CSS ──
            var s = p.createElement('style');
            s.id = 'memo-style';
            s.textContent = `
                #memo-fab {{
                    position:fixed; top:75px; right:18px; z-index:99999;
                    width:44px; height:44px; border-radius:10px;
                    background:#fff; border:2px solid #222; box-shadow:3px 3px 0px #111;
                    cursor:pointer; font-size:20px; display:flex;
                    align-items:center; justify-content:center;
                    transition:all 0.15s ease; padding:0; line-height:1; font-family:sans-serif;
                }}
                #memo-fab:hover {{ background:#f0f4ff; transform:translate(-1px,-1px); box-shadow:4px 4px 0px #111; }}
                #memo-drawer {{
                    position:fixed; top:0; right:0; width:360px; height:100vh;
                    background:#fff; border-left:2px solid #222;
                    box-shadow:-6px 0 24px rgba(0,0,0,0.13);
                    z-index:99998; transform:translateX(100%);
                    transition:transform 0.32s cubic-bezier(0.4,0,0.2,1);
                    display:flex; flex-direction:column; overflow:hidden; font-family:sans-serif;
                }}
                #memo-drawer.open {{ transform:translateX(0); }}
                .memo-header {{
                    display:flex; align-items:center; justify-content:space-between;
                    padding:14px 16px; border-bottom:2px solid #222;
                    font-weight:900; font-size:1.0em; background:#f8f9fa; flex-shrink:0;
                }}
                .memo-close {{
                    width:32px; height:32px; border:2px solid #222; border-radius:6px;
                    background:#fff; cursor:pointer; font-size:15px; display:flex;
                    align-items:center; justify-content:center;
                    box-shadow:2px 2px 0px #111; font-weight:900; padding:0;
                    transition:all 0.1s ease;
                }}
                .memo-close:active {{ box-shadow:0 0 0; transform:translate(2px,2px); }}
                .memo-body {{
                    flex:1; overflow-y:auto; padding:50px 12px 12px 12px;
                    background:#fafafa; box-sizing:border-box;
                }}
                .memo-empty {{ color:#aaa; text-align:center; padding:48px 0; font-size:0.95em; }}
                .memo-group {{
                    margin-bottom:12px; border:2px solid #222; border-radius:8px;
                    overflow:hidden; background:#fff; box-shadow:2px 2px 0px rgba(0,0,0,0.06);
                }}
                .memo-group-header {{
                    display:flex; align-items:center; justify-content:space-between;
                    background:#f0f0f0; padding:8px 10px 8px 12px;
                    font-weight:800; font-size:0.9em; border-bottom:1px solid #ddd;
                    gap:8px;
                }}
                .memo-group-title {{ flex:1; }}
                .memo-row {{
                    display:flex; align-items:center; padding:8px 10px 8px 12px;
                    border-bottom:1px solid #eee; gap:8px; box-sizing:border-box;
                }}
                .memo-row:last-child {{ border-bottom:none; }}
                .memo-match {{
                    flex:1; color:#333; font-size:0.86em; line-height:1.5;
                    font-family:'SF Mono','Fira Code',monospace; word-break:break-all;
                }}
                .memo-copy-btn {{
                    flex-shrink:0; width:30px; height:30px;
                    border:2px solid #222; border-radius:5px;
                    background:#f8f9fa; cursor:pointer; font-size:13px;
                    display:inline-flex; align-items:center; justify-content:center;
                    padding:0; box-shadow:2px 2px 0px #111;
                    transition:all 0.1s ease;
                }}
                .memo-copy-btn:hover {{ background:#e8f0fe; border-color:#4a90d9; }}
                .memo-copy-btn:active {{ box-shadow:0 0 0; transform:translate(2px,2px); }}
            `;
            p.head.appendChild(s);

            // ── 建立抽屜 ──
            var drawer = p.createElement('div');
            drawer.id = 'memo-drawer';

            // 標頭
            var header = p.createElement('div');
            header.className = 'memo-header';
            var headerTitle = p.createElement('span');
            headerTitle.textContent = '📋 即將開始備忘錄';
            var closeBtn = p.createElement('button');
            closeBtn.className = 'memo-close';
            closeBtn.innerHTML = '✕';
            closeBtn.addEventListener('click', function() {{
                p.getElementById('memo-drawer').classList.remove('open');
            }});
            header.appendChild(headerTitle);
            header.appendChild(closeBtn);
            drawer.appendChild(header);

            // 內容區
            var body = p.createElement('div');
            body.className = 'memo-body';

            if (!DATA || DATA.length === 0) {{
                var empty = p.createElement('div');
                empty.className = 'memo-empty';
                empty.textContent = '📭 目前無即將開始的比賽';
                body.appendChild(empty);
            }} else {{
                DATA.forEach(function(g, gi) {{
                    var allText = g.games.join('\\n');

                    // 群組容器
                    var group = p.createElement('div');
                    group.className = 'memo-group';

                    // 群組標頭
                    var gHeader = p.createElement('div');
                    gHeader.className = 'memo-group-header';

                    var gTitle = p.createElement('span');
                    gTitle.className = 'memo-group-title';
                    gTitle.textContent = g.icon + ' ' + g.league;

                    var gBtn = p.createElement('button');
                    gBtn.className = 'memo-copy-btn';
                    gBtn.innerHTML = '📋';
                    gBtn.title = '複製整組';
                    (function(txt, btn) {{
                        btn.addEventListener('click', function() {{ doCopy(txt, btn); }});
                    }})(allText, gBtn);

                    gHeader.appendChild(gTitle);
                    gHeader.appendChild(gBtn);
                    group.appendChild(gHeader);

                    // 每場比賽列
                    g.games.forEach(function(line, ri) {{
                        var row = p.createElement('div');
                        row.className = 'memo-row';

                        var matchSpan = p.createElement('span');
                        matchSpan.className = 'memo-match';
                        matchSpan.textContent = line;

                        var rBtn = p.createElement('button');
                        rBtn.className = 'memo-copy-btn';
                        rBtn.innerHTML = '📋';
                        rBtn.title = '複製此場';
                        (function(txt, btn) {{
                            btn.addEventListener('click', function() {{ doCopy(txt, btn); }});
                        }})(line, rBtn);

                        row.appendChild(matchSpan);
                        row.appendChild(rBtn);
                        group.appendChild(row);
                    }});

                    body.appendChild(group);
                }});
            }}

            drawer.appendChild(body);
            p.body.appendChild(drawer);

            // ── 注入浮動按鈕 ──
            var fab = p.createElement('button');
            fab.id = 'memo-fab';
            fab.innerHTML = '📝';
            fab.title = '即將開始備忘錄';
            fab.addEventListener('click', function() {{
                p.getElementById('memo-drawer').classList.toggle('open');
            }});
            p.body.appendChild(fab);

        }} catch(e) {{
            console.error('[Memo] inject failed:', e);
        }}
    }}

    if (window.parent.document.body) {{
        inject();
    }} else {{
        window.parent.addEventListener('load', inject);
    }}
    setTimeout(inject, 300);
}})();
</script>
</body></html>"""


def get_table_html(title, data_list):
    import json, re as _re

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
            function flashOK(b) {{
                b.textContent = '✅'; b.style.background = '#22c55e'; b.style.color = '#fff';
                setTimeout(function() {{
                    b.textContent = '📋'; b.style.background = '#f8f9fa'; b.style.color = '#333';
                }}, 2000);
            }}
            var b = document.getElementById('{btn_id}');
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{ flashOK(b); }});
            }} else {{
                var ta = document.createElement('textarea');
                ta.value = text;
                ta.style.cssText = 'position:fixed;top:-9999px;opacity:0;';
                document.body.appendChild(ta);
                ta.select(); document.execCommand('copy');
                document.body.removeChild(ta);
                flashOK(b);
            }}
        }};
        </script>"""
    else:
        copy_btn = ''
        copy_script = ''

    if data_list is None:
        body = f'<div class="tab-label">{title}</div><div class="card-empty">⏳ 數據鏈路異常，等待重新連線...</div>'
        est_height = 120
    elif not data_list:
        body = f'<div class="tab-label">{title}</div><div class="card-empty">📡 該日期暫無賽事數據，鏈路待命。</div>'
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
            away_name = f"<span class='serving-highlight'>{row['Away']}</span>" if serving == 'away' else row['Away']
            home_name = f"<span class='serving-highlight'>{row['Home']}</span>" if serving == 'home' else row['Home']
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
        <div class="tab-row"><div class="tab-label">{title}{copy_btn}</div></div>
        <div class="card">
            <table>
                <thead><tr>
                    <th class='col-time'>時間</th><th class='col-status'>狀態</th>
                    <th class='col-match'>對戰組合</th><th class='col-score'>比分</th>
                </tr></thead>
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
            display: inline-flex; align-items: center; position: relative; top: 2px; z-index: 2;
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
        .col-time {{ width: 14%; white-space: nowrap; font-size: 0.8em;}}
        .col-status {{ width: 20%; }}
        .col-match {{ width: 46%; font-size: 0.8em;}}
        .col-score {{ width: 20%; font-weight: 700; font-size: 0.9em; white-space: nowrap; }}
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
        .serving-highlight {{
            background: #fff7ed; border-radius: 3px; padding: 1px 5px;
            color: #9a3412; font-weight: 600;
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
    {body}{copy_script}{auto_height_script}"""
    return full_html, est_height + 80
