#!/usr/bin/env python3
"""
Script to rename and move all v1/ files to raw/ with three-digit prefixes and snake_case.
"""
import os
import re
import subprocess
import sys
from pathlib import Path

# Force UTF-8 encoding for console output to handle Unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def to_snake_case(text):
    """Convert text to snake_case."""
    # Replace special characters and spaces with underscores
    text = re.sub(r'[–—\-\s]+', '_', text)
    # Remove special characters
    text = re.sub(r'[^\w_]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove multiple consecutive underscores
    text = re.sub(r'_+', '_', text)
    # Remove leading/trailing underscores
    text = text.strip('_')
    return text

def parse_filename(filename):
    """Parse filename and extract number prefix and rest."""
    # Remove extension
    name_no_ext = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]

    # Match patterns like "01 Title", "15-01 Title", "15_01 Title"
    match = re.match(r'^(\d+)([_\-])?(\d+)?\s+(.+)$', name_no_ext)

    if match:
        prefix = match.group(1)  # Main number
        separator = match.group(2)  # - or _
        sub_number = match.group(3)  # Sub-index if present
        title = match.group(4)  # Rest of title

        # Convert prefix to 3 digits
        prefix_3digit = prefix.zfill(3)

        # Build snake_case title
        snake_title = to_snake_case(title)

        # Build new name
        if sub_number:
            # Keep sub-index format: 015_01_title
            new_name = f"{prefix_3digit}_{sub_number}_{snake_title}{ext}"
        else:
            # Just main number: 001_title
            new_name = f"{prefix_3digit}_{snake_title}{ext}"

        return new_name
    else:
        # Fallback: just convert to snake_case
        return to_snake_case(name_no_ext) + ext

def main():
    v1_dir = Path(r"W:\workspace\tick-frame-space\docs\theory\v1")
    raw_dir = Path(r"W:\workspace\tick-frame-space\docs\theory\raw")

    # Get all files in v1/
    files = sorted(v1_dir.glob("*"))

    print(f"Found {len(files)} files in v1/")
    print()

    # Create list of rename commands
    commands = []

    for old_path in files:
        if old_path.is_file():
            old_name = old_path.name
            new_name = parse_filename(old_name)
            new_path = raw_dir / new_name

            # Skip if already moved (052 file)
            if old_name == "52 Black Hole Behavior in the Tick‑Frame Universe.md":
                print(f"SKIP (already moved): {old_name}")
                continue

            print(f"{old_name}")
            print(f"  -> {new_name}")
            print()

            # Build git mv command
            cmd = ["git", "mv", str(old_path), str(new_path)]
            commands.append(cmd)

    print(f"\n{len(commands)} files to move.")
    print("\nExecuting git mv commands...")

    # Execute all commands
    for i, cmd in enumerate(commands, 1):
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=r"W:\workspace\tick-frame-space")
            print(f"[{i}/{len(commands)}] Moved: {Path(cmd[2]).name}")
        except subprocess.CalledProcessError as e:
            print(f"ERROR moving {Path(cmd[2]).name}: {e.stderr}")

    print("\nDone!")

if __name__ == "__main__":
    main()
