#!/usr/bin/env python3
"""
i18n Integration Script
Automatically adds data-i18n attributes to HTML files
"""

import re
import json
from pathlib import Path

# Text patterns to translate with their i18n keys
TRANSLATIONS = {
    # Common
    r'\bSave\b': 'common.save',
    r'\bCancel\b': 'common.cancel',
    r'\bDelete\b': 'common.delete',
    r'\bEdit\b': 'common.edit',
    r'\bAdd\b': 'common.add',
    r'\bSearch\b': 'common.search',
    r'\bFilter\b': 'common.filter',
    r'\bActions\b': 'common.actions',
    r'\bStatus\b': 'common.status',
    r'\bRefresh\b': 'common.refresh',
    r'\bClose\b': 'common.close',
    r'\bConfirm\b': 'common.confirm',
    r'\bLoading\.\.\.\b': 'common.loading',
    r'\bNo data\b': 'common.noData',
    
    # Users
    r'\bUser Management\b': 'users.title',
    r'\bAdd User\b': 'users.addUser',
    r'\bEdit User\b': 'users.editUser',
    r'\bDelete User\b': 'users.deleteUser',
    r'\bUsername\b': 'users.username',
    r'\bEmail\b': 'users.email',
    r'\bRole\b': 'users.role',
    r'\bActive\b': 'users.active',
    r'\bInactive\b': 'users.inactive',
    r'\bLast Login\b': 'users.lastLogin',
    r'\bChange Password\b': 'users.changePassword',
    r'\bCurrent Password\b': 'users.currentPassword',
    r'\bNew Password\b': 'users.newPassword',
    r'\bConfirm Password\b': 'users.confirmPassword',
    
    # Settings
    r'\bSystem Settings\b': 'settings.title',
    r'\bGeneral\b': 'settings.general',
    r'\bAppearance\b': 'settings.appearance',
    r'\bNotifications\b': 'settings.notifications',
    r'\bSecurity\b': 'settings.security',
    r'\bTimezone\b': 'settings.timezone',
    r'\bDate Format\b': 'settings.dateFormat',
    r'\bTime Format\b': 'settings.timeFormat',
    r'\bLanguage\b': 'settings.language',
    r'\bTheme\b': 'settings.theme',
    
    # Dashboard
    r'\bDashboard\b': 'dashboard.title',
    r'\bOverview\b': 'dashboard.overview',
    r'\bServers\b': 'dashboard.servers',
    r'\bTotal Servers\b': 'dashboard.totalServers',
    r'\bOnline\b': 'dashboard.onlineServers',
    r'\bOffline\b': 'dashboard.offlineServers',
    r'\bCPU Usage\b': 'dashboard.cpuUsage',
    r'\bMemory Usage\b': 'dashboard.memoryUsage',
    r'\bDisk Usage\b': 'dashboard.diskUsage',
    
    # Auth
    r'\bLogin\b': 'auth.login',
    r'\bLogout\b': 'auth.logout',
    r'\bPassword\b': 'auth.password',
}

def add_i18n_to_file(filepath):
    """Add data-i18n attributes to HTML file"""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modifications = 0
    
    # Add data-i18n to buttons, labels, headers
    for pattern, key in TRANSLATIONS.items():
        # Match text in buttons
        button_pattern = r'(<button[^>]*>)\s*' + pattern + r'\s*(</button>)'
        if re.search(button_pattern, content):
            content = re.sub(
                button_pattern,
                r'\1<span data-i18n="' + key + r'">' + pattern.replace('\\b', '') + r'</span>\2',
                content
            )
            modifications += 1
        
        # Match text in labels
        label_pattern = r'(<label[^>]*>)\s*' + pattern + r'\s*(</label>)'
        if re.search(label_pattern, content):
            content = re.sub(
                label_pattern,
                r'\1<span data-i18n="' + key + r'">' + pattern.replace('\\b', '') + r'</span>\2',
                content
            )
            modifications += 1
        
        # Match text in headers
        for tag in ['h1', 'h2', 'h3', 'h4']:
            header_pattern = r'(<' + tag + r'[^>]*>)\s*' + pattern + r'\s*(</' + tag + r'>)'
            if re.search(header_pattern, content):
                content = re.sub(
                    header_pattern,
                    r'\1<span data-i18n="' + key + r'">' + pattern.replace('\\b', '') + r'</span>\2',
                    content
                )
                modifications += 1
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Added {modifications} i18n attributes to {filepath.name}")
    else:
        print(f"○ No changes needed for {filepath.name}")

def main():
    """Main function"""
    frontend_dir = Path(__file__).parent.parent
    html_files = [
        frontend_dir / 'users.html',
        frontend_dir / 'settings.html',
        frontend_dir / 'dashboard.html',
    ]
    
    print("Starting i18n integration...\n")
    
    for filepath in html_files:
        if filepath.exists():
            add_i18n_to_file(filepath)
        else:
            print(f"✗ File not found: {filepath}")
    
    print("\n✓ i18n integration complete!")
    print("\nNote: This script adds basic data-i18n attributes.")
    print("Manual review and adjustments may be needed for complex elements.")

if __name__ == '__main__':
    main()
