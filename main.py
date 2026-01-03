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

# --- 2. SUMMARIZATION LOGIC ---
def clean_and_summarize(raw_html, limit=180):
    text = re.sub(r'<[^>]+>', '', raw_html)
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0] + "..."
    for word in TECH_KEYWORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f"<b>{word}</b>", text)
    return text

# --- 3. DATA FETCHING ---
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
    for i, entry in enumerate(all_entries[:12]): # Fetches 12 stories
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        # Mark items for Bento layout logic
        size_class = "wide" if i in [0, 4, 7] else "regular"
        cards_html += f"""
        <article class="news-item {size_class}">
            <div class="content">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <a href="{entry.link}" target="_blank" class="source-link">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
                    Intelligence Source
                </a>
            </div>
        </article>"""
    return cards_html

# --- 4. HTML GENERATION ---
def generate_index_html(cards_html):
    current_date = datetime.now().strftime("%B %d, %Y").lower()
    
    sun_icon = '<svg class="sun" viewBox="0 0 24 24"><path d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.415-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/></svg>'
    moon_icon = '<svg class="moon" viewBox="0 0 24 24"><path d="M12.3 22.1c1.2-1.2 1.5-2.4 1.3-3.2-.2-.8-1-1.4-1.7-1.4H10c-3.6 0-6.6-2.9-6.6-6.4 0-3.3 2.5-6.1 5.8-6.5 1.4-.2 2.6.4 3.4 1.3.8.9 1 2.1.6 3.2-.4 1.1-1.3 1.8-2.5 1.8h-1c-.6 0-1 .4-1 1s.4 1 1 1h4c2.5 0 4.8 1.1 6.3 3 .6.8.9 1.7.9 2.6 0 2.4-1.6 4.6-4 5.2-1.1.3-2.3.1-3.3-.4-.3-.2-.5-.3-.7-.5z"/></svg>'

    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #0071e3; --border: #e2e2e3;
            --nav-h: 64px; --font-main: 'Inter', sans-serif;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #2e2e32;
        }}
        
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; transition: background 0.3s; }}

        /* --- NAVIGATION --- */
        .nav {{ 
            position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); 
            background: var(--bg); border-bottom: 1px solid var(--border); 
            z-index: 2000; display: flex; align-items: center; justify-content: space-between; 
            padding: 0 24px; backdrop-filter: blur(12px); 
        }}
        .logo {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 8px; }}
        .pulse {{ width: 8px; height: 8px; background: #34c759; border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(52,199,89,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(52,199,89,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(52,199,89,0); }} }}
        
        .date {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 12px; color: var(--sub); text-transform: uppercase; }}
        
        .nav-actions {{ display: flex; align-items: center; gap: 12px; }}
        .theme-toggle {{ cursor: pointer; border: none; background: transparent; color: var(--text); padding: 5px; display: flex; }}
        .theme-toggle svg {{ width: 20px; height: 20px; fill: currentColor; }}
        [data-theme="dark"] .sun, [data-theme="light"] .moon {{ display: none; }}

        select {{ 
            background: var(--border); color: var(--text); border: none; padding: 6px 10px; 
            border-radius: 8px; font-size: 11px; font-weight: 700; cursor: pointer; outline: none;
        }}

        .container {{ width: 100%; max-width: 1200px; margin: 100px auto 40px; padding: 0 24px; }}

        /* --- MODEL 1: BENTO (Compact Modern) --- */
        [data-ui="bento"] .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }}
        [data-ui="bento"] .news-item {{ background: var(--bg); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }}
        [data-ui="bento"] .news-item.wide {{ grid-column: span 2; }}
        [data-ui="bento"] .title {{ font-size: 18px; font-weight: 800; }}

        /* --- MODEL 2: FEED (Minimal Narrative) --- */
        [data-ui="feed"] .container {{ max-width: 650px; }}
        [data-ui="feed"] .news-item {{ border-bottom: 1px solid var(--border); padding: 40px 0; }}
        [data-ui="feed"] .title {{ font-size: 26px; font-weight: 700; letter-spacing: -0.02em; }}

        /* --- MODEL 3: TERMINAL (Hacker Aesthetic) --- */
        [data-ui="terminal"] body {{ background: #050505; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="terminal"] .nav {{ background: #000; border-color: #00ff41; color: #00ff41; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; padding: 15px; margin-bottom: 15px; border-left: 4px solid #00ff41; }}
        [data-ui="terminal"] .title {{ color: #fff; text-transform: uppercase; font-size: 14px; }}
        [data-ui="terminal"] .source-link {{ color: #00ff41; }}

        /* --- MODEL 4: MAGAZINE (Classic Serif) --- */
        [data-ui="magazine"] body {{ background: #fdfcf8; color: #1a1a1a; }}
        [data-ui="magazine"] .title {{ font-family: 'Playfair Display', serif; font-size: 28px; font-style: italic; }}
        [data-ui="magazine"] .news-item {{ border-top: 3px solid #1a1a1a; padding-top: 20px; margin-bottom: 40px; }}

        /* --- MODEL 5: CARDS (Shadow & Depth) --- */
        [data-ui="cards"] .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; }}
        [data-ui="cards"] .news-item {{ background: var(--bg); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); padding: 30px; border: 1px solid var(--border); }}

        .source-link {{ display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 800; color: var(--accent); text-decoration: none; margin-top: auto; }}
        .source-link svg {{ width: 14px; height: 14px; }}
        b {{ color: var(--text); font-weight: 700; }}

        @media (max-width: 768px) {{
            .date {{ display: none; }}
            [data-ui="bento"] .news-item.wide {{ grid-column: span 1; }}
            .container {{ padding: 0 16px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/" class="logo"><div class="pulse"></div> N.I.U.S.</a>
        <div class="date">{current_date}</div>
        <div class="nav-actions">
            <button class="theme-toggle" onclick="toggleTheme()">{sun_icon}{moon_icon}</button>
            <select id="ui-selector" onchange="setUI(this.value)">
                <option value="bento">BENTO GRID</option>
                <option value="feed">INTEL FEED</option>
                <option value="terminal">TERMINAL</option>
                <option value="magazine">MAGAZINE</option>
                <option value="cards">DEPTH CARDS</option>
            </select>
        </div>
    </nav>

    <main class="container"><div class="items">{cards_html}</div></main>

    <script>
        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-ui-v5', mode);
            document.getElementById('ui-selector').value = mode;
        }}

        function toggleTheme() {{
            const current = document.documentElement.getAttribute('data-theme');
            const target = current === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('nius-theme-v5', target);
        }}

        window.onload = () => {{
            setUI(localStorage.getItem('nius-ui-v5') || 'bento');
            const savedTheme = localStorage.getItem('nius-theme-v5') || 
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            document.documentElement.setAttribute('data-theme', savedTheme);
        }};
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    cards = fetch_news()
    generate_index_html(cards)
