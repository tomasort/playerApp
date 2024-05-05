from bs4 import BeautifulSoup

# Load the SVG file
with open('./app/templates/remote.svg', 'r') as file:
    svg_content = file.read()

# Create BeautifulSoup object
soup = BeautifulSoup(svg_content, 'xml')  # 'xml' parser is suitable for SVG

# Find all 'g' tags in the SVG
g_tags = soup.find_all('g')

# Function to find leaf nodes and add onclick attribute
def add_onclick_attr(tag):
    children = tag.find_all('g')
    if "KEY" in tag['id']:
        # This is a leaf node
        tag['onclick'] = f"remote('{tag['id']}')"
    else:
        for child in children:
            add_onclick_attr(child)

# Traverse the 'g' tags to find leaves and add onclick attribute
for g_tag in g_tags:
    add_onclick_attr(g_tag)

# Save the modified SVG to a new file
with open('./app/templates/output.svg', 'w') as output_file:
    output_file.write(str(soup))