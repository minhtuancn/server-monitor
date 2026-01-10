#!/usr/bin/env python3

"""
Batch fix broken internal links - skip node_modules and vendor directories
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Common file moves (old path -> new path)
FILE_MOVES = {
    'CUSTOM-DOMAIN-GUIDE.md': 'docs/operations/CUSTOM_DOMAIN.md',
    'HTTPS-SETUP.md': 'docs/security/HTTPS_SETUP.md',
    'TEST_GUIDE.md': 'docs/operations/TEST_GUIDE.md',
    'DEPLOYMENT.md': 'docs/operations/DEPLOYMENT.md',
    'UPGRADE_GUIDE.md': 'docs/operations/UPGRADE_ROLLBACK.md',
    'DOCKER.md': 'docs/getting-started/DOCKER.md',
    'ARCHITECTURE.md': 'docs/architecture/ARCHITECTURE.md',
    'SECURITY.md': 'docs/security/SECURITY.md',
    'ROADMAP.md': 'docs/product/ROADMAP.md',
    'TASKS.md': 'docs/product/TASKS.md',
    'CHANGELOG.md': 'docs/product/CHANGELOG.md',
}

SKIP_DIRS = {'node_modules', 'vendor', '.git', '__pycache__', 'htmlcov', '.next'}

def find_broken_links(directory):
    """Find all broken internal links in markdown files (excluding vendor dirs)"""
    broken_links = []
    
    for md_file in Path(directory).rglob("*.md"):
        # Skip vendor/archived dirs
        if any(skip_dir in str(md_file) for skip_dir in SKIP_DIRS) or 'archive' in str(md_file):
            continue
            
        with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        
        for link_text, link_url in links:
            # Skip external links, anchors, and absolute URLs
            if link_url.startswith(('http://', 'https://', '#', 'mailto:', '/')):
                continue
                
            # Resolve relative path
            try:
                link_path = (md_file.parent / link_url).resolve()
                # Handle anchor links
                if '#' in link_url:
                    link_path = (md_file.parent / link_url.split('#')[0]).resolve()
            except:
                link_path = None
            
            # Check if file exists
            if not link_path or not link_path.exists():
                broken_links.append({
                    'file': md_file,
                    'link': link_url,
                    'text': link_text,
                    'content': content
                })
    
    return broken_links

def fix_link(link_url):
    """Try to fix a broken link"""
    # Handle anchor links
    anchor = ''
    if '#' in link_url:
        link_url, anchor = link_url.split('#', 1)
        anchor = '#' + anchor
    
    # Remove leading ../
    clean_link = link_url.replace('../', '').replace('./', '').strip('/')
    
    # Check if it's in FILE_MOVES
    for old_name, new_path in FILE_MOVES.items():
        if clean_link.endswith(old_name) or clean_link == old_name:
            return new_path + anchor
    
    # Check if it's a file that exists in docs
    potential_paths = [
        f'docs/operations/{clean_link}',
        f'docs/security/{clean_link}',
        f'docs/getting-started/{clean_link}',
        f'docs/architecture/{clean_link}',
        f'docs/product/{clean_link}',
        f'docs/{clean_link}',
    ]
    
    for path in potential_paths:
        if Path(path).exists():
            return path + anchor
    
    return None

def apply_fixes(broken_links, dry_run=True):
    """Apply fixes to broken links"""
    fixes_by_file = defaultdict(list)
    
    # Group fixes by file
    for item in broken_links:
        fixed_link = fix_link(item['link'])
        if fixed_link:
            fixes_by_file[item['file']].append({
                'old': item['link'],
                'new': fixed_link,
                'text': item['text']
            })
    
    stats = {'files': 0, 'links': 0, 'failed': 0}
    
    for file_path, fixes in fixes_by_file.items():
        if not fixes:
            continue
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all fixes for this file
        for fix in fixes:
            # Build the old link pattern
            old_pattern = f']({fix["old"]})'
            new_pattern = f']({fix["new"]})'
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                stats['links'] += 1
                print(f"  ✓ {fix['old']} → {fix['new']}")
            else:
                stats['failed'] += 1
        
        # Write back if changed
        if content != original_content:
            stats['files'] += 1
            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated: {file_path}")
            else:
                print(f"📝 Would update: {file_path}")
    
    return stats

def main():
    import sys
    
    dry_run = '--apply' not in sys.argv
    
    print("🔍 Scanning for broken links (excluding node_modules)...")
    broken = find_broken_links('.')
    
    print(f"\n📊 Found {len(broken)} broken links in project files")
    
    if not broken:
        print("✅ No broken links found!")
        return
    
    # Try to fix
    print("\n🔧 Attempting to fix links...")
    stats = apply_fixes(broken, dry_run=dry_run)
    
    print(f"\n📈 Summary:")
    print(f"  Files to update: {stats['files']}")
    print(f"  Links fixed: {stats['links']}")
    print(f"  Failed: {stats['failed']}")
    print(f"  Unfixable: {len(broken) - stats['links'] - stats['failed']}")
    
    if dry_run:
        print("\n💡 Run with --apply to actually fix the links")
    else:
        print("\n✅ Links have been fixed!")

if __name__ == '__main__':
    main()
