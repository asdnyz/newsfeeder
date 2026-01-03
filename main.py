import os
import glob
import re
import feedparser
from datetime import datetime

# --- CONFIGURATION ---
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
        # Adding a 'size-X' class for the Bento layout logic
        size_class = "wide" if i % 4 == 0 else "regular"
        cards_html += f"""
        <article class="news-item {size_class}">
            <div class="content">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <a href="{entry.link}" target="_blank" class="source-link">View Full Intelligence</a>
            </div>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    current_date = datetime.now().strftime("%B %d, %Y").upper()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N.I.U.S. | Multiverse</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #f5f5f7; --text: #1d1d1f; --sub: #86868b; --accent: #0071e3; --border: rgba(0,0,0,0.1);
            --nav-h: 64px; --font-main: 'Inter', sans-serif;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #ffffff; --sub: #86868b; --border: rgba(255,255,255,0.15);
        }}
        
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; transition: 0.3s; }}

        /* --- 3-WAY TOGGLE NAV --- */
        .nav {{ position: fixed; top: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 1000; display: flex; align-items: center; justify-content: space-between; padding: 0 40px; backdrop-filter: blur(10px); }}
        .logo {{ font-weight: 800; font-size: 18px; letter-spacing: -0.05em; }}
        .date {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 12px; opacity: 0.5; }}
        
        .switcher {{ display: flex; background: var(--border); padding: 4px; border-radius: 30px; gap: 4px; }}
        .sw-btn {{ padding: 6px 12px; border-radius: 20px; font-size: 10px; font-weight: 800; cursor: pointer; border: none; background: transparent; color: var(--sub); transition: 0.2s; }}
        .sw-btn.active {{ background: var(--text); color: var(--bg); }}

        .container {{ max-width: 1100px; margin: 100px auto; padding: 0 20px; }}

        /* --- MODE 1: BENTO GRID --- */
        [data-ui="bento"] .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
        [data-ui="bento"] .news-item {{ background: var(--border); border-radius: 20px; padding: 24px; transition: 0.3s; border: 1px solid transparent; }}
        [data-ui="bento"] .news-item.wide {{ grid-column: span 2; }}
        [data-ui="bento"] .news-item:hover {{ transform: scale(1.02); border-color: var(--accent); }}
        [data-ui="bento"] .title {{ font-size: 20px; font-weight: 800; margin: 0 0 12px; }}

        /* --- MODE 2: INTELLIGENCE FEED --- */
        [data-ui="feed"] .container {{ max-width: 700px; }}
        [data-ui="feed"] .news-item {{ border-bottom: 1px solid var(--border); padding: 32px 0; }}
        [data-ui="feed"] .title {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
        [data-ui="feed"] .details {{ font-size: 16px; line-height: 1.6; opacity: 0.8; }}
        [data-ui="feed"] .source-link {{ text-transform: uppercase; font-size: 11px; font-weight: 800; color: var(--accent); text-decoration: none; }}

        /* --- MODE 3: TERMINAL --- */
        [data-ui="terminal"] body {{ background: #0a0a0a; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="terminal"] .nav {{ background: #000; border-color: #00ff41; color: #00ff41; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; padding: 20px; margin-bottom: 10px; box-shadow: 0 0 5px #00ff41; }}
        [data-ui="terminal"] .title {{ font-size: 16px; text-transform: uppercase; color: #fff; }}
        [data-ui="terminal"] b {{ color: #00ff41; background: rgba(0, 255, 65, 0.1); }}
        [data-ui="terminal"] .sw-btn.active {{ background: #00ff41; color: #000; }}

        @media (max-width: 768px) {{
            .date {{ display: none; }}
            [data-ui="bento"] .news-item.wide {{ grid-column: span 1; }}
            .nav {{ padding: 0 15px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="logo">N.I.U.S.</div>
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
            localStorage.setItem('nius-ui', mode);
            
            // Update active button state
            document.querySelectorAll('.sw-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + mode).classList.add('active');
        }}

        // Initialize from local storage
        window.onload = () => {{
            const savedMode = localStorage.getItem('nius-ui') || 'bento';
            setUI(savedMode);
            
            // Auto Dark Mode detect
            if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
                document.documentElement.setAttribute('data-theme', 'dark');
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
