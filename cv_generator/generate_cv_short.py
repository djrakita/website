import jinja2
import os
import subprocess
import shutil
import re
import pypdf
import yaml
from cv_utils import normalize_author_string, format_date_string, load_yaml, escape_dict, RESEARCH_MISSION, CONTACT_INFO

BASE_DIR = "/Users/dannyrakita/Documents/website/"
CV_GEN_DIR = os.path.join(BASE_DIR, "cv_generator")

def get_pdf_page_count(pdf_path):
    if not os.path.exists(pdf_path): return 999
    try:
        with open(pdf_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            return len(reader.pages)
    except: return 999 

def generate_short_version(version_name, output_filename, config):
    print(f"\n--- Generating {version_name} Version ---")
    target_pages = config.get('target_pages', 99)
    curr = config.copy()
    iteration = 0
    max_iters = 10
    
    # Pre-process enabled sections
    enabled = curr.get('sections_enabled', [])
    
    while iteration < max_iters:
        data = CONTACT_INFO.copy()
        data.update({
            'research_interests': RESEARCH_MISSION if curr.get('show_mission', True) else "",
            'condensed': curr.get('condensed', True),
            'titles': {'awards': "Selected Honors & Awards", 'funding': "Selected Research Grants and Funding", 'publications': "Selected Publications", 'invited_talks': "Selected Invited Talks", 'teaching': "Selected Teaching", 'advising': "Selected Advising", 'service': r"Selected Service", 'media': "Selected Media"}
        })

        # Experience & Education (Always include if not explicitly disabled)
        data['experience'] = escape_dict([dict(exp, dates=format_date_string(exp['dates'])) for exp in load_yaml("experience.yml", BASE_DIR)]) if 'experience' in enabled else []
        data['education'] = escape_dict(load_yaml("education.yml", BASE_DIR)) if 'education' in enabled else []

        # Awards
        awards = load_yaml("awards.yml", BASE_DIR)
        force_awards = curr.get('force_include', {}).get('awards', [])
        data['awards'] = escape_dict([a for a in awards if a['title'] in force_awards or awards.index(a) < curr.get('max_entries', {}).get('awards', 5)]) if 'awards' in enabled else []

        # Funding
        funding = [dict(fund, dates=format_date_string(fund['dates'])) for fund in load_yaml("funding.yml", BASE_DIR)]
        data['funding'] = escape_dict(funding[:curr.get('max_entries', {}).get('funding', 5)]) if 'funding' in enabled else []

        # Publications
        pubs = load_yaml("publications.yml", BASE_DIR)
        force_pubs = curr.get('force_include', {}).get('publications', [])
        filtered_pubs = []
        for p in pubs:
            if p.get('type') == 'Preprint': continue
            authors = normalize_author_string(p.get('authors', ''))
            authors = re.sub(r'Rakita, D\.?', r'\\textbf{Rakita, D.}', authors)
            p['authors'] = authors
            # Logic: check if explicitly tagged in data, or in force_include list, or has award
            is_forced = p.get('title') in force_pubs or p.get('version') == version_name or (isinstance(p.get('version'), list) and version_name in p['version'])
            p['salience'] = 1000 if is_forced else (100 if p.get('award') else 0)
            filtered_pubs.append(p)
        
        # Sort by salience then year
        filtered_pubs.sort(key=lambda x: (x.get('salience', 0), int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0), reverse=True)
        filtered_pubs = filtered_pubs[:curr.get('max_entries', {}).get('publications', 10)]
        filtered_pubs.sort(key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0, reverse=True)

        pubs_by_type = {}
        for p in filtered_pubs:
            ptype = p.get('type', 'Other')
            if ptype not in pubs_by_type: pubs_by_type[ptype] = []
            y = p.get('year'); p['display_year'] = '' if (pubs_by_type[ptype] and pubs_by_type[ptype][-1].get('y') == y) else y
            p['y'] = y; pubs_by_type[ptype].append(p)
        data['publications_by_type'] = escape_dict(pubs_by_type) if 'publications' in enabled else {}

        # Teaching
        teaching = load_yaml("teaching.yml", BASE_DIR)
        data['teaching'] = escape_dict(teaching[:curr.get('max_entries', {}).get('teaching', 5)]) if 'teaching' in enabled else []

        # Advising
        advising = load_yaml("advising.yml", BASE_DIR)
        filtered_adv = []
        allowed_cats = curr.get('advising_categories', ['Ph.D. Students'])
        for c in advising:
            if c['category'] not in allowed_cats: continue
            if c['category'] == 'Undergraduate Students':
                names = sorted([s['name'] for s in c.get('students', [])], key=lambda x: x.split()[-1])
                c['is_inline'] = True; c['inline_text'] = "\\textit{Undergraduate advisees: } " + ", ".join(names)
            else:
                c['is_inline'] = False
                for i, s in enumerate(c.get('students', [])):
                    d = format_date_string(s.get('dates', ''))
                    s['display_dates'] = '' if (i > 0 and c['students'][i-1].get('d') == d) else d
                    s['d'] = d
            filtered_adv.append(c)
        data['advising'] = escape_dict(filtered_adv) if 'advising' in enabled else []

        # Simple sections
        data['service'] = escape_dict(load_yaml("service.yml", BASE_DIR)[:curr.get('max_entries', {}).get('service', 5)]) if 'service' in enabled else []
        data['talks'] = escape_dict(load_yaml("talks.yml", BASE_DIR)[:curr.get('max_entries', {}).get('talks', 5)]) if 'talks' in enabled else []
        data['media'] = escape_dict(load_yaml("media.yml", BASE_DIR)[:curr.get('max_entries', {}).get('media', 5)]) if 'media' in enabled else []
        data['skills'] = escape_dict(load_yaml("skills.yml", BASE_DIR)) if curr.get('show_skills', True) else []

        # Render
        env = jinja2.Environment(block_start_string='<%', block_end_string='%>', variable_start_string='<<', variable_end_string='>>', trim_blocks=True, autoescape=False, loader=jinja2.FileSystemLoader(CV_GEN_DIR))
        template = env.get_template("template.tex")
        rendered = template.render(data)
        
        job = f"cv_{version_name.lower().replace(' ', '_')}"
        with open(os.path.join(CV_GEN_DIR, f"{job}.tex"), "w") as f: f.write(rendered)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-jobname={job}", f"{job}.tex"], cwd=CV_GEN_DIR, capture_output=True)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-jobname={job}", f"{job}.tex"], cwd=CV_GEN_DIR, capture_output=True)
        
        pdf = os.path.join(CV_GEN_DIR, f"{job}.pdf")
        count = get_pdf_page_count(pdf)
        print(f"Iter {iteration}: {count} pages (Target: {target_pages}).")
        if count <= target_pages: break
        
        iteration += 1
        # Iteratively prune max_entries if still over
        for k in curr['max_entries']:
            if curr['max_entries'][k] > 0: curr['max_entries'][k] -= 1
        if iteration > 1: curr['show_mission'] = False

    final = os.path.join(BASE_DIR, "downloads", output_filename)
    if os.path.exists(pdf): shutil.copy2(pdf, final)
    print(f"Final {version_name}: {get_pdf_page_count(final)} pages.")

def main():
    config_path = os.path.join(CV_GEN_DIR, "cv_config.yml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    versions = config.get('versions', {})
    if "4-Page" in versions:
        generate_short_version("4-Page", "cv_4page.pdf", versions["4-Page"])
    if "1-Page" in versions:
        generate_short_version("1-Page", "cv_1page.pdf", versions["1-Page"])

if __name__ == "__main__":
    main()
