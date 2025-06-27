"""
Script untuk menghapus semua emoji dari main.py
"""

import re

def remove_emojis_from_main():
    """Remove all emojis from main.py"""
    
    # Read the file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace emojis with ASCII equivalents
    replacements = [
        ('❌', '[ERROR]'),
        ('✅', '[SUCCESS]'),
        ('⚠️', '[WARN]'),
        ('📊', '[INFO]'),
        ('💡', '[INFO]'),
        ('🚀', '[INFO]'),
        ('⏹️', '[STOP]'),
        ('🎯', '[TARGET]'),
        ('🔧', '[TOOL]'),
        ('📈', '[CHART]'),
        ('📉', '[CHART]'),
        ('📋', '[LIST]'),
        ('⏰', '[TIME]'),
        ('🎥', '[VIDEO]'),
        ('🖼️', '[IMAGE]'),
        ('💾', '[SAVE]'),
        ('🔍', '[SEARCH]'),
        ('⚡', '[FAST]'),
        ('🔥', '[HOT]'),
        ('❄️', '[COLD]'),
        ('🌟', '[STAR]'),
        ('🎉', '[PARTY]'),
        ('✨', '[SPARKLE]'),
        ('🚧', '[WORK]'),
        ('🔨', '[HAMMER]'),
        ('🛠️', '[TOOLS]'),
        ('📝', '[NOTE]'),
        ('📄', '[DOCS]'),
        ('📁', '[FOLDER]'),
        ('📂', '[OPEN-FOLDER]'),
        ('🗂️', '[TABS]'),
        ('🗃️', '[FILES]'),
        ('🗄️', '[CABINET]'),
        ('📚', '[BOOKS]'),
        ('📖', '[BOOK]'),
        ('📰', '[NEWS]'),
        ('🔖', '[BOOKMARK]'),
        ('🏷️', '[TAG]'),
        ('💼', '[BRIEFCASE]'),
        ('📊', '[CHART]'),
        ('📈', '[UP-CHART]'),
        ('📉', '[DOWN-CHART]'),
        ('📇', '[CARD]'),
        ('📋', '[CLIPBOARD]'),
        ('📌', '[PIN]'),
        ('📍', '[LOCATION]'),
        ('📎', '[CLIP]'),
        ('🖇️', '[CLIPS]'),
        ('📐', '[RULER]'),
        ('📏', '[RULER]'),
        ('🖊️', '[PEN]'),
        ('🖋️', '[PEN]'),
        ('✏️', '[PENCIL]'),
        ('🖍️', '[CRAYON]'),
        ('🖌️', '[BRUSH]'),
        ('🔍', '[SEARCH]'),
        ('🔎', '[SEARCH]')
    ]
    
    # Apply replacements
    original_content = content
    for emoji, replacement in replacements:
        content = content.replace(emoji, replacement)
    
    # Write back to file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Report changes
    changes_made = original_content != content
    if changes_made:
        print("[SUCCESS] Emojis removed from main.py")
        print(f"[INFO] File updated with ASCII-safe replacements")
        
        # Count changes
        change_count = 0
        for emoji, replacement in replacements:
            count = original_content.count(emoji)
            if count > 0:
                change_count += count
                print(f"  - {emoji} → {replacement} ({count} occurrences)")
        
        print(f"[INFO] Total changes: {change_count}")
    else:
        print("[INFO] No emojis found in main.py")

if __name__ == "__main__":
    remove_emojis_from_main()
