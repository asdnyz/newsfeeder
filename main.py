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

TECH_KEYWORDS = ["Technology", "AI", "GPT", "Telecom", "Commodity", "Fintech"]

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
        size_class = "wide" if i in [0, 4, 7] else "regular"
        cards_html += f"""
        <article class="news-item {size_class}" data-index="{i}">
            <div class="content">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <div class="swipe-actions">
                    <span>DISMISS</span>
                    <span>SAVE</span>
                </div>
                <a href="{entry.link}" target="_blank" class="source-link">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
                    Full Intel
                </a>
            </div>
        </article>"""
    return cards_html

def generate_index_html(cards_html):
    current_date = datetime.now().strftime("%A, %B %d, %Y").lower()
    sun_icon = '<svg class="sun" viewBox="0 0 24 24"><path d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.415-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/></svg>'
    moon_icon = '<svg class="moon" viewBox="0 0 24 24"><path d="M12.3 22.1c1.2-1.2 1.5-2.4 1.3-3.2-.2-.8-1-1.4-1.7-1.4H10c-3.6 0-6.6-2.9-6.6-6.4 0-3.3 2.5-6.1 5.8-6.5 1.4-.2 2.6.4 3.4 1.3.8.9 1 2.1.6 3.2-.4 1.1-1.3 1.8-2.5 1.8h-1c-.6 0-1 .4-1 1s.4 1 1 1h4c2.5 0 4.8 1.1 6.3 3 .6.8.9 1.7.9 2.6 0 2.4-1.6 4.6-4 5.2-1.1.3-2.3.1-3.3-.4-.3-.2-.5-.3-.7-.5z"/></svg>'

    full_html = f"""<!DOCTYPE html>
<html lang="en" data-ui="bento" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>N.I.U.S.</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@500&family=Playfair+Display:wght@700&family=Libre+Baskerville:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; touch-action: manipulation; }}
        :root {{
            --bg: #ffffff; --text: #1d1d1f; --sub: #86868b; --accent: #3eaf7c; --border: #e2e2e3;
            --nav-h: 64px; --font-main: 'Inter', sans-serif;
        }}
        [data-theme="dark"] {{
            --bg: #000000; --text: #f5f5f7; --sub: #a1a1a6; --border: #2e2e32;
        }}
        body {{ font-family: var(--font-main); background: var(--bg); color: var(--text); margin: 0; padding: 0; transition: background 0.3s; overflow: hidden; }}

        /* --- NAV --- */
        .nav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--nav-h); background: var(--bg); border-bottom: 1px solid var(--border); z-index: 2000; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; backdrop-filter: blur(12px); }}
        .logo {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 8px; text-decoration: none; color: inherit; }}
        .pulse {{ width: 8px; height: 8px; background: var(--accent); border-radius: 50%; animation: p 2s infinite; }}
        @keyframes p {{ 0% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0.4); }} 70% {{ box-shadow: 0 0 0 8px rgba(62,175,124,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62,175,124,0); }} }}
        .date-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 11px; color: var(--sub); text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .nav-actions {{ display: flex; align-items: center; gap: 8px; }}
        .theme-toggle {{ cursor: pointer; border: none; background: transparent; color: var(--text); padding: 4px; display: flex; }}
        .theme-toggle svg {{ width: 18px; height: 18px; fill: currentColor; }}
        [data-theme="dark"] .sun, [data-theme="light"] .moon {{ display: none; }}
        select {{ background: var(--border); color: var(--text); border: none; padding: 5px 8px; border-radius: 6px; font-size: 10px; font-weight: 800; cursor: pointer; }}

        .container {{ width: 100%; max-width: 1200px; margin: 90px auto 40px; padding: 0 20px; }}
        .items {{ display: grid; gap: 16px; position: relative; }}

        /* --- SWIPER MODEL & CONTROLS --- */
        [data-ui="swiper"] .container {{ height: 80vh; display: flex; justify-content: center; align-items: center; margin-top: 64px; overflow: hidden; position: relative; }}
        [data-ui="swiper"] .items {{ width: 100%; max-width: 380px; height: 520px; position: relative; perspective: 1000px; }}
        [data-ui="swiper"] .news-item {{ 
            position: absolute; width: 100%; height: 100%; background: var(--bg); border: 1px solid var(--border);
            border-radius: 24px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            transition: transform 0.4s ease, opacity 0.4s ease; cursor: grab; display: flex; flex-direction: column;
        }}
        [data-ui="swiper"] .news-item:not(.active) {{ display: none; }}
        [data-ui="swiper"] .news-item.active {{ display: flex; z-index: 10; }}

        /* Desktop Arrows */
        .swipe-arrow {{ 
            position: absolute; top: 50%; transform: translateY(-50%); 
            background: var(--border); color: var(--text); border: none;
            width: 48px; height: 48px; border-radius: 50%; cursor: pointer;
            display: none; align-items: center; justify-content: center; z-index: 100;
        }}
        .arrow-left {{ left: -80px; }}
        .arrow-right {{ right: -80px; }}
        [data-ui="swiper"] .swipe-arrow {{ display: flex; }}

        /* --- TYPOGRAPHY --- */
        .title {{ line-height: 1.3; font-weight: 800; margin: 0 0 10px; }}
        .details {{ font-size: 13px; line-height: 1.5; color: var(--sub); margin-bottom: 15px; }}
        .source-link {{ display: flex; align-items: center; gap: 5px; font-size: 11px; font-weight: 800; color: var(--accent); text-decoration: none; }}
        .source-link svg {{ width: 12px; height: 12px; }}
        b {{ color: var(--text); font-weight: 700; }}

        /* --- RESPONSIVE LOGIC --- */
        @media (max-width: 1024px) {{
            [data-ui="swiper"] .swipe-arrow {{ display: none; }} /* Hide on mobile/tablets */
            .container {{ margin-top: 80px; }}
        }}
        @media (orientation: landscape) and (min-width: 1024px) {{
             [data-ui="swiper"] .swipe-arrow {{ display: flex; }} /* Show on landscape desktop */
        }}

        /* OTHER MODELS */
        [data-ui="bento"] .items {{ grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }}
        [data-ui="bento"] .news-item {{ border: 1px solid var(--border); border-radius: 16px; padding: 20px; }}
        [data-ui="bento"] .news-item.wide {{ grid-column: span 2; }}
        [data-ui="terminal"] body {{ background: #050505; color: #00ff41; font-family: 'JetBrains Mono', monospace; }}
        [data-ui="newspaper"] body {{ background: #f4f1ea; color: #222; }}
        [data-ui="newspaper"] .items {{ column-count: 3; column-gap: 40px; display: block; }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="#" class="logo"><div class="pulse"></div> N.I.U.S.</a>
        <div class="date-center">{current_date}</div>
        <div class="nav-actions">
            <button class="theme-toggle" onclick="toggleTheme()">{sun_icon}{moon_icon}</button>
            <select id="ui-selector" onchange="setUI(this.value)">
                <option value="bento">BENTO GRID</option>
                <option value="swiper">SWIPER (TOUCH)</option>
                <option value="feed">INTEL FEED</option>
                <option value="terminal">TERMINAL</option>
                <option value="newspaper">NEWSPAPER</option>
                <option value="magazine">MAGAZINE</option>
                <option value="cards">DEPTH CARDS</option>
                <option value="randomizer">RANDOMIZER</option>
            </select>
        </div>
    </nav>
    <main class="container">
        <div class="items" id="news-grid">
            <button class="swipe-arrow arrow-left" onclick="handleSwipe('left')">←</button>
            {cards_html}
            <button class="swipe-arrow arrow-right" onclick="handleSwipe('right')">→</button>
        </div>
    </main>
    <script>
        let currentIndex = 0;
        let startX = 0;

        function setUI(mode) {{
            const grid = document.getElementById('news-grid');
            const items = Array.from(grid.querySelectorAll('.news-item'));
            document.documentElement.setAttribute('data-ui', mode);
            localStorage.setItem('nius-v9-pref', mode);
            
            items.forEach((el, idx) => {{
                el.classList.remove('active', 'span-wide', 'span-tall');
                el.style.transform = ''; el.style.opacity = '';
                if (mode === 'swiper' && idx === 0) {{ el.classList.add('active'); currentIndex = 0; }}
            }});

            if (mode === 'randomizer') {{
                items.forEach(el => {{
                    if (Math.random() > 0.8) el.classList.add('span-wide');
                    el.style.order = Math.floor(Math.random() * 100);
                }});
            }}
            document.getElementById('ui-selector').value = mode;
        }}

        // GESTURE & CLICK LOGIC
        const grid = document.getElementById('news-grid');
        grid.addEventListener('touchstart', e => startX = e.touches[0].clientX);
        grid.addEventListener('touchend', e => {{
            if (document.documentElement.getAttribute('data-ui') !== 'swiper') return;
            let diff = e.changedTouches[0].clientX - startX;
            if (Math.abs(diff) > 50) handleSwipe(diff > 0 ? 'right' : 'left');
        }});
        grid.addEventListener('mousedown', e => startX = e.clientX);
        grid.addEventListener('mouseup', e => {{
            if (document.documentElement.getAttribute('data-ui') !== 'swiper') return;
            let diff = e.clientX - startX;
            if (Math.abs(diff) > 50) handleSwipe(diff > 0 ? 'right' : 'left');
        }});

        function handleSwipe(dir) {{
            const items = Array.from(grid.querySelectorAll('.news-item'));
            const active = items[currentIndex];
            active.style.transform = `translateX(${{dir === 'right' ? 1000 : -1000}}px) rotate(${{dir === 'right' ? 20 : -20}}deg)`;
            active.style.opacity = '0';
            
            setTimeout(() => {{
                active.classList.remove('active');
                currentIndex = (currentIndex + 1) % items.length;
                items[currentIndex].classList.add('active');
            }}, 400);
        }}

        function toggleTheme() {{
            const target = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', target);
            localStorage.setItem('nius-theme-v9', target);
        }}

        window.onload = () => {{
            setUI(localStorage.getItem('nius-v9-pref') || 'bento');
            const theme = localStorage.getItem('nius-theme-v9') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
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
