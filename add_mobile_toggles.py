#!/usr/bin/env python3
"""
Script to add mobile toggle buttons to dashboard templates that don't have them
"""

import os
import re

# Templates that should have mobile toggle (dashboard-style pages)
DASHBOARD_TEMPLATES = [
    "customers.html",
    "loans.html", 
    "payments.html",
    "reports.html",
    "settings.html",
    "add_customer.html",
    "edit_customer.html",
    "new_loan.html"
]

MOBILE_TOGGLE_HTML = '''    <!-- Mobile Toggle -->
    <button class="mobile-toggle" id="mobileToggle" style="display: none;">
        <i class="fas fa-bars"></i>
    </button>'''

def add_mobile_toggle(file_path):
    """Add mobile toggle to a template if it doesn't have one"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if mobile toggle already exists
        if 'mobile-toggle' in content or 'mobileToggle' in content:
            print(f"⚪ Mobile toggle already exists: {os.path.basename(file_path)}")
            return False
        
        # Look for sidebar closing tag and add mobile toggle after it
        pattern = r'(</nav>\s*\n)'
        if '</nav>' in content and 'sidebar' in content:
            # Find the nav closing tag that comes after sidebar
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '</nav>' in line and i > 0:
                    # Check if previous lines contain sidebar
                    prev_content = '\n'.join(lines[max(0, i-20):i])
                    if 'sidebar' in prev_content:
                        # Insert mobile toggle after this nav
                        lines.insert(i + 1, '')
                        lines.insert(i + 2, MOBILE_TOGGLE_HTML)
                        content = '\n'.join(lines)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Added mobile toggle: {os.path.basename(file_path)}")
                        return True
                        break
        
        print(f"⚠️  Could not add mobile toggle: {os.path.basename(file_path)}")
        return False
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main function"""
    templates_dir = "templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Templates directory not found: {templates_dir}")
        return
    
    print("📱 Adding mobile toggle buttons to dashboard templates...\n")
    
    updated_count = 0
    for template in DASHBOARD_TEMPLATES:
        file_path = os.path.join(templates_dir, template)
        if os.path.exists(file_path):
            if add_mobile_toggle(file_path):
                updated_count += 1
        else:
            print(f"⚠️  Template not found: {template}")
    
    print(f"\n✅ Added mobile toggle to {updated_count} templates")

if __name__ == '__main__':
    main()
