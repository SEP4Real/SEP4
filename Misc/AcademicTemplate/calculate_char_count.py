#!/usr/bin/env python3
import sys
import re
import os

def calculate_characters(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 1. Strip Markdown/HTML Comments (<!-- comment -->)
    # These are not visible in the final compiled document.
    comment_pattern = re.compile(r'<!--.*?-->', re.DOTALL)
    content = comment_pattern.sub('', content)
        
    # 2. Strip YAML Frontmatter
    yaml_pattern = re.compile(r'^---\r?\n(.*?)\r?\n---\r?\n', re.DOTALL)
    yaml_match = yaml_pattern.match(content)
    if yaml_match:
        content = content[yaml_match.end():]
        
    # 3. Exclude References, Bibliography, Sources, and Appendices
    # Look for headers like "# References", "# Bibliography", "# Appendix" (case-insensitive)
    exclude_pattern = re.compile(r'^\s*#+\s+(?:appendix|references|bibliography|sources|8\.\s+references)', re.IGNORECASE | re.MULTILINE)
    split_parts = exclude_pattern.split(content)
    main_content = split_parts[0]
    
    # 4. Count Figures (Markdown images and HTML img tags)
    md_img_pattern = re.compile(r'!\[.*?\]\(.*?\)')
    html_img_pattern = re.compile(r'<img\s+[^>]*>')
    
    md_imgs = md_img_pattern.findall(main_content)
    html_imgs = html_img_pattern.findall(main_content)
    total_figures = len(md_imgs) + len(html_imgs)
    
    # Remove image syntaxes from text count to avoid counting paths and alt text
    clean_content = md_img_pattern.sub('', main_content)
    clean_content = html_img_pattern.sub('', clean_content)
    
    # 5. Count Characters (including spaces, newlines, etc.)
    text_char_count = len(clean_content)
    
    # 6. Add 800 characters per figure (according to guidelines)
    figure_allowance = total_figures * 800
    total_char_count = text_char_count + figure_allowance
    
    # Format count with thousands separator and return simple text
    formatted_total = f"{total_char_count:,}"
    return f"{formatted_total} characters"

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: calculate_char_count.py <path_to_markdown_file>", file=sys.stderr)
        sys.exit(1)
        
    filepath = sys.argv[1]
    result = calculate_characters(filepath)
    print(result)
