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
    for i, entry in enumerate(all_entries[:12]):
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        size_class = "wide" if i in [0, 4, 7] else "regular"
        cards_html += f"""
        <article class="news-item {size_class}">
            <div class="content">
                <h2 class="title"><a href="{entry.link}" target="_blank">{entry.title}</a></h2>
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
    full_date = datetime.now().strftime("%B %d, %Y").lower()
    short_date = datetime.now().strftime("%d-%b-%y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@0,700;1,700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #0071e3; --border: #e2e2e3;
            --nav-h: 60px; --font-main: 'Inter', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --ft-title: clamp(1rem, 1.2vw + 0.5rem, 1.25rem);
            --ft-details: clamp(0.8rem, 0.7vw + 0.4rem, 0.9rem);
            --menu-bg: #ffffff;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626;
            --menu-bg: #111111;
        }}
        
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; transition: background 0.3s; overflow-x: hidden; }}

        /* --- NAVIGATION --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; backdrop-filter: blur(12px); }}
        .logo {{ font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; text-decoration: none; color: inherit; z-index: 2100; }}
        .pulse {{ width: 6px; height: 6px; background: #34c759; border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(52,199,89,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(52,199,89,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(52,199,89,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 700; font-size: 9px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.1em; }}
        
        /* Desktop Actions: Hidden on Mobile */
        .desktop-actions {{ display: flex; align-items: center; gap: 15px; }}
        .theme-btn {{ background: none; border: none; cursor: pointer; font-size: 18px; color: var(--text); }}
        select {{ background: var(--border); color: var(--text); border: none; padding: 6px 10px; border-radius: 8px; font-size: 11px; font-weight: 800; cursor: pointer; outline: none; }}

        /* Sandwich Toggle: Hidden on Desktop */
        #menu-toggle {{ display: none; }}
        .sandwich {{ display: none; cursor: pointer; z-index: 2100; flex-direction: column; gap: 4px; padding: 10px; }}
        .sandwich span {{ width: 20px; height: 2px; background: var(--text); transition: 0.3s; }}

        @media (max-width: 768px) {{
            .desktop-actions {{ display: none; }}
            .sandwich {{ display: flex; }}
            .nav-actions {{
                position: fixed; top: 0; right: -100%; width: 240px; height: 100vh;
                background: var(--menu-bg); border-left: 1px solid var(--border);
                flex-direction: column; padding: 100px 25px; gap: 15px; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: -10px 0 30px rgba(0,0,0,0.1); z-index: 2050;
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
            .theme-toggle-mobile {{ margin-bottom: 10px; font-size: 13px; display: flex; align-items: center; gap: 10px; background: none; color: var(--accent); }}
        }}

        .container {{ width: 100%; max-width: 1200px; margin: 90px auto 40px; padding: 0 20px; }}
        .items {{ display: grid; gap: 20px; }}

        /* --- MODELS --- */
        [data-ui="bento"] .items {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
        [data-ui="bento"] .news-item {{ background: var(--bg); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }}
        [data-ui="bento"] .news-item.wide {{ grid-column: span 2; }}

        [data-ui="terminal"] {{ font-family: var(--font-mono) !important; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid var(--accent); padding: 15px; border-left: 6px solid var(--accent); background: var(--bg); margin-bottom: 12px; }}
        [data-ui="terminal"] .title a {{ color: var(--text); text-decoration: none; text-transform: uppercase; font-size: 13px; }}
        [data-ui="terminal"] b {{ color: #00ff41; font-weight: 800; }}

        .title {{ line-height: 1.25; font-weight: 800; margin: 0 0 8px; font-size: var(--ft-title); }}
        .title a {{ text-decoration: none; color: inherit; transition: color 0.2s; }}
        .details {{ font-size: var(--ft-details); line-height: 1.5; color: var(--sub); }}
        .source-link {{ display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; color: var(--accent); text-decoration: none; margin-top: auto; }}
        .source-link svg {{ width: 12px; height: 12px; }}

        @media (max-width: 768px) {{
            .items {{ grid-template-columns: 1fr !important; }}
            [data-ui="bento"] .news-item.wide {{ grid-column: span 1; }}
            .container {{ margin-top: 80px; padding: 0 15px; }}
            .date-center {{ font-size: 8px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="#" class="logo"><div class="pulse"></div> N.I.U.S.</a>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        
        <div class="desktop-actions">
            <button class="theme-btn" onclick="toggleTheme()">🌓</button>
            <select id="ui-selector" onchange="setUI(this.value)">
                <option value="bento">BENTO GRID</option>
                <option value="feed">INTEL FEED</option>
                <option value="terminal">TERMINAL</option>
                <option value="magazine">MAGAZINE</option>
                <option value="cards">DEPTH CARDS</option>
            </select>
        </div>

        <input type="checkbox" id="menu-toggle">
        <label for="menu-toggle" class="sandwich">
            <span></span><span></span><span></span>
        </label>
        
        <div class="nav-actions">
            <button class="menu-item theme-toggle-mobile" onclick="toggleTheme()">🌓 TOGGLE THEME</button>
            <div style="font-size: 9px; font-weight: 800; color: var(--sub); margin-top: 10px;">SELECT MODEL</div>
            <button class="menu-item" onclick="setUI('bento')">Bento Grid</button>
            <button class="menu-item" onclick="setUI('feed')">Intel Feed</button>
            <button class="menu-item" onclick="setUI('terminal')">Terminal</button>
            <button class="menu-item" onclick="setUI('magazine')">Magazine</button>
            <button class="menu-item" onclick="setUI('cards')">Depth Cards</button>
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
            localStorage.setItem('nius-v-theme', target);
        }}

        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-v-ui', mode);
            if(document.getElementById('ui-selector')) document.getElementById('ui-selector').value = mode;
            document.getElementById('menu-toggle').checked = false;
        }}

        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-v-ui') || 'bento');
            const theme = localStorage.getItem('nius-v-theme') || 
                (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
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
