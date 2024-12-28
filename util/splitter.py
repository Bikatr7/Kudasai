import regex
import os

def sanitize_filename(title, max_length=50):
    """Create a safe filename from chapter title."""
    title = title.replace('〇', '').strip()
    
    ## Keep only alphanumeric chars, spaces, and safe punctuation
    safe_chars = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-'))
    
    ## Replace multiple spaces with single underscore
    safe_chars = regex.sub(r'\s+', '_', safe_chars)
    
    return safe_chars[:max_length].rstrip('_')

def is_chapter_marker(line):
    """Check if a line is a true chapter marker by looking for 〇 followed by text."""
    ## Match 〇 followed by whitespace and then English or Japanese text
    pattern = r'^〇\s*[A-Za-z\p{Han}\p{Hiragana}\p{Katakana}]'
    return bool(regex.match(pattern, line))

def get_raw_chapters(preprocessed_file):
    """Extract chapter titles from preprocessed text before first 〇 marker."""
    chapters = []
    with open(preprocessed_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if(line.startswith('〇')):
                break
            if(line and not line.lower() == 'toc'):
                chapters.append(line)
    return chapters

def split_chapters(preprocessed_file, translated_file, output_dir='chapters'):
    """Split text file into chapters based on 〇 markers."""
    os.makedirs(output_dir, exist_ok=True)
    
    raw_chapters = get_raw_chapters(preprocessed_file)
    
    current_chapter = []
    chapter_num = 1
    chapter_names = []
    
    with open(translated_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        if(is_chapter_marker(line)):
            if(current_chapter):
                chapter_title = current_chapter[0]
                filename = f"{chapter_num:02d}_{sanitize_filename(chapter_title)}.txt"
                chapter_names.append(f"{chapter_num:02d}. {chapter_title.strip()}")
                
                with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                    f.writelines(current_chapter)
                chapter_num += 1
            
            ## Start new chapter
            current_chapter = [line]
        else:
            if(current_chapter):
                current_chapter.append(line)
    
    ## Save final chapter
    if(current_chapter):
        chapter_title = current_chapter[0]
        filename = f"{chapter_num:02d}_{sanitize_filename(chapter_title)}.txt"
        chapter_names.append(f"{chapter_num:02d}. {chapter_title.strip()}")
        
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.writelines(current_chapter)
    
    ## Write chapter info to a file
    with open(os.path.join(output_dir, 'chapter_list.txt'), 'w', encoding='utf-8') as f:
        f.write("EXPERIMENTAL CHAPTER SPLIT - Please report any perceived issues to your translation head\n\n")
        f.write("Raw chapters detected from preprocessed text:\n")
        f.write("\n".join(raw_chapters))
        f.write("\n\nChapters split from translated text:\n")
        f.write('\n'.join(chapter_names))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python splitter.py <preprocessed_text.txt> <translated_text.txt>")
        sys.exit(1)
        
    preprocessed_file = sys.argv[1]
    translated_file = sys.argv[2]
    
    split_chapters(preprocessed_file, translated_file)
