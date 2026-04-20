"""
StadiumPulse Venue Layout & Architectural Unit Tests.

Verifies the dynamic generation of stadium seating coordinates
and venue-specific architectural logic.
"""

from src.core.venues import create_stadium_venue, STADIUM_MAP


def test_circular_layout_generation():
    """Verify that a generic venue generates a circular layout."""
    venue = create_stadium_venue("Standard Arena", 4, 1, 1)

    # Check section count
    assert len(venue.sections) == 4

    # Check coordinates for S1 (i=1)
    # Circular: x = 200 + 130 * cos(angle), y = 200 + 130 * sin(angle)
    s1 = venue.sections[0]
    assert s1.section_id == "S1"
    assert 200.0 <= s1.x <= 400.0
    assert 200.0 <= s1.y <= 400.0


def test_modi_elliptical_layout():
    """Verify that Narendra Modi Stadium uses its unique elliptical logic."""
    venue = STADIUM_MAP["modi"]
    assert "Narendra Modi" in venue.stadium_name

    # The elliptical factor uses 160(x) and 150(y)
    # Check that x coordinates reach farther than the standard 130
    max_x = max(s.x for s in venue.sections)
    assert max_x > 330.0  # 200 + 130 = 330 (standard circle max)


def test_wembley_rectangular_oval_layout():
    """Verify that Wembley Stadium uses its rectangular-oval logic."""
    venue = STADIUM_MAP["wembley"]
    assert "Wembley" in venue.stadium_name

    # The rectangular-oval uses 150(x) and 110(y)
    # It should be wider than it is tall
    max_x = max(s.x for s in venue.sections)
    max_y = max(s.y for s in venue.sections)
    min_x = min(s.x for s in venue.sections)
    min_y = min(s.y for s in venue.sections)

    width = max_x - min_x
    height = max_y - min_y
    assert width > height  # Rectangular oval characteristic


def test_dynamic_capacity_scaling():
    """Verify that section capacity scales inversely with section count."""
    venue_small = create_stadium_venue("Mini", 10, 1, 1)  # 120000 / 10 = 12000
    venue_large = create_stadium_venue("Mega", 100, 1, 1)  # 120000 / 100 = 1200

    assert venue_small.sections[0].capacity == 12000
    assert venue_large.sections[0].capacity == 1200


def test_seating_color_logic_integration():
    """
    Verifies the range of coordinates remains within the 0-400 SVG viewport.
    (Color logic itself is tested in app/integration level, here we test the geometry).
    """
    for venue in STADIUM_MAP.values():
        for section in venue.sections:
            assert 0 <= section.x <= 400
            assert 0 <= section.y <= 400
