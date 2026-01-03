import os
import glob
import re
import feedparser
from datetime import datetime

# --- 1. CONFIGURATION ---
RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://rsshub.app/theverge/index",
    "https://rsshub.app/hackernews",
    "https://rsshub.app/bbc/world",
    "https://rsshub.app/reuters/world"
]

TECH_KEYWORDS = ["AI", "Nvidia", "Apple", "GPT", "OpenAI", "Microsoft", "LLM", "Silicon", "Tesla", "Fintech"]

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
    print("📡 Syncing Pro Intelligence...")
    all_entries = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except: pass
    all_entries.sort(key=lambda x: x.get('published_parsed') or x.get('updated_parsed'), reverse=True)
    
    cards_html = ""
    for i, entry in enumerate(all_entries[:12]):
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        cards_html += f"""
        <article class="news-item">
            <div class="content">
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
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 60px; --font-main: 'Inter', sans-serif;
            --ft-title: clamp(1rem, 1.2vw + 0.5rem, 1.25rem);
            --ft-details: clamp(0.8rem, 0.7vw + 0.4rem, 0.9rem);
            --menu-bg: #ffffff;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626;
            --menu-bg: #111111;
        }}
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; transition: background 0.3s; overflow-x: hidden; }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; backdrop-filter: blur(15px); }}
        .logo {{ font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; text-decoration: none; color: inherit; z-index: 2100; }}
        .pulse {{ width: 6px; height: 6px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 700; font-size: 9px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.1em; white-space: nowrap; }}
        
        /* --- UNIFIED SANDWICH MENU --- */
        #menu-toggle {{ display: none; }}
        .sandwich {{ cursor: pointer; z-index: 2100; display: flex; flex-direction: column; gap: 4px; padding: 10px; }}
        .sandwich span {{ width: 20px; height: 2px; background: var(--text); transition: 0.3s; }}
        
        .nav-actions {{ 
            position: fixed; top: 0; right: -100%; width: 240px; height: 100vh;
            background: var(--menu-bg); border-left: 1px solid var(--border);
            display: flex; flex-direction: column; padding: 100px 25px; gap: 15px;
            transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 2050;
            box-shadow: -10px 0 30px rgba(0,0,0,0.1);
        }}
        #menu-toggle:checked ~ .nav-actions {{ right: 0; }}
        #menu-toggle:checked ~ .sandwich span:nth-child(1) {{ transform: translateY(6px) rotate(45deg); }}
        #menu-toggle:checked ~ .sandwich span:nth-child(2) {{ opacity: 0; }}
        #menu-toggle:checked ~ .sandwich span:nth-child(3) {{ transform: translateY(-6px) rotate(-45deg); }}

        .menu-item {{ 
            padding: 12px 15px; border-radius: 8px; font-size: 11px; font-weight: 800;
            color: var(--text); text-decoration: none; background: var(--border);
            text-transform: uppercase; text-align: left; border: none; cursor: pointer;
        }}
        .theme-toggle-btn {{ background: none; color: var(--accent); margin-bottom: 10px; }}

        /* --- CONTENT --- */
        .container {{ width: 100%; max-width: 1000px; margin: 80px auto 40px; padding: 0 15px; }}
        .items {{ display: grid; gap: 20px; }}

        [data-ui="columnist"] .items {{ grid-template-columns: 1fr 1fr; gap: 30px; }}
        [data-ui="columnist"] .news-item {{ border-left: 2px solid var(--border); padding-left: 15px; }}
        [data-ui="feed"] .container {{ max-width: 600px; }}
        [data-ui="terminal"] body {{ background: #000; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="newspaper"] .items {{ column-count: 3; column-gap: 30px; display: block; }}
        [data-ui="newspaper"] .news-item {{ break-inside: avoid; border-bottom: 0.5px solid #444; padding-bottom: 12px; margin-bottom: 12px; }}

        .title {{ line-height: 1.2; font-weight: 800; margin: 0 0 6px; font-size: var(--ft-title); }}
        .title a {{ text-decoration: none; color: inherit; }}
        .details {{ font-size: var(--ft-details); line-height: 1.45; color: var(--sub); }}
        b {{ color: var(--text); font-weight: 700; }}

        @media (max-width: 768px) {{
            [data-ui="columnist"] .items, [data-ui="newspaper"] .items {{ grid-template-columns: 1fr; column-count: 1; }}
            .container {{ margin-top: 75px; }}
            .date-center {{ font-size: 8px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="logo"><div class="pulse"></div> N.I.U.S.</div>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        
        <div class="menu-wrap">
            <input type="checkbox" id="menu-toggle">
            <label for="menu-toggle" class="sandwich">
                <span></span><span></span><span></span>
            </label>
            
            <div class="nav-actions">
                <button class="menu-item theme-toggle-btn" onclick="toggleTheme()">🌓 Change Theme</button>
                <div style="font-size: 9px; font-weight: 800; color: var(--sub); margin-top: 10px;">SELECT MODEL</div>
                <button class="menu-item" onclick="setUI('columnist')">Columnist</button>
                <button class="menu-item" onclick="setUI('feed')">Intel Feed</button>
                <button class="menu-item" onclick="setUI('terminal')">Terminal</button>
                <button class="menu-item" onclick="setUI('newspaper')">Newspaper</button>
                <button class="menu-item" onclick="setUI('magazine')">Magazine</button>
                <button class="menu-item" onclick="setUI('cards')">Cards</button>
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

        function toggleTheme() {{
            const target = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('nius-v14-theme', target);
        }}

        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-v14-ui', mode);
            document.getElementById('menu-toggle').checked = false;
        }}

        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-v14-ui') || 'columnist');
            const theme = localStorage.getItem('nius-v14-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
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
