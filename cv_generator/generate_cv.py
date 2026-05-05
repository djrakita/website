import jinja2
import os
import subprocess
import shutil
import re
from cv_utils import normalize_author_string, format_date_string, load_yaml, escape_dict, RESEARCH_MISSION

BASE_DIR = "/Users/dannyrakita/Documents/website/"
CV_GEN_DIR = os.path.join(BASE_DIR, "cv_generator")

def main():
    print("\n--- Generating Full CV Version ---")
    
    # Core Data
    data = {
        'name': "Daniel Rakita",
        'organization': "Yale University, Department of Computer Science",
        'address': "123 Main St, New Haven, CT 06520 USA",
        'email': "daniel.rakita@yale.edu",
        'website': "https://dannyrakita.com",
        'lab_website': "https://apollo-lab-yale.github.io/",
        'google_scholar': "https://scholar.google.com/citations?user=1Y-cnCUAAAAJ&hl=en",
        'research_interests': RESEARCH_MISSION,
        'condensed': False,
        'titles': {
            'awards': "Honors & Awards",
            'funding': "Research Grants and Funding",
            'publications': "Publications",
            'invited_talks': "Selected Invited Talks",
            'teaching': "Teaching & Curriculum Development",
            'advising': "Advising & Student Mentoring",
            'service': r"Service \& Leadership",
            'media': "Selected Media Coverage"
        }
    }

    # Load and process data
    data['experience'] = escape_dict([dict(exp, dates=format_date_string(exp['dates'])) for exp in load_yaml("experience.yml", BASE_DIR)])
    data['education'] = escape_dict(load_yaml("education.yml", BASE_DIR))
    data['awards'] = escape_dict(load_yaml("awards.yml", BASE_DIR))
    data['funding'] = escape_dict([dict(fund, dates=format_date_string(fund['dates'])) for fund in load_yaml("funding.yml", BASE_DIR)])

    pubs = load_yaml("publications.yml", BASE_DIR)
    pubs_by_type = {}
    for p in pubs:
        if p.get('type') == 'Preprint': continue
        authors = normalize_author_string(p.get('authors', ''))
        authors = re.sub(r'Rakita, D\.?', r'\\textbf{Rakita, D.}', authors)
        p['authors'] = authors
        
        ptype = p.get('type', 'Other')
        if ptype not in pubs_by_type: pubs_by_type[ptype] = []
        y = p.get('year')
        p['display_year'] = '' if (pubs_by_type[ptype] and pubs_by_type[ptype][-1].get('year') == y) else y
        pubs_by_type[ptype].append(p)
    data['publications_by_type'] = escape_dict(pubs_by_type)

    data['teaching'] = escape_dict(load_yaml("teaching.yml", BASE_DIR))
    
    advising = load_yaml("advising.yml", BASE_DIR)
    for c in advising:
        if c['category'] == 'Undergraduate Students':
            names = sorted([s['name'] for s in c.get('students', [])], key=lambda x: x.split()[-1])
            c['is_inline'] = True
            c['inline_text'] = "\\textit{Current and past undergraduate advisees: } " + ", ".join(names)
        else:
            c['is_inline'] = False
            for i, s in enumerate(c.get('students', [])):
                d = format_date_string(s.get('dates', ''))
                s['display_dates'] = '' if (i > 0 and c['students'][i-1].get('dates') == d) else d
    data['advising'] = escape_dict(advising)

    data['service'] = escape_dict(load_yaml("service.yml", BASE_DIR))
    data['talks'] = escape_dict(load_yaml("talks.yml", BASE_DIR))
    data['media'] = escape_dict(load_yaml("media.yml", BASE_DIR))
    data['skills'] = escape_dict(load_yaml("skills.yml", BASE_DIR))

    # Render
    env = jinja2.Environment(block_start_string='<%', block_end_string='%>', variable_start_string='<<', variable_end_string='>>', trim_blocks=True, autoescape=False, loader=jinja2.FileSystemLoader(CV_GEN_DIR))
    template = env.get_template("template.tex")
    rendered = template.render(data)
    
    with open(os.path.join(CV_GEN_DIR, "cv_full.tex"), "w") as f: f.write(rendered)
    
    # Compile
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname=cv_full", "cv_full.tex"], cwd=CV_GEN_DIR, capture_output=True)
    subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname=cv_full", "cv_full.tex"], cwd=CV_GEN_DIR, capture_output=True)
    
    # Move to downloads
    final_pdf = os.path.join(BASE_DIR, "downloads", "Rakita CV.pdf")
    shutil.copy2(os.path.join(CV_GEN_DIR, "cv_full.pdf"), final_pdf)
    print(f"Full CV saved to {final_pdf}")

    # Snapshot
    img_out = os.path.join(BASE_DIR, "imgs", "cv_image.png")
    subprocess.run(["gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=png16m", "-r150", "-dFirstPage=1", "-dLastPage=1", f"-sOutputFile={img_out}", final_pdf], capture_output=True)
    print(f"Snapshot saved to {img_out}")

if __name__ == "__main__":
    main()
