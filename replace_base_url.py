#!/usr/bin/env python3
"""
Script to Replace All localhost:8000 with Environment Variable
===============================================================
This script replaces all hardcoded http://localhost:8000 URLs 
with the API_BASE_URL variable from .env in frontend code
"""

import os
import re
from pathlib import Path

def find_jsx_js_files(directory):
    """Find all .js and .jsx files"""
    files = []
    for ext in ['*.js', '*.jsx', '*.ts', '*.tsx']:
        files.extend(Path(directory).rglob(ext))
    return files

def replace_in_file(filepath, replacements):
    """Replace text in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes_made = True
        
        if changes_made:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"  ✗ Error processing {filepath}: {e}")
        return False

def add_import_if_needed(filepath):
    """Add API import if not present"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file uses axios or fetch with localhost
        has_api_call = 'axios' in content or 'fetch(' in content
        has_localhost = 'localhost:8000' in content or 'http://localhost:8000' in content
        has_import = "from '../utils/api'" in content or "from './utils/api'" in content
        
        if has_api_call and has_localhost and not has_import:
            # Add import at the top after other imports
            import_line = "import apiClient, { API_BASE_URL } from '../utils/api';\n"
            
            # Find the last import statement
            import_pattern = r'(import .+;)\n'
            imports = list(re.finditer(import_pattern, content))
            
            if imports:
                last_import = imports[-1]
                content = content[:last_import.end()] + import_line + content[last_import.end():]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
        
        return False
    except Exception as e:
        print(f"  ✗ Error adding import to {filepath}: {e}")
        return False

def main():
    """Main function"""
    print("="*70)
    print("REPLACE LOCALHOST:8000 WITH BASE_URL")
    print("="*70)
    print()
    
    frontend_dir = "../fuel_frontend/src"
    
    if not os.path.exists(frontend_dir):
        print(f"✗ Frontend directory '{frontend_dir}' not found")
        print("  Run this script from the frontend root directory")
        return
    
    print(f"📁 Scanning {frontend_dir} for files...")
    files = find_jsx_js_files(frontend_dir)
    print(f"   Found {len(files)} files")
    print()
    
    # Replacements to make
    replacements = [
        # Replace full URLs
        ('http://localhost:8000', '${API_BASE_URL}'),
        ("'http://localhost:8000'", 'API_BASE_URL'),
        ('"http://localhost:8000"', 'API_BASE_URL'),
        ('`http://localhost:8000`', '${API_BASE_URL}'),
        
        # Replace URL concatenations
        ("'http://localhost:8000' + ", 'API_BASE_URL + '),
        ('"http://localhost:8000" + ', 'API_BASE_URL + '),
    ]
    
    updated_files = []
    import_added = []
    
    print("🔧 Processing files...")
    for filepath in files:
        # Skip node_modules
        if 'node_modules' in str(filepath):
            continue
        
        # Replace URLs
        if replace_in_file(filepath, replacements):
            updated_files.append(filepath)
            print(f"  ✓ Updated: {filepath}")
        
        # Add import if needed
        if add_import_if_needed(filepath):
            import_added.append(filepath)
            print(f"  ✓ Added import: {filepath}")
    
    print()
    print("="*70)
    print("✅ REPLACEMENT COMPLETE!")
    print("="*70)
    print()
    print(f"📊 Summary:")
    print(f"   Files scanned: {len(files)}")
    print(f"   Files updated: {len(updated_files)}")
    print(f"   Imports added: {len(import_added)}")
    print()
    
    if updated_files:
        print("📝 Updated files:")
        for f in updated_files[:10]:  # Show first 10
            print(f"   - {f}")
        if len(updated_files) > 10:
            print(f"   ... and {len(updated_files) - 10} more")
        print()
    
    print("✅ Next steps:")
    print("   1. Review changes in your files")
    print("   2. Make sure .env has REACT_APP_API_BASE_URL=http://localhost:8000")
    print("   3. Restart your development server")
    print()
    print("💡 Tip: Check src/utils/api.js for the API configuration")
    print("="*70)

if __name__ == "__main__":
    main()