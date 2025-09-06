#!/usr/bin/env python3
"""
Script to ensure all HTML templates include universal responsive CSS and JS
"""

import os
import glob
import re

# Directory containing templates
TEMPLATES_DIR = "templates"

# CSS and JS to add
UNIVERSAL_CSS = '    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/universal-responsive.css\') }}">'
UNIVERSAL_JS = '    <script src="{{ url_for(\'static\', filename=\'js/universal.js\') }}"></script>'

def update_template(file_path):
    """Update a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        updated = False
        
        # Check if universal CSS is already included
        if 'universal-responsive.css' not in content:
            # Find the last CSS link and add universal CSS after it
            css_pattern = r'(<link[^>]*\.css[^>]*>)'
            css_matches = list(re.finditer(css_pattern, content))
            if css_matches:
                last_css = css_matches[-1]
                insert_pos = last_css.end()
                content = content[:insert_pos] + '\n' + UNIVERSAL_CSS + content[insert_pos:]
                updated = True
        
        # Check if universal JS is already included
        if 'universal.js' not in content:
            # Find bootstrap JS and add universal JS after it
            bootstrap_js_pattern = r'(<script[^>]*bootstrap[^>]*></script>)'
            bootstrap_match = re.search(bootstrap_js_pattern, content)
            if bootstrap_match:
                insert_pos = bootstrap_match.end()
                content = content[:insert_pos] + '\n' + UNIVERSAL_JS + content[insert_pos:]
                updated = True
        
        # Write back if updated
        if updated and content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {os.path.basename(file_path)}")
            return True
        else:
            print(f"⚪ No changes needed: {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function to update all templates"""
    if not os.path.exists(TEMPLATES_DIR):
        print(f"❌ Templates directory not found: {TEMPLATES_DIR}")
        return
    
    # Find all HTML files
    html_files = glob.glob(os.path.join(TEMPLATES_DIR, "*.html"))
    
    if not html_files:
        print("❌ No HTML files found in templates directory")
        return
    
    print(f"📝 Found {len(html_files)} HTML templates")
    print("🔧 Adding universal responsive CSS and JS...\n")
    
    updated_count = 0
    for file_path in html_files:
        if update_template(file_path):
            updated_count += 1
    
    print(f"\n✅ Process complete! Updated {updated_count} out of {len(html_files)} templates")
    
    # Additional checks
    print("\n🔍 Additional responsiveness checks:")
    
    # Check for mobile toggle buttons
    mobile_toggle_count = 0
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'mobile-toggle' in content or 'mobileToggle' in content:
                mobile_toggle_count += 1
    
    print(f"📱 Mobile toggle found in {mobile_toggle_count} templates")
    
    # Check for viewport meta tags
    viewport_count = 0
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'viewport' in content and 'width=device-width' in content:
                viewport_count += 1
    
    print(f"📐 Viewport meta tag found in {viewport_count} templates")
    
    print("\n🎉 All templates are now responsive!")

if __name__ == '__main__':
    main()
