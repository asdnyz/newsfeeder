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
            <h2 class="title"><a href="{entry.link}" target="_blank">{entry.title}</a></h2>
            <p class="details">{summary}</p>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    # Fixed date formats for the dynamic switcher
    full_date = datetime.now().strftime("%B %d, %Y").lower()
    short_date = datetime.now().strftime("%d-%b-%Y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="liquid" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    
    <title>N.I.U.S. | Intelligence</title>
    <meta name="description" content="Nexus Intelligence Ultimate Source.">
    <meta name="author" content="Niyaz Asad">

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 60px; --font-main: 'Inter', sans-serif;
            --ft-title: clamp(1rem, 1.2vw + 0.5rem, 1.25rem);
            --ft-details: clamp(0.8rem, 0.7vw + 0.4rem, 0.9rem);
            --blur-bg: rgba(255, 255, 255, 0.7);
            --menu-bg: #ffffff;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626;
            --blur-bg: rgba(0, 0, 0, 0.7);
            --menu-bg: #111111;
        }}
        
        /* ADAPTIVE TERMINAL LOGIC */
        [data-ui="terminal"] {{ font-family: 'JetBrains Mono', monospace !important; }}
        [data-ui="terminal"] .news-item {{ 
            border: 1px solid var(--accent); 
            padding: 15px; 
            border-left: 6px solid var(--accent); 
            background: var(--bg); 
            margin-bottom: 12px;
        }}
        [data-ui="terminal"] .title a {{ color: var(--text); text-decoration: none; text-transform: uppercase; font-size: 13px; }}
        [data-ui="terminal"] b {{ color: var(--accent); }}

        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; transition: background 0.4s; overflow-x: hidden; min-height: 100vh; }}

        .liquid-bg {{ 
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; display: none;
            background: radial-gradient(circle at 20% 30%, rgba(62,175,124,0.1) 0%, transparent 40%),
                        radial-gradient(circle at 80% 70%, rgba(0,113,227,0.1) 0%, transparent 40%);
            filter: blur(80px); animation: liquid-move 20s infinite alternate;
        }}
        @keyframes liquid-move {{ 0% {{ transform: scale(1); }} 100% {{ transform: scale(1.2) translate(5%, 5%); }} }}
        [data-ui="liquid"] .liquid-bg {{ display: block; }}

        .nav {{ position: fixed; top: 0; width: 100%; height: var(--nav-h); background: var(--blur-bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; backdrop-filter: blur(20px); }}
        .logo {{ font-weight: 800; font-size: 14px; display: flex; align-items: center; gap: 6px; text-decoration: none; color: inherit; z-index: 2100; }}
        .pulse {{ width: 6px; height: 6px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        
        /* DATE HEADER */
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 700; font-size: 9px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.1em; white-space: nowrap; }}
        
        .menu-container {{ display: flex; align-items: center; gap: 10px; }}
        .theme-btn {{ background: none; border: none; cursor: pointer; padding: 8px; color: var(--text); font-size: 16px; }}
        #menu-toggle {{ display: none; }}
        .sandwich {{ display: none; cursor: pointer; z-index: 2100; flex-direction: column; gap: 5px; padding: 10px; }}
        .sandwich span {{ width: 22px; height: 1.5px; background: var(--text); transition: 0.3s; }}

        .nav-actions {{ display: flex; align-items: center; gap: 15px; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}
        select {{ background: var(--border); color: var(--text); border: none; padding: 6px 12px; border-radius: 8px; font-size: 10px; font-weight: 800; cursor: pointer; outline: none; }}

        @media (max-width: 768px) {{
            .sandwich {{ display: flex; }}
            .nav-actions {{
                position: fixed; top: 0; right: -110%; width: 250px; height: 100vh;
                background: var(--menu-bg); border-left: 1px solid var(--border);
                flex-direction: column; padding: 100px 30px; justify-content: flex-start;
                box-shadow: -10px 0 30px rgba(0,0,0,0.1);
            }}
            #menu-toggle:checked ~ .nav-actions {{ right: 0; }}
            #menu-toggle:checked ~ .sandwich span:nth-child(1) {{ transform: translateY(6.5px) rotate(45deg); }}
            #menu-toggle:checked ~ .sandwich span:nth-child(2) {{ opacity: 0; }}
            #menu-toggle:checked ~ .sandwich span:nth-child(3) {{ transform: translateY(-6.5px) rotate(-45deg); }}
            .date-center {{ font-size: 8px; }}
        }}

        .container {{ width: 100%; max-width: 1000px; margin: 90px auto 40px; padding: 0 20px; }}
        .items {{ display: grid; gap: 20px; }}
        [data-ui="liquid"] .items {{ grid-template-columns: 1fr 1fr; gap: 25px; }}
        [data-ui="liquid"] .news-item {{ background: var(--blur-bg); backdrop-filter: blur(10px); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }}
        [data-ui="columnist"] .items {{ grid-template-columns: 1fr 1fr; border-top: 1px solid var(--border); padding-top: 20px; }}
        [data-ui="feed"] .container {{ max-width: 600px; }}
        [data-ui="magazine"] .title {{ font-family: 'Playfair Display', serif; font-size: 1.8rem; }}

        .title {{ line-height: 1.25; font-weight: 800; margin: 0 0 8px; font-size: var(--ft-title); }}
        .title a {{ text-decoration: none; color: inherit; }}
        .details {{ font-size: var(--ft-details); line-height: 1.5; color: var(--sub); }}
        b {{ color: var(--text); font-weight: 700; }}

        @media (max-width: 768px) {{
            .items, [data-ui="liquid"] .items {{ grid-template-columns: 1fr; }}
            .container {{ margin-top: 80px; padding: 0 15px; }}
        }}
    </style>
</head>
<body>
    <div class="liquid-bg"></div>
    <nav class="nav">
        <a href="#" class="logo"><div class="pulse"></div> N.I.U.S.</a>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        
        <div class="menu-container">
            <input type="checkbox" id="menu-toggle">
            <label for="menu-toggle" class="sandwich">
                <span></span><span></span><span></span>
            </label>
            
            <div class="nav-actions">
                <button class="theme-btn" onclick="toggleTheme()">🌓</button>
                <select id="ui-selector" onchange="setUI(this.value)">
                    <option value="liquid">LIQUID GLASS</option>
                    <option value="columnist">COLUMNIST</option>
                    <option value="feed">INTEL FEED</option>
                    <option value="terminal">TERMINAL</option>
                    <option value="newspaper">NEWSPAPER</option>
                    <option value="magazine">MAGAZINE</option>
                </select>
            </div>
        </div>
    </nav>

    <main class="container"><div class="items" id="news-grid">{cards_html}</div></main>

    <script>
        // DYNAMIC DATE SWITCHER
        function updateDate() {{
            const el = document.getElementById('live-date');
            if (window.innerWidth < 768) {{
                el.innerText = el.getAttribute('data-short');
            }} else {{
                el.innerText = el.getAttribute('data-full');
            }}
        }}
        window.addEventListener('resize', updateDate);

        function toggleTheme() {{
            const target = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('nius-v18-theme', target);
        }}

        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-v18-ui', mode);
            document.getElementById('ui-selector').value = mode;
            document.getElementById('menu-toggle').checked = false;
        }}

        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-v18-ui') || 'liquid');
            const theme = localStorage.getItem('nius-v18-theme') || 
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
