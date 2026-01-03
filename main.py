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
    for i, entry in enumerate(all_entries[:12]):
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        cards_html += f"""
        <article class="news-item" data-index="{i}">
            <div class="content">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <div class="swipe-indicator">← DISMISS | SAVE →</div>
                <a href="{entry.link}" target="_blank" class="source-link">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
                    Source Report
                </a>
            </div>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    full_date = datetime.now().strftime("%B %d, %Y").lower()
    short_date = datetime.now().strftime("%d-%b-%Y").lower()
    
    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:ital,wght@1,700&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 64px; --font-main: 'Inter', sans-serif;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #2e2e32;
        }}
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; min-height: 100vh; overflow-y: auto; }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; backdrop-filter: blur(12px); }}
        .logo {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 8px; text-decoration: none; color: inherit; }}
        .pulse {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 11px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .nav-actions {{ display: flex; align-items: center; gap: 8px; }}
        select {{ background: var(--border); color: var(--text); border: none; padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: 800; cursor: pointer; }}

        .container {{ width: 100%; max-width: 1200px; margin: 90px auto 40px; padding: 0 20px; }}
        .items {{ display: grid; gap: 20px; }}

        /* --- MODEL DEFINITIONS --- */
        [data-ui="bento"] .items {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
        [data-ui="bento"] .news-item {{ background: var(--bg); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }}
        
        [data-ui="feed"] .container {{ max-width: 650px; }}
        [data-ui="feed"] .news-item {{ border-bottom: 1px solid var(--border); padding: 30px 0; }}
        [data-ui="feed"] .title {{ font-size: 24px; color: var(--accent); }}

        [data-ui="terminal"] body {{ background: #050505; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="terminal"] .news-item {{ border: 1px solid #00ff41; padding: 15px; border-left: 5px solid #00ff41; }}

        [data-ui="magazine"] .title {{ font-family: 'Playfair Display', serif; font-size: 28px; font-style: italic; border-bottom: 2px solid var(--text); display: inline; }}
        [data-ui="magazine"] .news-item {{ padding: 40px 0; border-bottom: 1px solid var(--border); }}

        [data-ui="cards"] .items {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; }}
        [data-ui="cards"] .news-item {{ background: var(--bg); border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); padding: 25px; border: 1px solid var(--border); }}

        [data-ui="newspaper"] .items {{ column-count: 3; column-gap: 40px; display: block; }}
        [data-ui="newspaper"] .news-item {{ break-inside: avoid; border-bottom: 0.5px solid #333; padding-bottom: 20px; margin-bottom: 20px; }}

        /* --- SWIPER MODE --- */
        [data-ui="swiper"] body {{ overflow: hidden; }}
        [data-ui="swiper"] .container {{ height: 80vh; display: flex; justify-content: center; align-items: center; margin-top: 64px; }}
        [data-ui="swiper"] .items {{ width: 100%; max-width: 380px; height: 500px; position: relative; }}
        [data-ui="swiper"] .news-item {{ position: absolute; width: 100%; height: 100%; display: none; background: var(--bg); border: 1px solid var(--border); border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        [data-ui="swiper"] .news-item.active {{ display: flex; flex-direction: column; }}

        .title {{ line-height: 1.3; font-weight: 800; margin: 0 0 10px; }}
        .details {{ font-size: 13px; line-height: 1.5; color: var(--sub); margin-bottom: 15px; }}
        .source-link {{ display: flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 800; color: var(--accent); text-decoration: none; }}
        .source-link svg {{ width: 12px; height: 12px; }}
        b {{ color: var(--text); font-weight: 700; }}
        .swipe-indicator {{ display: none; margin-top: auto; font-size: 10px; font-weight: 800; opacity: 0.5; }}
        [data-ui="swiper"] .swipe-indicator {{ display: block; }}

        @media (max-width: 768px) {{
            .date-center {{ font-size: 10px; }}
            [data-ui="newspaper"] .items {{ column-count: 1; }}
            .container {{ margin-top: 80px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="logo"><div class="pulse"></div> N.I.U.S.</div>
        <div class="date-center" id="live-date" data-full="{full_date}" data-short="{short_date}">{full_date}</div>
        <div class="nav-actions">
            <select id="ui-selector" onchange="setUI(this.value)">
                <option value="bento">BENTO</option>
                <option value="feed">INTEL</option>
                <option value="terminal">TERM</option>
                <option value="newspaper">NEWS</option>
                <option value="magazine">MAG</option>
                <option value="cards">CARDS</option>
                <option value="randomizer">RAND</option>
                <option value="swiper">SWIPE</option>
            </select>
        </div>
    </nav>
    <main class="container"><div class="items" id="news-grid">{cards_html}</div></main>
    <script>
        function updateDate() {{
            const el = document.getElementById('live-date');
            if (window.innerWidth < 768) el.innerText = el.getAttribute('data-short');
            else el.innerText = el.getAttribute('data-full');
        }}
        window.addEventListener('resize', updateDate);

        function setUI(mode) {{
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-v10-pref', mode);
            const items = Array.from(document.getElementById('news-grid').children);
            items.forEach(el => {{ el.classList.remove('active'); el.style.gridColumn = ''; }});

            if (mode === 'swiper') items[0].classList.add('active');
            if (mode === 'bento') items.forEach((el, i) => {{ if (i % 4 === 0) el.style.gridColumn = 'span 2'; }});
            if (mode === 'randomizer') items.forEach(el => {{ if (Math.random() > 0.7) el.style.gridColumn = 'span 2'; }});
        }}

        window.onload = () => {{
            updateDate();
            setUI(localStorage.getItem('nius-v10-pref') || 'bento');
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
