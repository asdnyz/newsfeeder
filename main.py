import os
import re
import feedparser
from datetime import datetime

# --- 1. CONFIGURATION ---
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://rsshub.app/theverge/index",
    "HackerNews": "https://rsshub.app/hackernews",
    "BBC World": "https://rsshub.app/bbc/world",
    "Reuters": "https://rsshub.app/reuters/world"
}

TECH_KEYWORDS = ["Fintech"]

# --- 2. LOGIC ---
def clean_and_summarize(raw_html, limit=180):
    text = re.sub(r'<[^>]+>', '', raw_html)
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0] + "..."
    for word in TECH_KEYWORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f"<b>{word}</b>", text)
    return text

def fetch_news():
    all_entries = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                entry['source_label'] = source
                all_entries.append(entry)
        except: pass
    all_entries.sort(key=lambda x: x.get('published_parsed') or x.get('updated_parsed'), reverse=True)
    
    cards_html = ""
    for entry in all_entries[:15]:
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        cards_html += f"""
        <article class="news-item" data-source="{entry['source_label']}">
            <div class="content">
                <span class="chip">{entry['source_label']}</span>
                <h2 class="title"><a href="{entry.link}" target="_blank">{entry.title}</a></h2>
                <p class="details">{summary}</p>
            </div>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    full_date = datetime.now().strftime("%B %d, %Y").lower()
    short_date = datetime.now().strftime("%d-%b-%y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="columnist" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>N.I.U.S. PRO</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 60px; --ticker-h: 30px; --font-main: 'Inter', sans-serif;
            --menu-bg: #ffffff;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626; --menu-bg: #111111;
        }}
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; transition: background 0.3s; overflow-x: hidden; }}

        /* --- TICKER --- */
        .ticker-wrap {{ position: fixed; top: 0; width: 100%; height: var(--ticker-h); background: var(--text); color: var(--bg); z-index: 2200; overflow: hidden; display: flex; align-items: center; font-family: 'JetBrains Mono'; font-size: 10px; font-weight: 800; }}
        .ticker-move {{ display: flex; white-space: nowrap; animation: ticker 30s linear infinite; }}
        .ticker-item {{ padding: 0 30px; }}
        @keyframes ticker {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: var(--ticker-h); left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; backdrop-filter: blur(15px); }}
        .logo {{ font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; text-decoration: none; color: inherit; }}
        .pulse {{ width: 6px; height: 6px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 700; font-size: 9px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.1em; white-space: nowrap; }}
        
        /* --- MENU --- */
        #menu-toggle {{ display: none; }}
        .sandwich {{ cursor: pointer; display: flex; flex-direction: column; gap: 4px; padding: 10px; }}
        .sandwich span {{ width: 20px; height: 2px; background: var(--text); transition: 0.3s; }}
        .nav-actions {{ position: fixed; top: 0; right: -100%; width: 260px; height: 100vh; background: var(--menu-bg); border-left: 1px solid var(--border); display: flex; flex-direction: column; padding: 80px 25px 40px; gap: 12px; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 2050; box-shadow: -10px 0 30px rgba(0,0,0,0.1); }}
        #menu-toggle:checked ~ .nav-actions {{ right: 0; }}
        .menu-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.2); z-index: 2040; display: none; }}
        #menu-toggle:checked ~ .menu-overlay {{ display: block; }}

        .menu-item {{ padding: 10px 15px; border-radius: 8px; font-size: 10px; font-weight: 800; color: var(--text); background: var(--border); border: none; cursor: pointer; text-align: left; text-transform: uppercase; }}
        .filter-btn.active {{ background: var(--accent); color: white; }}
        .close-btn {{ margin-top: auto; background: var(--text); color: var(--bg); text-align: center; }}

        /* --- CONTENT --- */
        .container {{ width: 100%; max-width: 1000px; margin: 120px auto 40px; padding: 0 15px; }}
        .items {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
        .news-item {{ border-left: 2px solid var(--border); padding-left: 15px; transition: 0.3s; }}
        .chip {{ font-size: 8px; font-weight: 800; background: var(--border); padding: 2px 6px; border-radius: 4px; text-transform: uppercase; color: var(--sub); }}
        .title {{ font-size: 1.1rem; line-height: 1.3; font-weight: 800; margin: 8px 0; }}
        .title a {{ text-decoration: none; color: inherit; }}
        .details {{ font-size: 0.9rem; line-height: 1.5; color: var(--sub); }}

        @media (max-width: 768px) {{
            .items {{ grid-template-columns: 1fr; }}
            .container {{ margin-top: 110px; }}
            .date-center {{ font-size: 8px; }}
        }}
    </style>
</head>
<body>
    <div class="ticker-wrap">
        <div class="ticker-move">
            <span class="ticker-item">NVDA: $495.22 (+2.4%)</span>
            <span class="ticker-item">AAPL: $192.53 (-0.4%)</span>
            <span class="ticker-item">MSFT: $375.01 (+1.1%)</span>
            <span class="ticker-item">TSLA: $248.48 (+0.8%)</span>
            <span class="ticker-item">NVDA: $495.22 (+2.4%)</span>
            <span class="ticker-item">AAPL: $192.53 (-0.4%)</span>
            <span class="ticker-item">MSFT: $375.01 (+1.1%)</span>
            <span class="ticker-item">TSLA: $248.48 (+0.8%)</span>
        </div>
    </div>

    <nav class="nav">
        <div class="logo"><div class="pulse"></div> N.I.U.S.</div>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        
        <div class="menu-wrap">
            <input type="checkbox" id="menu-toggle">
            <div class="menu-overlay" onclick="toggleMenu(false)"></div>
            <label for="menu-toggle" class="sandwich"><span></span><span></span><span></span></label>
            
            <div class="nav-actions">
                <button class="menu-item" style="color:var(--accent)" onclick="toggleTheme()">🌓 TOGGLE THEME</button>
                <div style="font-size: 9px; font-weight: 800; color: var(--sub); margin-top: 10px;">FILTER BY SOURCE</div>
                <button class="menu-item filter-btn active" onclick="filterSource('all', this)">All Sources</button>
                <button class="menu-item filter-btn" onclick="filterSource('TechCrunch', this)">TechCrunch</button>
                <button class="menu-item filter-btn" onclick="filterSource('The Verge', this)">The Verge</button>
                <button class="menu-item filter-btn" onclick="filterSource('HackerNews', this)">Hacker News</button>
                
                <div style="font-size: 9px; font-weight: 800; color: var(--sub); margin-top: 10px;">LAYOUT</div>
                <button class="menu-item" onclick="setUI('columnist')">Columnist</button>
                <button class="menu-item" onclick="setUI('terminal')">Terminal</button>
                <button class="menu-item close-btn" onclick="toggleMenu(false)">✕ CLOSE MENU</button>
            </div>
        </div>
    </nav>

    <main class="container"><div class="items" id="news-grid">{cards_html}</div></main>

    <script>
        function updateDate() {{
            const el = document.getElementById('live-date');
            el.innerText = window.innerWidth < 768 ? el.getAttribute('data-short') : el.getAttribute('data-full');
        }}
        window.addEventListener('resize', updateDate);

        function toggleMenu(s) {{ document.getElementById('menu-toggle').checked = s; }}
        
        function filterSource(source, btn) {{
            const items = document.querySelectorAll('.news-item');
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            items.forEach(item => {{
                item.style.display = (source === 'all' || item.getAttribute('data-source') === source) ? 'block' : 'none';
            }});
            toggleMenu(false);
        }}

        function toggleTheme() {{
            const t = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', t);
            localStorage.setItem('nius-v-theme', t);
        }}

        function setUI(m) {{
            document.documentElement.setAttribute('data-ui', m);
            toggleMenu(false);
        }}

        window.onload = () => {{
            updateDate();
            const theme = localStorage.getItem('nius-v-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            document.documentElement.setAttribute('data-theme', theme);
        }};
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    cards = fetch_news()
    generate_index_html(cards)
