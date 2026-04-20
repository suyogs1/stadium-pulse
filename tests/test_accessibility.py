"""
StadiumPulse Accessibility Audit Suite.

This module performs static analysis on the UI source code to ensure
adherence to accessibility standards (ARIA, Semantic HTML, Labels).
"""

import os
import re
import pytest

APP_PATH = "src/ui/dashboard.py"


@pytest.fixture
def app_source():
    """Reads the application source code for inspection."""
    if not os.path.exists(APP_PATH):
        pytest.fail(f"Application source not found at {APP_PATH}")
    with open(APP_PATH, "r", encoding="utf-8") as f:
        return f.read()


def test_semantic_headings(app_source):
    """Verifies the presence of semantic heading elements for screen readers."""
    assert "st.title(" in app_source or "<h1" in app_source, "Main page title (H1) is missing."
    assert (
        "st.header(" in app_source or "st.subheader(" in app_source
    ), "Section headers (H2/H3) are missing."


def test_interactive_widget_labels(app_source):
    """
    Ensures that all Streamlit interactive widgets have descriptive labels.
    """
    widgets = [r"st\.button\(", r"st\.selectbox\(", r"st\.slider\("]
    for widget_pattern in widgets:
        matches = re.findall(widget_pattern + r"\s*['\"]([^'\"]+)['\"]", app_source)
        if not matches and widget_pattern in app_source:
            pytest.fail(f"Detected widget {widget_pattern} potentially missing a static label.")


def test_assistive_descriptions_and_arias(app_source):
    """Verifies that complex visual elements have ARIA-friendly descriptions."""
    assert "aria-label=" in app_source, "Complex SVG visualizations are missing ARIA labels."
    assert "st.caption(" in app_source, "Figures and maps are missing descriptive captions."


def test_color_blind_legend_presence(app_source):
    """Ensures that textual color indicators exist."""
    legend_indicators = ["Healthy", "Warning", "Danger"]
    for indicator in legend_indicators:
        assert indicator in app_source, f"Congestion legend indicator '{indicator}' is missing."


def test_theme_mode_selector(app_source):
    """Verifies the multi-theme appearance selector."""
    assert "ui_theme" in app_source, "Theme state management is missing."
    assert "Appearance Theme" in app_source, "Appearance selector is missing."
    assert "High Contrast" in app_source, "High Contrast option is missing."


def test_venue_selector_label(app_source):
    """Verifies descriptive label for venue selection."""
    assert "Active Venue Select" in app_source, "Venue selector is missing a descriptive label."
