#!/usr/bin/env python3
"""
Parse ui-behavior.md to structured ui-behavior.json
Uses basic markdown parsing to extract screens, controls, grids, actions
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def parse_ui_behavior_md(md_content: str, seam: str) -> Dict[str, Any]:
    """Parse ui-behavior.md markdown into structured JSON"""

    data = {
        "seam": seam,
        "screens": [],
        "navigation": {},
        "assets": [],
        "interactions": []
    }

    lines = md_content.split('\n')
    current_screen = None
    current_section = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Screen detection
        if line.startswith('## Screen:') or line.startswith('### Screen:'):
            if current_screen:
                data['screens'].append(current_screen)
            current_screen = {
                "name": re.sub(r'^##+ Screen:\s*', '', line),
                "description": "",
                "layout": "",
                "controls": [],
                "grids": [],
                "actions": []
            }
            current_section = None

        # Layout section
        elif current_screen and line.startswith('**Layout'):
            current_section = "layout"
            # Next line has layout description
            i += 1
            if i < len(lines):
                current_screen['layout'] = lines[i].strip()

        # Controls section
        elif current_screen and line.startswith('**Controls'):
            current_section = "controls"

        # Grid section
        elif current_screen and (line.startswith('**Grid') or line.startswith('**Table')):
            current_section = "grid"
            grid_name = re.sub(r'\*\*|\*|:', '', line).strip()
            current_grid = {
                "name": grid_name,
                "columns": [],
                "features": [],
                "data_source": ""
            }

        # Actions section
        elif current_screen and line.startswith('**Actions'):
            current_section = "actions"

        # Parse controls (button, input, dropdown, etc.)
        elif current_section == "controls" and line.startswith('- **'):
            control_match = re.match(r'- \*\*(.+?)\*\*\s*\((.+?)\)', line)
            if control_match:
                current_screen['controls'].append({
                    "name": control_match.group(1),
                    "type": control_match.group(2).lower(),
                    "label": control_match.group(1),
                    "properties": {}
                })

        # Parse grid columns
        elif current_section == "grid" and line.startswith('- '):
            column_name = line.replace('- ', '').replace('**', '').strip()
            if column_name and 'current_grid' in locals():
                current_grid['columns'].append(column_name)

        # Parse actions (button clicks, form submits)
        elif current_section == "actions" and line.startswith('- '):
            action_match = re.match(r'- \*\*(.+?)\*\*:?\s*(.+)', line)
            if action_match:
                current_screen['actions'].append({
                    "trigger": action_match.group(1),
                    "action": action_match.group(2),
                    "target": ""
                })

        # Save completed grid
        if current_section != "grid" and 'current_grid' in locals():
            if current_screen and current_grid['columns']:
                current_screen['grids'].append(current_grid)
            del current_grid

        # Navigation section (outside screens)
        if line.startswith('## Navigation') or line.startswith('### Navigation'):
            current_screen = None
            current_section = "navigation"

        elif current_section == "navigation" and line.startswith('- **Menu'):
            menu_match = re.match(r'- \*\*Menu\s*Path\*\*:?\s*(.+)', line)
            if menu_match:
                data['navigation']['menu_path'] = menu_match.group(1).strip()

        elif current_section == "navigation" and line.startswith('- **Route'):
            route_match = re.match(r'- \*\*Route\*\*:?\s*(.+)', line)
            if route_match:
                data['navigation']['route'] = route_match.group(1).strip()

        # Assets section
        if line.startswith('## Assets') or line.startswith('### Assets'):
            current_screen = None
            current_section = "assets"

        elif current_section == "assets" and line.startswith('- '):
            asset_match = re.match(r'- (.+?)\s*\((.+?)\)', line)
            if asset_match:
                data['assets'].append({
                    "name": asset_match.group(1),
                    "type": asset_match.group(2).lower(),
                    "path": "",
                    "usage": ""
                })

        i += 1

    # Add last screen
    if current_screen:
        data['screens'].append(current_screen)

    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: parse-ui-behavior-to-json.py <seam_name>", file=sys.stderr)
        sys.exit(1)

    seam = sys.argv[1]
    md_path = Path(f"docs/seams/{seam}/ui-behavior.md")
    json_path = Path(f"docs/seams/{seam}/ui-behavior.json")

    if not md_path.exists():
        print(f"❌ File not found: {md_path}", file=sys.stderr)
        sys.exit(1)

    try:
        md_content = md_path.read_text(encoding='utf-8')
        data = parse_ui_behavior_md(md_content, seam)

        json_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
        print(f"✅ Created {json_path}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
