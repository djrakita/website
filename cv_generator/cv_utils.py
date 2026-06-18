import os
import re
import yaml

def normalize_author_string(authors_str):
    s = authors_str.replace(" and ", ", ").replace(" & ", ", ")
    parts = [p.strip() for p in s.split(",") if p.strip()]
    normalized_authors = []
    is_last_first = any(len(p) <= 2 or (len(p) <= 3 and p.endswith('.')) for p in parts)
    if is_last_first:
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and (len(parts[i+1]) <= 3 or '.' in parts[i+1]):
                normalized_authors.append(f"{parts[i]}, {parts[i+1]}")
                i += 2
            else:
                normalized_authors.append(parts[i]); i += 1
    else:
        for p in parts:
            name_parts = p.split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]; first_initial = name_parts[0][0] + "."
                normalized_authors.append(f"{last_name}, {first_initial}")
            else: normalized_authors.append(p)
    if len(normalized_authors) > 2: return ", ".join(normalized_authors[:-1]) + ", and " + normalized_authors[-1]
    elif len(normalized_authors) == 2: return normalized_authors[0] + " and " + normalized_authors[1]
    elif len(normalized_authors) == 1: return normalized_authors[0]
    return authors_str

def format_date_string(date_str):
    if not isinstance(date_str, str): return date_str
    s = date_str.strip()
    if s.endswith('-'): return s + ' current'
    return s

def load_yaml(filename, base_dir):
    filepath = os.path.join(base_dir, "data", filename)
    if not os.path.exists(filepath): return []
    with open(filepath, 'r') as f: return yaml.safe_load(f) or []

def escape_latex(s):
    if not isinstance(s, str): return s
    replacements = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_'}
    for k, v in replacements.items(): s = s.replace(k, v)
    return s

def escape_dict(d):
    if isinstance(d, dict): return {k: escape_dict(v) for k, v in d.items()}
    elif isinstance(d, list): return [escape_dict(v) for v in d]
    else: return escape_latex(d)

RESEARCH_MISSION = "The high-level goal of my lab is to enable robots and learning systems to act and improve in real-time, directly within the dynamic, uncertain environments of the real world. We develop algorithms for fast optimization, planning, and control that allow systems to continuously update their behavior as they operate, tightly integrating perception, action, and learning so that robots can react quickly, gather the right information, and adapt their strategies on the fly. Our work is motivated by domains where real-time adaptability has meaningful societal impact: home and assistive robotics, where systems must operate safely alongside people; healthcare and robotic surgery, where precision and real-time feedback are essential; and disaster response, where robots must act under uncertainty with limited prior information."

CONTACT_INFO = {
    'name': "Daniel Rakita",
    'organization': "Yale University, Department of Computer Science",
    'address': "51 Prospect St, New Haven, CT 06511",
    'email': "daniel.rakita@yale.edu",
    'website': "https://dannyrakita.net",
    'lab_website': "https://apollo-lab-yale.github.io/",
    'google_scholar': "https://scholar.google.com/citations?user=1Y-cnCUAAAAJ&hl=en"
}
