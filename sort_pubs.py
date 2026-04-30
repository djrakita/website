import yaml

with open('publications.yml', 'r') as f:
    data = yaml.safe_load(f)

journals = []
conferences = []
preprints = []
others = []

for item in data:
    t = item.get('type', '')
    if t == 'Journal':
        journals.append(item)
    elif t == 'Conference':
        conferences.append(item)
    elif t == 'Preprint':
        preprints.append(item)
    else:
        others.append(item)

# Sort descending by year
journals.sort(key=lambda x: x.get('year', 0), reverse=True)
conferences.sort(key=lambda x: x.get('year', 0), reverse=True)
preprints.sort(key=lambda x: x.get('year', 0), reverse=True)
others.sort(key=lambda x: x.get('year', 0), reverse=True)

with open('publications.yml', 'w') as f:
    if preprints:
        f.write("# ==========================================\n")
        f.write("# Preprints\n")
        f.write("# ==========================================\n\n")
        yaml.dump(preprints, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
        f.write("\n")
        
    if journals:
        f.write("# ==========================================\n")
        f.write("# Journal Articles\n")
        f.write("# ==========================================\n\n")
        yaml.dump(journals, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
        f.write("\n")
        
    if conferences:
        f.write("# ==========================================\n")
        f.write("# Conference Papers\n")
        f.write("# ==========================================\n\n")
        yaml.dump(conferences, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
        f.write("\n")
        
    if others:
        f.write("# ==========================================\n")
        f.write("# Other\n")
        f.write("# ==========================================\n\n")
        yaml.dump(others, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
        f.write("\n")

