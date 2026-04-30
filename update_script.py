import re

with open('script.js', 'r') as f:
    content = f.read()

# Update Publications Fetch
pub_replace = """        fetch('publications.yml')
            .then(response => response.text())
            .then(text => jsyaml.load(text))
            .then(data => {
                pubContainer.innerHTML = ''; // Clear loading message

                // Group by type (Apollo lab format uses 'type')
                const groupedData = {};
                data.forEach(item => {
                    if (!item.type) return;
                    let catName = item.type === 'Journal' ? 'Journal Articles' : 
                                 (item.type === 'Conference' ? 'Conference Papers' : item.type + 's');
                    if (!groupedData[catName]) {
                        groupedData[catName] = [];
                    }
                    groupedData[catName].push(item);
                });

                const categories = Object.keys(groupedData).map(cat => ({
                    category: cat,
                    items: groupedData[cat]
                }));

                categories.forEach(category => {"""

content = re.sub(
    r"        fetch\('publications\.json'\)\s*\n\s*\.then\(response => response\.json\(\)\)\s*\n\s*\.then\(data => \{\s*\n\s*pubContainer\.innerHTML = ''; // Clear loading message\s*\n\s*data\.forEach\(category => \{",
    pub_replace,
    content
)

# Update Publications Render
# The item structure from Apollo Lab format doesn't have an `id` field.
# Old format: <span>[${item.id}] ${item.authors} ${item.year}. ${item.title} <em>${item.venue}</em>.</span>
# New format: <span>${item.authors} (${item.year}). ${item.title} <em>${item.venue ? item.venue : ''}</em>.</span>

content = content.replace(
    "<span>[${item.id}] ${item.authors} ${item.year}. ${item.title} <em>${item.venue}</em>.</span>",
    "<span>${item.authors} (${item.year}). ${item.title} <em>${item.venue ? item.venue : ''}</em>.</span>"
)

# Also update pdf link logic. New format uses `link` instead of `pdf`
content = content.replace(
    "const pdfLink = item.pdf ? `",
    "const pdfLink = item.link ? `"
).replace(
    "<a href=\"${item.pdf}\"",
    "<a href=\"${item.link}\""
)


# Update News Fetch
news_replace = """        fetch('news.yml')
            .then(response => response.text())
            .then(text => jsyaml.load(text))
            .then(data => {"""

content = re.sub(
    r"        fetch\('news\.json'\)\s*\n\s*\.then\(response => response\.json\(\)\)\s*\n\s*\.then\(data => \{",
    news_replace,
    content
)

with open('script.js', 'w') as f:
    f.write(content)

