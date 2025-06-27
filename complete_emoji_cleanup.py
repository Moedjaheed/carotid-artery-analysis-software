#!/usr/bin/env python3
"""
Complete Emoji Cleanup Script for All Files
Removes Unicode emojis and replaces them with ASCII-safe alternatives
"""

import os
import re

def clean_file(file_path):
    """Clean emojis from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Define emoji replacements
        emoji_replacements = [
            ('❌', '[ERROR]'),
            ('✅', '[SUCCESS]'),
            ('⚠️', '[WARN]'),
            ('📊', '[INFO]'),
            ('💡', '[INFO]'),
            ('🚀', '[START]'),
            ('⏹️', '[STOP]'),
            ('🎯', '[TARGET]'),
            ('🔧', '[TOOL]'),
            ('📈', '[CHART]'),
            ('📉', '[CHART]'),
            ('📋', '[LIST]'),
            ('🔍', '[SEARCH]'),
            ('🎉', '[PARTY]'),
            ('✨', '[NEW]'),
            ('ℹ️', '[INFO]'),
            ('🖼️', '[IMAGE]'),
            ('🔥', '[HOT]'),
            ('❄️', '[COLD]'),
            ('🌟', '[STAR]'),
            ('🛠️', '[TOOLS]'),
            ('📝', '[NOTE]'),
            ('📄', '[DOCS]'),
            ('🗂️', '[TABS]'),
            ('🗃️', '[FILES]'),
            ('🗄️', '[CABINET]'),
            ('🏷️', '[TAG]'),
            ('📌', '[PIN]'),
            ('📍', '[LOCATION]'),
            ('🖇️', '[CLIPS]'),
            ('🖊️', '[PEN]'),
            ('🖋️', '[PEN]'),
            ('✏️', '[PENCIL]'),
            ('🖍️', '[CRAYON]'),
            ('🖌️', '[BRUSH]'),
        ]
        
        # Apply replacements
        for emoji, replacement in emoji_replacements:
            content = content.replace(emoji, replacement)
        
        # Check if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[SUCCESS] Cleaned emojis from: {file_path}")
            return True
        else:
            print(f"[INFO] No emojis found in: {file_path}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")
        return False

def main():
    """Clean emojis from all relevant Python files"""
    print("[INFO] Starting complete emoji cleanup...")
    
    # Files to clean
    files_to_clean = [
        'main.py',
        'enhanced_inference_gui.py',
        'launcher_enhanced_fixed.py',
        'video_inference.py',
        'data_viewer.py',
        'advanced_analytics.py',
        'frame_comparison_viewer.py',
        'elasticity_calculator.py',
        'data_sync.py',
        'batch_processor.py',
        'training_model.py',
        'theme_manager.py',
        'config.py'
    ]
    
    cleaned_count = 0
    
    for filename in files_to_clean:
        if os.path.exists(filename):
            if clean_file(filename):
                cleaned_count += 1
        else:
            print(f"[WARN] File not found: {filename}")
    
    print(f"\n[SUCCESS] Cleanup completed! {cleaned_count} files were cleaned.")
    print("[INFO] All files should now be free of Unicode encoding issues.")

if __name__ == "__main__":
    main()
