import os

# Folder to search
root_folder = r'C:\Users\laolu\OneDrive\Desktop\SCRAPPY SCHEDULER'
output_file = 'parsed_code_output.txt'

# File extensions to include
include_extensions = ('.py', '.html', '.css', '.js')

# Write to the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    for dirpath, dirnames, filenames in os.walk(root_folder):
        # Skip __pycache__ folders
        if '__pycache__' in dirpath:
            continue
        for filename in filenames:
            if filename.endswith(include_extensions) and not filename.endswith('.pyc'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        relative_path = os.path.relpath(file_path, root_folder)
                        outfile.write(f'\n\n--- FILE: {relative_path} ---\n')
                        outfile.write(f.read())
                except Exception as e:
                    outfile.write(f'\n\n--- FILE: {relative_path} (ERROR: {e}) ---\n')

print(f'\n✅ Done! Parsed files saved in: {output_file}')
