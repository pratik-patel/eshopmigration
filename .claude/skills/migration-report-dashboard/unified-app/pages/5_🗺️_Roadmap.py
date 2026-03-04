"""
Roadmap Page
Implementation waves, timeline, and dependencies
"""

import streamlit as st
import sys
from pathlib import Path
import json
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.unified_loader import UnifiedDataLoader
import pandas as pd

st.set_page_config(page_title="Roadmap", page_icon="🗺️", layout="wide")

# Load data
@st.cache_resource
def get_data_loader():
    return UnifiedDataLoader(
        docs_path="../../../../docs",
        mock_legacy_path="../../mock-data/legacy"
    )

try:
    loader = get_data_loader()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

st.title("🗺️ Implementation Roadmap")
st.markdown("### Phase 4: Implementation waves, critical path, and priorities")

if not data_loaded:
    st.error("Data loading failed. Check paths and data sources.")
    st.stop()

try:
    roadmap_path = Path(loader.modern.docs_path) / "implementation-roadmap.md"

    if not roadmap_path.exists():
        st.info("Implementation roadmap not found. Run Phase 4 (Roadmap) to generate migration plan.")
        st.stop()

    # Load roadmap content
    content = roadmap_path.read_text(encoding="utf-8")

    # Display full content
    tab1, tab2, tab3 = st.tabs(["📄 Roadmap Document", "🌊 Waves", "📊 Timeline"])

    with tab1:
        st.subheader("Full Roadmap Document")
        st.markdown(content)

    with tab2:
        st.subheader("Implementation Waves")

        # Try to extract wave information from markdown
        wave_pattern = r'##\s+Wave\s+(\d+):\s+(.+)'
        waves = re.findall(wave_pattern, content)

        if not waves:
            st.info("No wave structure detected in roadmap. View the full document for details.")
        else:
            for wave_num, wave_name in waves:
                with st.expander(f"**Wave {wave_num}: {wave_name}**", expanded=(wave_num == "1")):
                    # Extract content for this wave
                    wave_header = f"## Wave {wave_num}: {wave_name}"
                    next_wave_header = f"## Wave {int(wave_num) + 1}:"

                    start_idx = content.find(wave_header)
                    if start_idx != -1:
                        end_idx = content.find(next_wave_header, start_idx)
                        if end_idx == -1:
                            # Last wave
                            next_section = content.find("\n## ", start_idx + len(wave_header))
                            end_idx = next_section if next_section != -1 else len(content)

                        wave_content = content[start_idx:end_idx]

                        # Try to extract seams mentioned in this wave
                        seam_pattern = r'`([a-z-]+)`'
                        mentioned_seams = list(set(re.findall(seam_pattern, wave_content)))

                        if mentioned_seams:
                            st.markdown("**Seams in this wave:**")
                            for seam in mentioned_seams:
                                st.markdown(f"- `{seam}`")

                        # Display wave content
                        st.markdown(wave_content)

        # Wave summary
        if waves:
            st.markdown("---")
            st.subheader("Wave Summary")

            wave_data = []
            for wave_num, wave_name in waves:
                # Try to extract seam count
                wave_header = f"## Wave {wave_num}: {wave_name}"
                start_idx = content.find(wave_header)
                if start_idx != -1:
                    end_idx = content.find(f"## Wave {int(wave_num) + 1}:", start_idx)
                    if end_idx == -1:
                        end_idx = len(content)
                    wave_content = content[start_idx:end_idx]
                    seam_pattern = r'`([a-z-]+)`'
                    mentioned_seams = len(set(re.findall(seam_pattern, wave_content)))

                    wave_data.append({
                        "Wave": f"Wave {wave_num}",
                        "Name": wave_name,
                        "Seams": mentioned_seams,
                    })

            df = pd.DataFrame(wave_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Timeline View")

        # Extract timeline information if present
        if "timeline" in content.lower() or "duration" in content.lower():
            st.markdown("Timeline information extracted from roadmap:")

            # Try to find duration/timeline mentions
            duration_pattern = r'(\d+)\s+(weeks?|months?|days?)'
            durations = re.findall(duration_pattern, content, re.IGNORECASE)

            if durations:
                st.info(f"Found {len(durations)} timeline mentions in the roadmap document.")

                # Show duration mentions
                for duration, unit in durations:
                    st.markdown(f"- {duration} {unit}")
            else:
                st.info("No explicit timeline durations found in roadmap.")

        # Show seam dependency information
        st.markdown("---")
        st.subheader("Seam Dependencies")

        proposals = loader.modern.load_seam_proposals()
        seams = proposals.get("seams", [])

        if seams:
            dep_data = []
            for seam in seams:
                name = seam.get("seam_name") or seam.get("name") or seam.get("seam_id")
                deps = seam.get("dependencies", [])
                priority = seam.get("priority", "medium")

                dep_data.append({
                    "Seam": name,
                    "Priority": priority.upper(),
                    "Dependencies": len(deps),
                    "Depends On": ", ".join(deps) if deps else "None"
                })

            df_deps = pd.DataFrame(dep_data)
            st.dataframe(df_deps, use_container_width=True, hide_index=True)

            # Critical path identification
            st.markdown("---")
            st.subheader("Critical Path")

            high_priority = [s for s in seams
                           if s.get("priority", "").lower() == "high"]

            if high_priority:
                st.warning(f"**{len(high_priority)} high-priority seams** identified:")
                for seam in high_priority:
                    name = seam.get("seam_name") or seam.get("name") or seam.get("seam_id")
                    st.markdown(f"- `{name}`")
            else:
                st.info("No high-priority seams identified yet.")

        else:
            st.info("No seam dependency data available.")

except Exception as e:
    st.error("Error loading roadmap")
    st.exception(e)
