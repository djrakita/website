import jinja2
import os
import subprocess
import re
import yaml
from cv_utils import normalize_author_string, format_date_string, load_yaml, escape_dict, CONTACT_INFO

BASE_DIR = "/Users/dannyrakita/Documents/website/"
CV_GEN_DIR = os.path.join(BASE_DIR, "cv_generator")

def generate_grant_cv():
    print("\n--- Generating Grant Proposal CV ---")
    
    data = CONTACT_INFO.copy()
    data.update({
        'header_right': "One-page Curriculum Vitae -- May 2026",
        'condensed': True,
        'titles': {
            'awards': "Awards (selected)",
            'funding': "Selected Research Grants and Funding",
            'publications': "Publications (selected)",
            'experience': "Appointments (selected)",
            'education': "Education (selected)",
            'invited_talks': "Selected Invited Talks",
            'teaching': "Selected Teaching",
            'advising': "Selected Advising",
            'service': "Selected Service",
            'media': "Selected Media"
        }
    })

    # Appointments (Selected)
    experience = load_yaml("experience.yml", BASE_DIR)
    # Filter out NREIP
    filtered_exp = [exp for exp in experience if "NREIP" not in exp.get('title', '')]
    data['experience'] = escape_dict([dict(exp, dates=format_date_string(exp['dates'])) for exp in filtered_exp])

    # Education (Selected)
    education = load_yaml("education.yml", BASE_DIR)
    # Filter out undergrad and bachelor
    filtered_edu = [edu for edu in education if "Undergraduate" not in edu.get('degree', '') and "Bachelor" not in edu.get('degree', '')]
    data['education'] = escape_dict(filtered_edu)

    # Publications (Selected)
    requested_titles = [
        "Subsecond 3D Mesh Generation for Robot Manipulation",
        "Hybrid Diffusion Policies with Projective Geometric Algebra for Efficient Robot Manipulation Learning",
        "Coherence-based Approximate Derivatives via Web of Affine Spaces Optimization",
        "PROXIMA: An Approach for Time or Accuracy Budgeted Collision Proximity Queries",
        "CollisionIK: A Per-Instant Pose Optimization Method for Generating Robot Motions",
        "RelaxedIK: Real-time Synthesis of Accurate and Feasible Robot Arm Motion"
    ]
    
    pubs = load_yaml("publications.yml", BASE_DIR)
    selected_pubs = []
    
    # We want to maintain the order provided in the request if possible, 
    # but the template groups by type. Let's see.
    # Actually, let's just find them and group them by type as the template expects.
    
    for title in requested_titles:
        found = False
        for p in pubs:
            if p['title'].strip().lower() == title.strip().lower():
                # Process authors
                authors = normalize_author_string(p.get('authors', ''))
                authors = re.sub(r'Rakita, D\.?', r'\\textbf{Rakita, D.}', authors)
                p['authors'] = authors
                selected_pubs.append(p)
                found = True
                break
        if not found:
            print(f"Warning: Could not find publication: {title}")

    # Group by type for the template
    pubs_by_type = {}
    for p in selected_pubs:
        ptype = p.get('type', 'Conference') # Default to Conference if not specified
        if ptype not in pubs_by_type:
            pubs_by_type[ptype] = []
        
        # Display year logic
        y = p.get('year')
        p['display_year'] = y # For selected version, maybe just show the year for all?
        # The template uses display_year to avoid repeating years.
        # Let's keep it consistent.
        p['y'] = y
        pubs_by_type[ptype].append(p)

    # Post-process display_year for each group
    for ptype in pubs_by_type:
        # Sort by year descending within type
        pubs_by_type[ptype].sort(key=lambda x: int(x.get('year', 0)) if str(x.get('year', '')).isdigit() else 0, reverse=True)
        for i, p in enumerate(pubs_by_type[ptype]):
            if i > 0 and pubs_by_type[ptype][i-1].get('y') == p.get('y'):
                p['display_year'] = ''
            else:
                p['display_year'] = p.get('y')

    data['publications_by_type'] = escape_dict(pubs_by_type)

    # Awards (Selected)
    awards = load_yaml("awards.yml", BASE_DIR)
    selected_awards_titles = ["Cisco", "Microsoft", "Best Paper Award Winner"]
    filtered_awards = []
    for a in awards:
        if any(term in a.get('title', '') for term in selected_awards_titles):
            filtered_awards.append(a)
    data['awards'] = escape_dict(filtered_awards)

    # Disable other sections to ensure 1-page
    data['funding'] = []
    data['teaching'] = []
    data['advising'] = []
    data['service'] = []
    data['media'] = []
    data['skills'] = []
    data['research_interests'] = ""

    # Render
    env = jinja2.Environment(
        block_start_string='<%', block_end_string='%>',
        variable_start_string='<<', variable_end_string='>>',
        trim_blocks=True, autoescape=False,
        loader=jinja2.FileSystemLoader(CV_GEN_DIR)
    )
    template = env.get_template("template.tex")
    rendered = template.render(data)
    
    job = "cv_1-page"
    tex_path = os.path.join(CV_GEN_DIR, f"{job}.tex")
    with open(tex_path, "w") as f:
        f.write(rendered)
    
    print(f"Compiling {job}.tex...")
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-jobname={job}", f"{job}.tex"], cwd=CV_GEN_DIR, capture_output=True)
    # Run twice for longtable/hyperlinks
    subprocess.run(["pdflatex", "-interaction=nonstopmode", f"-jobname={job}", f"{job}.tex"], cwd=CV_GEN_DIR, capture_output=True)
    
    pdf_path = os.path.join(CV_GEN_DIR, f"{job}.pdf")
    if os.path.exists(pdf_path):
        print(f"Successfully generated {pdf_path}")
    else:
        print(f"Error: Failed to generate {pdf_path}")

if __name__ == "__main__":
    generate_grant_cv()
