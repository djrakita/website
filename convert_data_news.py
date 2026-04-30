import json
import yaml
from datetime import datetime

with open('news.json', 'r') as f:
    news_data = json.load(f)

news_yaml = []
for item in news_data:
    date_str = item.get('date', '')
    # try to convert "February 2026" to "2026-02-01"
    try:
        dt = datetime.strptime(date_str, '%B %Y')
        date_iso = dt.strftime('%Y-%m-%d')
    except ValueError:
        date_iso = date_str
        
    news_yaml.append({
        'date': date_iso,
        'type': 'Announcement',
        'title': 'News Update', # Default title since old news didn't have titles
        'content': item.get('content', '')
    })

with open('news.yml', 'w') as f:
    yaml.dump(news_yaml, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

