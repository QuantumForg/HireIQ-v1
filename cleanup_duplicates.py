import os
import shutil
import re

def main():
    print("Starting HireIQ Workspace Cleanup...")
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # We will walk through all files recursively
    files_to_delete = []
    copies_made = 0
    
    # Pattern to match files containing " (2)" before the extension
    # e.g., "README (2).md" or "constants (2).py"
    pattern = re.compile(r"^(.*)\s\(2\)(\.[^.]+)?$")
    
    for root, dirs, files in os.walk(project_root):
        # Exclude common directories to speed up and prevent modifying venv or git files
        if any(ignored in root for ignored in [".git", "venv", ".venv", "__pycache__"]):
            continue
            
        for file in files:
            match = pattern.match(file)
            if match:
                base_name = match.group(1)
                ext = match.group(2) or ""
                original_file_name = base_name + ext
                
                dup_path = os.path.join(root, file)
                orig_path = os.path.join(root, original_file_name)
                
                print(f"Copying '{dup_path}' -> '{orig_path}'")
                shutil.copy2(dup_path, orig_path)
                copies_made += 1
                files_to_delete.append(dup_path)
                
            # Check for final_score.py.archived
            if file == "final_score.py.archived":
                archived_path = os.path.join(root, file)
                files_to_delete.append(archived_path)
                
    print(f"\nCompleted copying {copies_made} updated files.")
    print("Deleting duplicate and archived files...")
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            print(f"Removing: {file_path}")
            os.remove(file_path)
            
    print("\nCleanup successfully completed! Codebase is now clean and up-to-date.")

if __name__ == "__main__":
    main()
