import jinja2
import os
import subprocess
import shutil
import re
import pypdf
from cv_utils import normalize_author_string, format_date_string, load_yaml, escape_dict, RESEARCH_MISSION

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
    target_pages = config.get('target_pages')
    curr = config.copy()
    iteration = 0
    max_iters = 12
    
    while iteration < max_iters:
        data = {
            'name': "Daniel Rakita", 'organization': "Yale University, Department of Computer Science",
            'address': "123 Main St, New Haven, CT 06520 USA", 'email': "daniel.rakita@yale.edu",
            'website': "https://dannyrakita.com", 'lab_website': "https://apollo-lab-yale.github.io/",
            'google_scholar': "https://scholar.google.com/citations?user=1Y-cnCUAAAAJ&hl=en",
            'research_interests': RESEARCH_MISSION if curr.get('show_mission', True) else "",
            'condensed': curr.get('condensed', True),
            'titles': {'awards': "Selected Honors & Awards", 'funding': "Selected Research Grants and Funding", 'publications': "Selected Publications", 'invited_talks': "Selected Invited Talks", 'teaching': "Selected Teaching", 'advising': "Selected Advising", 'service': r"Selected Service", 'media': "Selected Media"}
        }

        data['experience'] = escape_dict([dict(exp, dates=format_date_string(exp['dates'])) for exp in load_yaml("experience.yml", BASE_DIR)])
        data['education'] = escape_dict(load_yaml("education.yml", BASE_DIR))

        awards = load_yaml("awards.yml", BASE_DIR)
        data['awards'] = escape_dict(awards[:curr.get('max_awards', 10)])

        funding = [dict(fund, dates=format_date_string(fund['dates'])) for fund in load_yaml("funding.yml", BASE_DIR)]
        data['funding'] = escape_dict(funding[:curr.get('max_funding', 5)])

        pubs = load_yaml("publications.yml", BASE_DIR)
        filtered_pubs = []
        for p in pubs:
            if p.get('type') == 'Preprint': continue
            authors = normalize_author_string(p.get('authors', ''))
            authors = re.sub(r'Rakita, D\.?', r'\\textbf{Rakita, D.}', authors)
            p['authors'] = authors; p['salience'] = 100 if p.get('award') else 0
            filtered_pubs.append(p)
        
        filtered_pubs.sort(key=lambda x: (x.get('salience', 0), int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0), reverse=True)
        filtered_pubs = filtered_pubs[:curr.get('max_pubs', 10)]
        filtered_pubs.sort(key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0, reverse=True)

        pubs_by_type = {}
        for p in filtered_pubs:
            ptype = p.get('type', 'Other')
            if ptype not in pubs_by_type: pubs_by_type[ptype] = []
            y = p.get('year'); p['display_year'] = '' if (pubs_by_type[ptype] and pubs_by_type[ptype][-1].get('y') == y) else y
            p['y'] = y; pubs_by_type[ptype].append(p)
        data['publications_by_type'] = escape_dict(pubs_by_type)

        teaching = load_yaml("teaching.yml", BASE_DIR)
        data['teaching'] = escape_dict(teaching[:curr.get('max_teaching', 5)])

        advising = load_yaml("advising.yml", BASE_DIR)
        filtered_adv = []
        allowed = curr.get('advising_categories', ['Ph.D. Students', 'Masters Students'])
        for c in advising:
            if c['category'] not in allowed: continue
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
        data['advising'] = escape_dict(filtered_adv)

        service = load_yaml("service.yml", BASE_DIR)
        data['service'] = escape_dict(service[:curr.get('max_service', 5)])

        talks = load_yaml("talks.yml", BASE_DIR)
        data['talks'] = escape_dict(talks[:curr.get('max_talks', 5)])

        media = load_yaml("media.yml", BASE_DIR)
        data['media'] = escape_dict(media[:curr.get('max_media', 5)])

        data['skills'] = escape_dict(load_yaml("skills.yml", BASE_DIR)) if curr.get('show_skills', True) else []

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
        curr['max_pubs'] = max(0, curr.get('max_pubs', 10) - 2)
        curr['max_awards'] = max(0, curr.get('max_awards', 5) - 1)
        if iteration > 1: curr['show_mission'] = False
        if iteration > 2: curr['max_media'] = 0
        if iteration > 3: curr['max_talks'] = 0
        if iteration > 4: curr['max_service'] = 0
        if iteration > 5: curr['show_skills'] = False
        if iteration > 6: curr['max_teaching'] = 0
        if iteration > 7: curr['max_funding'] = 0
        if iteration > 8: curr['advising_categories'] = ['Ph.D. Students']

    final = os.path.join(BASE_DIR, "downloads", output_filename)
    if os.path.exists(pdf): shutil.copy2(pdf, final)
    print(f"Final {version_name}: {get_pdf_page_count(final)} pages.")

def main():
    # 4-Page Version
    generate_short_version("4-Page", "cv_4page.pdf", {'target_pages': 4, 'max_pubs': 20, 'max_awards': 10})
    # 1-Page Version
    generate_short_version("1-Page", "cv_1page.pdf", {'target_pages': 1, 'show_mission': False, 'max_pubs': 1, 'max_awards': 1, 'max_funding': 1, 'max_service': 0, 'max_talks': 0, 'max_teaching': 1, 'max_media': 0, 'show_skills': False})

if __name__ == "__main__":
    main()
