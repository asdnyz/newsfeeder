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
    print("📡 Syncing NIUS Multiverse...")
    all_entries = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except: pass

    all_entries.sort(key=lambda x: x.get('published_parsed') or x.get('updated_parsed'), reverse=True)
    
    cards_html = ""
    for i, entry in enumerate(all_entries[:10]):
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        # Assign 'wide' class to every 4th item for Bento look
        size_class = "wide" if i % 4 == 0 else "regular"
        cards_html += f"""
        <article class="news-item {size_class}">
            <div class="content">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <a href="{entry.link}" target="_blank" class="source-link">View Source</a>
            </div>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    current_date = datetime.now().strftime("%B %d, %Y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N.I.U.S. | Multiverse</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        :root {{
            --bg: #f5f5f7; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: rgba(0,0,0,0.08);
            --nav-h: 64px; --font-main: 'Inter', sans-serif;
        }}
        [data-theme="dark"] {{
            --bg: #111111; --text: #ffffff; --sub: #a1a1a6; --border: rgba(255,255,255,0.1);
        }}
        
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; overflow-x: hidden; }}

        /* --- STICKY NAV --- */
        .nav {{ 
            position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); 
            background: var(--bg); border-bottom: 1px solid var(--border); 
            z-index: 2000; display: flex; align-items: center; justify-content: space-between; 
            padding: 0 20px; backdrop-filter: blur(12px); 
        }}
        .logo {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 8px; }}
        .pulse {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(62, 175, 124, 0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62, 175, 124, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62, 175, 124, 0); }} }}
        
        .date {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 13px; color: var(--sub); }}
        
        .switcher {{ display: flex; background: var(--vp-c-bg-mute, #eee); padding: 3px; border-radius: 20px; gap: 2px; border: 1px solid var(--border); }}
        .sw-btn {{ padding: 5px 10px; border-radius: 15px; font-size: 9px; font-weight: 800; cursor: pointer; border: none; background: transparent; color: var(--sub); }}
        .sw-btn.active {{ background: var(--text); color: var(--bg); }}

        .container {{ width: 100%; max-width: 1200px; margin: 100px auto; padding: 0 24px; }}

        /* --- BENTO MODE --- */
        [data-ui="bento"] .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        [data-ui="bento"] .news-item {{ background: var(--vp-c-bg-soft, rgba(0,0,0,0.03)); border-radius: 16px; padding: 20px; border: 1px solid var(--border); transition: 0.2s; }}
        [data-ui="bento"] .news-item.wide {{ grid-column: span 2; }}
        [data-ui="bento"] .title {{ font-size: 18px; font-weight: 700; margin: 0 0 10px; }}

        /* --- FEED MODE --- */
        [data-ui="feed"] .container {{ max-width: 750px; }}
        [data-ui="feed"] .news-item {{ border-bottom: 1px solid var(--border); padding: 25px 0; }}
        [data-ui="feed"] .title {{ font-size: 22px; font-weight: 700; margin-bottom: 8px; }}

        /* --- TERMINAL MODE --- */
        [data-ui="terminal"] body {{ background: #000; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="terminal"] .nav {{ background: #000; border-color: #00ff41; color: #00ff41; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; padding: 15px; margin-bottom: 12px; }}
        [data-ui="terminal"] .title {{ color: #fff; font-size: 15px; text-transform: uppercase; }}
        [data-ui="terminal"] .sw-btn.active {{ background: #00ff41; color: #000; }}

        @media (max-width: 768px) {{
            .date {{ position: static; transform: none; margin: 0 auto; order: 2; font-size: 11px; }}
            .logo {{ order: 1; }}
            .switcher {{ order: 3; }}
            [data-ui="bento"] .news-item.wide {{ grid-column: span 1; }}
            .items {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body data-theme="light">
    <nav class="nav">
        <div class="logo"><div class="pulse"></div> N.I.U.S.</div>
        <div class="date">{current_date}</div>
        <div class="switcher">
            <button class="sw-btn" onclick="setUI('bento')" id="btn-bento">BENTO</button>
            <button class="sw-btn" onclick="setUI('feed')" id="btn-feed">FEED</button>
            <button class="sw-btn" onclick="setUI('terminal')" id="btn-terminal">TERM</button>
        </div>
    </nav>

    <main class="container">
        <div class="items">{cards_html}</div>
    </main>

    <script>
        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-ui-pref', mode);
            document.querySelectorAll('.sw-btn').forEach(b => b.classList.remove('active'));
            document.getElementById('btn-' + mode).classList.add('active');
        }}

        window.onload = () => {{
            const saved = localStorage.getItem('nius-ui-pref') || 'bento';
            setUI(saved);
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                document.body.setAttribute('data-theme', 'dark');
            }}
        }};
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    cards = fetch_news()
    generate_index_html(cards)
