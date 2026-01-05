import os
import re
import feedparser
import urllib.request
from datetime import datetime

# --- 1. CONFIGURATION ---
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Hacker News": "https://news.ycombinator.com/rss",
    "BBC Tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "Reuters Tech": "https://www.reutersagency.com/feed/?best-sectors=technology&post_type=best"
}

TECH_KEYWORDS = ["AI", "Nvidia", "Apple", "GPT", "OpenAI", "Microsoft", "LLM", "Silicon", "Tesla", "Fintech"]

def clean_and_summarize(raw_html, limit=180):
    text = re.sub(r'<[^>]+>', '', raw_html)
    text = " ".join(text.split())
    if not text or text.lower() == "comments":
        return None
    if len(text) > limit:
        text = text[:limit].rsplit(' ', 1)[0] + "..."
    for word in TECH_KEYWORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub(f"<b>{word}</b>", text)
    return text

def fetch_data():
    all_entries = []
    unique_sources = list(RSS_FEEDS.keys())
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for source, url in RSS_FEEDS.items():
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                feed = feedparser.parse(response.read())
                for entry in feed.entries:
                    summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
                    if summary:
                        entry['processed_summary'] = summary
                        entry['source_label'] = source
                        all_entries.append(entry)
        except: pass

    all_entries.sort(key=lambda x: x.get('published_parsed') or x.get('updated_parsed'), reverse=True)
    
    # 1. Generate News Cards
    cards_html = ""
    for entry in all_entries[:15]:
        cards_html += f"""
        <article class="news-item" data-source="{entry['source_label']}">
            <div class="content">
                <div class="source-tag">{entry['source_label']}</div>
                <h2 class="title"><a href="{entry.link}" target="_blank">{entry.title}</a></h2>
                <p class="details">{entry['processed_summary']}</p>
            </div>
        </article>"""
        
    # 2. Generate Automatic Filter Buttons
    buttons_html = '<button class="menu-item filter-btn active" onclick="filterSource(\'all\', this)">All Feeds</button>'
    for source in unique_sources:
        buttons_html += f'<button class="menu-item filter-btn" onclick="filterSource(\'{source}\', this)">{source}</button>'
    
    # 3. Generate Headline Ticker (Source : Title | ...)
    ticker_content = " +++ ".join([f"{e['source_label']} : {e['title']}" for e in all_entries[:20]])
    ticker_html = f'<div class="ticker-text">{ticker_content} +++ {ticker_content}</div>'
        
    return cards_html, buttons_html, ticker_html

