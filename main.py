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
    short_date = datetime.now().strftime("%d-%b-%Y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="columnist" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@1,700&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 60px; --font-main: 'Inter', sans-serif;
            --ft-title: clamp(1rem, 1.2vw + 0.5rem, 1.25rem);
            --ft-details: clamp(0.8rem, 0.7vw + 0.4rem, 0.9rem);
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626;
        }}
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; overflow-y: auto; overflow-x: hidden; }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 15px; backdrop-filter: blur(15px); }}
        .logo {{ font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; text-decoration: none; color: inherit; }}
        .pulse {{ width: 6px; height: 6px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 700; font-size: 9px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.1em; }}
        
        .nav-actions {{ display: flex; align-items: center; gap: 8px; }}
        select {{ background: var(--border); color: var(--text); border: none; padding: 4px 6px; border-radius: 4px; font-size: 9px; font-weight: 800; cursor: pointer; outline: none; }}

        .container {{ width: 100%; max-width: 1000px; margin: 80px auto 40px; padding: 0 15px; }}
        .items {{ display: grid; gap: 20px; }}

        /* --- MODELS --- */
        [data-ui="columnist"] .items {{ grid-template-columns: 1fr 1fr; gap: 30px; }}
        [data-ui="columnist"] .news-item {{ border-left: 2px solid var(--border); padding-left: 15px; }}

        [data-ui="feed"] .container {{ max-width: 600px; }}
        [data-ui="feed"] .news-item {{ border-bottom: 1px solid var(--border); padding: 20px 0; }}
        [data-ui="feed"] .title {{ color: var(--accent); }}

        [data-ui="terminal"] body {{ background: #000; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; padding: 10px; margin-bottom: 8px; }}
        [data-ui="terminal"] a {{ color: #fff; text-decoration: none; }}

        [data-ui="magazine"] .title {{ font-family: 'Playfair Display', serif; font-size: 1.6rem; font-style: italic; }}
        [data-ui="magazine"] .news-item {{ border-bottom: 1px solid var(--border); padding: 25px 0; }}

        [data-ui="cards"] .items {{ grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }}
        [data-ui="cards"] .news-item {{ background: var(--bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}

        [data-ui="newspaper"] .items {{ column-count: 3; column-gap: 30px; display: block; }}
        [data-ui="newspaper"] .news-item {{ break-inside: avoid; border-bottom: 0.5px solid #444; padding-bottom: 12px; margin-bottom: 12px; }}

        /* Typography */
        .title {{ line-height: 1.2; font-weight: 800; margin: 0 0 6px; font-size: var(--ft-title); }}
        .title a {{ text-decoration: none; color: inherit; transition: color 0.2s; }}
        .title a:hover {{ color: var(--accent); }}
        .details {{ font-size: var(--ft-details); line-height: 1.45; color: var(--sub); margin-bottom: 0; }}
        b {{ color: var(--text); font-weight: 700; }}

        @media (max-width: 768px) {{
            [data-ui="columnist"] .items {{ grid-template-columns: 1fr; }}
            [data-ui="newspaper"] .items {{ column-count: 1; }}
            .container {{ margin-top: 75px; padding: 0 12px; }}
            .date-center {{ font-size: 8px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="logo"><div class="pulse"></div> N.I.U.S.</div>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        <div class="nav-actions">
            <select id="ui-selector" onchange="setUI(this.value)">
                <option value="columnist">COLUMNIST</option>
                <option value="feed">INTEL</option>
                <option value="terminal">TERM</option>
                <option value="newspaper">NEWS</option>
                <option value="magazine">MAG</option>
                <option value="cards">CARDS</option>
            </select>
        </div>
    </nav>
    <main class="container"><div class="items" id="news-grid">{cards_html}</div></main>
    <script>
        function updateDate() {{
            const el = document.getElementById('live-date');
            el.innerText = window.innerWidth < 768 ? el.getAttribute('data-short') : el.getAttribute('data-full');
        }}
        window.addEventListener('resize', updateDate);

        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-pro-pref', mode);
            document.getElementById('ui-selector').value = mode;
        }}

        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-pro-pref') || 'columnist');
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) document.documentElement.setAttribute('data-theme', 'dark');
        }};
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    cards = fetch_news()
    generate_index_html(cards)
