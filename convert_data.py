import json
import yaml

# publications
with open('publications.json', 'r') as f:
    pub_data = json.load(f)

pubs_yaml = []
for cat in pub_data:
    if 'category' not in cat or 'items' not in cat:
        continue
    
    cat_name = cat['category']
    # map old category to new type
    pub_type = "Journal" if "Journal" in cat_name else "Conference"
    
    for item in cat['items']:
        new_item = {
            'title': item.get('title', '').strip(' .'),
            'authors': item.get('authors', '').replace('<strong>', '').replace('</strong>', '').replace('<b>', '').replace('</b>', ''),
            'type': pub_type,
            'venue': item.get('venue', '').strip(' .'),
            'year': int(item.get('year', 0)),
        }
        if 'pdf' in item:
            new_item['link'] = item['pdf']
        
        # In apollo lab, the ID is not really used, but we might keep it if needed. 
        # Actually apollo format doesn't have ID, so we skip it to match exactly.
        
        # We can try to keep some other fields if we want, but apollo format is:
        # title, authors, type, venue, year, link, threads, video, website, etc.
        pubs_yaml.append(new_item)

with open('publications.yml', 'w') as f:
    yaml.dump(pubs_yaml, f, sort_keys=False, default_flow_style=False, allow_unicode=True)

# news
with open('news.json', 'r') as f:
    news_data = json.load(f)

news_yaml = []
for item in news_data:
    # news.json is currently just a flat list? Let's check its format.
    # We didn't look at news.json yet.
    pass