def generate_index_html(cards_html, buttons_html, ticker_html):
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
            --nav-h: 80px; --ticker-h: 40px; --font-main: 'Inter', sans-serif;
            --menu-bg: #ffffff;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #262626; --menu-bg: #111111;
        }}
        html {{ font-size: 18px; }} 
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; transition: background 0.3s; overflow-x: hidden; }}

        /* --- TERMINAL --- */
        [data-ui="terminal"] body {{ background: #000 !important; color: #00ff41 !important; font-family: 'JetBrains Mono', monospace !important; }}
        [data-ui="terminal"] .nav, [data-ui="terminal"] .ticker-wrap {{ background: #000; border-color: #00ff41; color: #00ff41; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; border-left: 6px solid #00ff41; background: #000; }}
        [data-ui="terminal"] .title a, [data-ui="terminal"] .ticker-text {{ color: #00ff41; }}

        /* --- TICKER --- */
        .ticker-wrap {{ position: fixed; top: var(--nav-h); width: 100%; height: var(--ticker-h); background: var(--text); color: var(--bg); z-index: 1900; overflow: hidden; display: flex; align-items: center; border-bottom: 1px solid var(--border); }}
        .ticker-text {{ white-space: nowrap; display: inline-block; padding-left: 100%; animation: ticker 60s linear infinite; font-family: 'JetBrains Mono'; font-weight: 800; font-size: 14px; text-transform: uppercase; }}
        @keyframes ticker {{ 0% {{ transform: translate3d(0, 0, 0); }} 100% {{ transform: translate3d(-100%, 0, 0); }} }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; backdrop-filter: blur(15px); }}
        .logo {{ font-weight: 800; font-size: 20px; text-decoration: none; color: inherit; }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 800; font-size: 14px; color: var(--sub); text-transform: uppercase; white-space: nowrap; display: flex; align-items: center; gap: 10px; }}
        .pulse {{ width: 10px; height: 10px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 10px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        
        #menu-toggle {{ display: none; }}
        .sandwich {{ cursor: pointer; z-index: 2100; display: flex; flex-direction: column; gap: 6px; }}
        .sandwich span {{ width: 28px; height: 3px; background: var(--text); transition: 0.3s; }}
        
        .nav-actions {{ position: fixed; top: 0; right: -100%; width: 300px; height: 100vh; background: var(--menu-bg); border-left: 1px solid var(--border); display: flex; flex-direction: column; padding: 100px 30px; gap: 18px; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); z-index: 2050; box-shadow: -15px 0 45px rgba(0,0,0,0.15); }}
        #menu-toggle:checked ~ .nav-actions {{ right: 0; }}
        .menu-overlay {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.4); z-index: 2040; display: none; }}
        #menu-toggle:checked ~ .menu-overlay {{ display: block; }}

        .menu-item {{ padding: 15px 20px; border-radius: 12px; font-size: 14px; font-weight: 800; color: var(--text); background: var(--border); border: none; cursor: pointer; text-align: left; }}
        .filter-btn.active {{ background: var(--accent); color: white; }}
        .close-btn {{ margin-top: auto; background: var(--text); color: var(--bg); text-align: center; }}

        /* --- CONTENT --- */
        .container {{ width: 100%; max-width: 1200px; margin: calc(var(--nav-h) + var(--ticker-h) + 40px) auto 60px; padding: 0 30px; }}
        .items {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }}
        .news-item {{ border-left: 4px solid var(--border); padding-left: 20px; transition: 0.3s; }}
        .source-tag {{ font-size: 11px; font-weight: 800; color: var(--accent); text-transform: uppercase; margin-bottom: 8px; }}
        .title {{ font-size: 1.4rem; line-height: 1.25; font-weight: 800; margin: 0 0 12px; }}
        .title a {{ text-decoration: none; color: inherit; }}
        .details {{ font-size: 1.1rem; line-height: 1.55; color: var(--sub); }}

        @media (max-width: 768px) {{
            .items {{ grid-template-columns: 1fr; }}
            .container {{ margin-top: calc(var(--nav-h) + var(--ticker-h) + 30px); }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="#" class="logo">N.I.U.S.</a>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">
            <div class="pulse"></div> {full_date}
        </div>
        
        <div class="menu-wrap">
            <input type="checkbox" id="menu-toggle">
            <div class="menu-overlay" onclick="toggleMenu(false)"></div>
            <label for="menu-toggle" class="sandwich"><span></span><span></span><span></span></label>
            
            <div class="nav-actions">
                <button class="menu-item" style="color:var(--accent)" onclick="toggleTheme()">🌓 TOGGLE APPEARANCE</button>
                <div style="font-size: 12px; font-weight: 800; color: var(--sub); margin-top: 15px;">SOURCE FILTER</div>
                {buttons_html}
                <div style="font-size: 12px; font-weight: 800; color: var(--sub); margin-top: 15px;">LAYOUT</div>
                <button class="menu-item" onclick="setUI('columnist')">Columnist</button>
                <button class="menu-item" onclick="setUI('terminal')">Terminal</button>
                <button class="menu-item close-btn" onclick="toggleMenu(false)">✕ CLOSE MENU</button>
            </div>
        </div>
    </nav>

    <div class="ticker-wrap">{ticker_html}</div>

    <main class="container"><div class="items" id="news-grid">{cards_html}</div></main>
    <script>
        function updateDate() {{
            const el = document.getElementById('live-date');
            const dateStr = window.innerWidth < 768 ? el.getAttribute('data-short') : el.getAttribute('data-full');
            el.innerHTML = '<div class="pulse"></div> ' + dateStr;
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
            localStorage.setItem('nius-final-theme', t);
        }}
        function setUI(m) {{
            document.documentElement.setAttribute('data-ui', m);
            localStorage.setItem('nius-final-ui', m);
            toggleMenu(false);
        }}
        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-final-ui') || 'columnist');
            const theme = localStorage.getItem('nius-final-theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            document.documentElement.setAttribute('data-theme', theme);
        }};
    </script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    c_html, b_html, t_html = fetch_data()
    generate_index_html(c_html, b_html, t_html)
