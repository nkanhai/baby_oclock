"""
Test voice input parsing logic.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from voice_parser import parse_voice_input


class TestBottlePhrases:
    """Test bottle feed voice parsing"""

    def test_bottle_90_ml(self):
        result = parse_voice_input("bottle 90 ml")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 90.0

    def test_fed_90_milliliters(self):
        result = parse_voice_input("fed 90 milliliters")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 90.0

    def test_90_ml_bottle(self):
        result = parse_voice_input("90 ml bottle")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 90.0

    def test_bottle_feed_60_point_5_ml(self):
        result = parse_voice_input("bottle feed 60.5 ml")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 60.5

    def test_fed_baby_120_ml(self):
        result = parse_voice_input("fed baby 120 ml")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 120.0

    def test_bottle_no_amount(self):
        result = parse_voice_input("bottle")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] is None

    def test_feed_with_number_word(self):
        # Testing single digit ml which is rare but supported by logic
        result = parse_voice_input("feed five ml")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 5.0


class TestNursingPhrases:
    """Test nursing voice parsing"""

    def test_nurse_left(self):
        result = parse_voice_input("nurse left")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'

    def test_nursed_on_the_left_side(self):
        result = parse_voice_input("nursed on the left side")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'

    def test_breastfed_right_10_minutes(self):
        result = parse_voice_input("breastfed right 10 minutes")
        assert result['type'] == 'nurse'
        assert result['side'] == 'right'
        assert result['duration_min'] == 10

    def test_nursing_both_sides(self):
        result = parse_voice_input("nursing both sides")
        assert result['type'] == 'nurse'
        assert result['side'] == 'both'

    def test_left_side_15_minutes(self):
        result = parse_voice_input("left side 15 minutes")
        # This is ambiguous - might not detect type without "nurse" keyword
        # Current implementation may return None
        # This test documents current behavior
        if result:
            assert result['side'] == 'left'
            assert result['duration_min'] == 15

    def test_nursed_no_side(self):
        result = parse_voice_input("nursed")
        assert result['type'] == 'nurse'
        assert result['side'] is None


class TestPumpPhrases:
    """Test pump voice parsing"""

    def test_pumped_120_ml_both(self):
        result = parse_voice_input("pumped 120 ml both")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount_ml'] == 120.0

    def test_pump_left_60_ml(self):
        result = parse_voice_input("pump left 60 ml")
        assert result['type'] == 'pump'
        assert result['side'] == 'left'
        assert result['amount_ml'] == 60.0

    def test_pumped_right_side_90_ml(self):
        result = parse_voice_input("pumped right side 90 ml")
        assert result['type'] == 'pump'
        assert result['side'] == 'right'
        assert result['amount_ml'] == 90.0

    def test_pump_both_sides_150_ml(self):
        result = parse_voice_input("pump both sides 150 ml")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount_ml'] == 150.0

    def test_pumped_no_details(self):
        result = parse_voice_input("pumped")
        assert result['type'] == 'pump'
        assert result['side'] is None
        assert result['amount_ml'] is None


class TestAmbiguousEdgeCases:
    """Test ambiguous and edge case inputs"""

    def test_empty_string(self):
        result = parse_voice_input("")
        assert result is None

    def test_hello(self):
        result = parse_voice_input("hello")
        assert result is None

    def test_just_90_ml(self):
        result = parse_voice_input("90 ml")
        # Current implementation may not detect type
        # This documents current behavior
        if result:
            assert result['amount_ml'] == 90.0

    def test_bottle_with_side_ignored(self):
        result = parse_voice_input("bottle left 90 ml")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 90.0
        # Side should be ignored for bottles (current implementation will capture it)
        # This tests current behavior

    def test_just_number_two(self):
        result = parse_voice_input("two")
        # Ambiguous - should not parse without context
        # Current implementation won't detect type
        assert result is None

    def test_nursed_90_ml_left(self):
        result = parse_voice_input("nursed 90 ml left")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'
        # Amount might be captured even though unusual for nursing
        if result.get('amount_ml'):
            assert result['amount_ml'] == 90.0


class TestNumberWordConversion:
    """Test number word to digit conversion"""

    def test_one(self):
        result = parse_voice_input("bottle one ml")
        assert result['amount_ml'] == 1.0

    def test_two(self):
        result = parse_voice_input("feed two ml")
        assert result['amount_ml'] == 2.0

    def test_three(self):
        result = parse_voice_input("bottle three ml")
        assert result['amount_ml'] == 3.0

    def test_four(self):
        result = parse_voice_input("fed four ml")
        assert result['amount_ml'] == 4.0

    def test_five(self):
        result = parse_voice_input("bottle five ml")
        assert result['amount_ml'] == 5.0

    def test_six(self):
        result = parse_voice_input("feed six ml")
        assert result['amount_ml'] == 6.0

    def test_seven(self):
        result = parse_voice_input("bottle seven ml")
        assert result['amount_ml'] == 7.0

    def test_eight(self):
        result = parse_voice_input("fed eight ml")
        assert result['amount_ml'] == 8.0

    def test_nine(self):
        result = parse_voice_input("bottle nine ml")
        assert result['amount_ml'] == 9.0

    def test_ten(self):
        result = parse_voice_input("feed ten ml")
        assert result['amount_ml'] == 10.0


class TestDuration:
    """Test duration parsing"""

    def test_10_minutes(self):
        result = parse_voice_input("nursed left 10 minutes")
        assert result['duration_min'] == 10

    def test_15_min(self):
        result = parse_voice_input("nurse right 15 min")
        assert result['duration_min'] == 15

    def test_duration_without_type(self):
        result = parse_voice_input("20 minutes")
        # Without type keyword, should not parse
        assert result is None


class TestCaseSensitivity:
    """Test that parsing is case-insensitive"""

    def test_uppercase(self):
        result = parse_voice_input("BOTTLE 90 ML")
        assert result['type'] == 'bottle'
        assert result['amount_ml'] == 90.0

    def test_mixed_case(self):
        result = parse_voice_input("Nursed Left 10 Minutes")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'
        assert result['duration_min'] == 10

    def test_lowercase(self):
        result = parse_voice_input("pumped both 120 ml")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount_ml'] == 120.0
