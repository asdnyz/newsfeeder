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

TECH_KEYWORDS = ["Tech","AI", "Nvidia", "Apple", "GPT", "OpenAI", "Microsoft", "LLM", "Silicon", "Tesla", "Fintech", "Market", "Economy"]

# --- 2. SUMMARIZATION LOGIC ---
def clean_and_summarize(raw_html, limit=200):
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
    print("📡 Syncing VitePress Terminal...")
    all_entries = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            print(f"⚠️ Feed Error: {e}")

    # Sort by date (newest first)
    all_entries.sort(key=lambda x: x.get('published_parsed') or x.get('updated_parsed'), reverse=True)
    
    cards_html = ""
    link_icon = '<svg class="link-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>'

    for entry in all_entries[:6]:
        summary = clean_and_summarize(entry.get('summary', '') or entry.get('description', ''))
        cards_html += f"""
        <div class="VPFeature">
            <article class="box">
                <h2 class="title">{entry.title}</h2>
                <p class="details">{summary}</p>
                <a href="{entry.link}" target="_blank" class="VPLink link">{link_icon} View Source</a>
            </article>
        </div>"""
    return cards_html

# --- 4. HTML GENERATION ---
def generate_index_html(cards_html):
    print("🍏 Building NIUS VitePress UI...")
    
    # Generate the current date label
    current_date = datetime.now().strftime("%B %d, %Y")
    
    sun_icon = '<svg class="vpi-sun" viewBox="0 0 24 24"><path d="M12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12zm0-2a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM11 1h2v3h-2V1zm0 19h2v3h-2v-3zM3.515 4.929l1.414-1.414L7.05 5.636 5.636 7.05 3.515 4.93zM16.95 18.364l1.414-1.414 2.121 2.121-1.414 1.414-2.121-2.121zm2.121-14.85l1.414 1.415-2.121 2.121-1.415-1.414 2.121-2.121zM5.636 16.95l1.414 1.414-2.121 2.121-1.414-1.414 2.121-2.121zM23 11v2h-3v-2h3zM4 11v2H1v-2h3z"/></svg>'
    moon_icon = '<svg class="vpi-moon" viewBox="0 0 24 24"><path d="M12.3 22.1c1.2-1.2 1.5-2.4 1.3-3.2-.2-.8-1-1.4-1.7-1.4H10c-3.6 0-6.6-2.9-6.6-6.4 0-3.3 2.5-6.1 5.8-6.5 1.4-.2 2.6.4 3.4 1.3.8.9 1 2.1.6 3.2-.4 1.1-1.3 1.8-2.5 1.8h-1c-.6 0-1 .4-1 1s.4 1 1 1h4c2.5 0 4.8 1.1 6.3 3 .6.8.9 1.7.9 2.6 0 2.4-1.6 4.6-4 5.2-1.1.3-2.3.1-3.3-.4-.3-.2-.5-.3-.7-.5z"/></svg>'

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>N.I.U.S. | Daily Brief</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{ 
            --vp-c-bg: #ffffff; --vp-c-bg-soft: #f6f6f7; --vp-c-bg-mute: #f1f1f2; 
            --vp-c-text-1: #2c3e50; --vp-c-text-2: #476582; --vp-c-brand: #3eaf7c; 
            --vp-c-border: #e2e2e3; --vp-nav-height: 64px; 
        }}
        html.dark {{ 
            --vp-c-bg: #1b1b1f; --vp-c-bg-soft: #242429; --vp-c-bg-mute: #2e2e32; 
            --vp-c-text-1: rgba(255, 255, 255, 0.87); --vp-c-text-2: rgba(235, 235, 235, 0.6); 
            --vp-c-border: #2e2e32; 
        }}
        body {{ font-family: 'Inter', -apple-system, sans-serif; background-color: var(--vp-c-bg); color: var(--vp-c-text-1); margin: 0; -webkit-font-smoothing: antialiased; }}
        
        /* Fixed Navigation */
        .VPNav {{ position: fixed; top: 0; left: 0; width: 100%; height: var(--vp-nav-height); background-color: var(--vp-c-bg); border-bottom: 1px solid var(--vp-c-border); z-index: 1000; backdrop-filter: blur(8px); display: flex; align-items: center; }}
        .VPNavBar {{ width: 100%; max-width: 1280px; margin: 0 auto; padding: 0 32px; display: flex; align-items: center; justify-content: space-between; }}
        .logo-main {{ font-weight: 700; font-size: 16px; display: flex; align-items: center; gap: 8px; color: var(--vp-c-text-1); text-decoration: none; }}
        .nav-center {{ position: absolute; left: 50%; transform: translateX(-50%); font-weight: 600; font-size: 13px; color: var(--vp-c-text-2); text-transform: lowercase; }}
        
        .pulse {{ width: 8px; height: 8px; background: var(--vp-c-brand); border-radius: 50%; animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0% {{ box-shadow: 0 0 0 0 rgba(62, 175, 124, 0.7); }} 70% {{ box-shadow: 0 0 0 10px rgba(62, 175, 124, 0); }} 100% {{ box-shadow: 0 0 0 0 rgba(62, 175, 124, 0); }} }}
        
        .appearance {{ cursor: pointer; background: var(--vp-c-bg-mute); border-radius: 20px; width: 40px; height: 22px; position: relative; border: 1px solid var(--vp-c-border); }}
        .appearance-check {{ width: 18px; height: 18px; background: #fff; border-radius: 50%; position: absolute; top: 1px; left: 1px; transition: 0.2s; display: flex; align-items: center; justify-content: center; }}
        html.dark .appearance-check {{ left: 19px; background: #000; }}
        .vpi-sun, .vpi-moon {{ width: 12px; height: 12px; fill: currentColor; }}
        html.dark .vpi-sun {{ display: none; }}
        html:not(.dark) .vpi-moon {{ display: none; }}

        /* Main Layout */
        .container {{ max-width: 1152px; margin: 100px auto 40px; padding: 0 24px; }}
        
        /* Date Header Styles */
        .date-header {{ border-bottom: 1px solid var(--vp-c-border); padding-bottom: 12px; margin-bottom: 32px; }}
        .date-label {{ font-size: 24px; font-weight: 800; letter-spacing: -0.02em; }}
        .date-sub {{ font-size: 14px; color: var(--vp-c-text-2); font-weight: 500; margin-top: 4px; }}

        /* Grid - Fixed Overlap */
        .items {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }}
        .box {{ display: flex; flex-direction: column; height: 100%; padding: 24px; border-radius: 12px; border: 1px solid var(--vp-c-bg-soft); background-color: var(--vp-c-bg-soft); transition: border-color 0.25s; }}
        .box:hover {{ border-color: var(--vp-c-brand); }}
        .title {{ line-height: 1.4; font-size: 18px; font-weight: 700; margin: 0 0 12px; }}
        .details {{ flex-grow: 1; line-height: 1.6; font-size: 14px; color: var(--vp-c-text-2); margin-bottom: 20px; }}
        .VPLink {{ font-size: 13px; font-weight: 600; color: var(--vp-c-brand); text-decoration: none; display: flex; align-items: center; gap: 6px; }}
        .link-icon {{ width: 14px; height: 14px; }}
        b {{ color: var(--vp-c-text-1); font-weight: 700; }}

        @media (max-width: 768px) {{
            .nav-center {{ display: none; }}
            .container {{ margin-top: 80px; padding: 0 16px; }}
            .items {{ grid-template-columns: 1fr; gap: 16px; }}
            .date-label {{ font-size: 20px; }}
        }}
    </style>
</head>
<body>
    <header class="VPNav">
        <div class="VPNavBar">
            <a href="/" class="logo-main"><div class="pulse"></div> N.I.U.S.</a>
            <div class="nav-center">{current_date}</div>
            <div class="appearance" onclick="toggleTheme()">
                <div class="appearance-check">{sun_icon}{moon_icon}</div>
            </div>
        </div>
    </header>

    <main class="container">
        <div class="items">{cards_html}</div>
    </main>

    <script>
        function toggleTheme() {{
            document.documentElement.classList.toggle('dark');
            const isDark = document.documentElement.classList.contains('dark');
            localStorage.setItem('vitepress-theme-appearance', isDark ? 'dark' : 'light');
        }}
        (function() {{
            const saved = localStorage.getItem('vitepress-theme-appearance');
            if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
                document.documentElement.classList.add('dark');
            }}
        }})();
    </script>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(full_html)

if __name__ == "__main__":
    cards = fetch_news()
    generate_index_html(cards)
