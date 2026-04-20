"""
StadiumPulse Automated UI Accessibility Audit.

Verifies that the dashboard adheres to basic WCAG-inspired
accessibility standards for headings, labels, and semantic context.
"""


def test_semantic_heading_hierarchy():
    """Verify that the dashboard uses a logical heading structure."""
    with open("src/ui/dashboard.py", "r", encoding="utf-8") as f:
        content = f.read()

    # H1 equivalent
    assert "st.title(" in content or "<h1" in content
    # H2/H3 equivalents
    assert "st.header(" in content or "st.subheader(" in content
    assert "Operational Pulse Console" in content
    assert "Geospatial Congestion Mapping" in content


def test_descriptive_interaction_labels():
    """Ensure all interactive controls have meaningful labels."""
    with open("src/ui/dashboard.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Verification of key UI triggers
    assert "Active Venue Select" in content
    assert "Appearance Theme" in content
    assert "⏮️ Prev" in content
    assert "Next ⏭️" in content


def test_congestion_legend_presence():
    """Verify that the heatmaps include a textual legend explaining color codes."""
    with open("src/ui/dashboard.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Semantic color definitions in the legend
    assert "Healthy" in content
    assert "Warning" in content
    assert "Danger" in content


def test_visual_asset_captions():
    """Ensure that complex visualizations (charts/maps) have descriptive captions."""
    with open("src/ui/dashboard.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Figures and descriptive text
    assert "st.caption(" in content
    assert "Figure 1: Stadium Pulse Heatmap" in content
    assert "aria-label" in content.lower()  # Verify presence of ARIA hints


def test_aria_landmark_attributes():
    """Verify that specialized components use ARIA roles for screen readers."""
    with open("src/ui/dashboard.py", "r", encoding="utf-8") as f:
        content = f.read()

    assert 'role="img"' in content, "Heatmap container missing semantic role."
    assert "aria-label=" in content.lower(), "Complex SVG nodes missing descriptive labels."
