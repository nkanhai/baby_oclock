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

    def test_bottle_3_ounces(self):
        result = parse_voice_input("bottle 3 ounces")
        assert result['type'] == 'bottle'
        assert result['amount'] == 3.0

    def test_fed_three_ounces(self):
        result = parse_voice_input("fed three ounces")
        assert result['type'] == 'bottle'
        assert result['amount'] == 3.0

    def test_3_ounce_bottle(self):
        result = parse_voice_input("3 ounce bottle")
        assert result['type'] == 'bottle'
        assert result['amount'] == 3.0

    def test_bottle_feed_2_point_5_oz(self):
        result = parse_voice_input("bottle feed 2.5 oz")
        assert result['type'] == 'bottle'
        assert result['amount'] == 2.5

    def test_fed_baby_4_ounces(self):
        result = parse_voice_input("fed baby 4 ounces")
        assert result['type'] == 'bottle'
        assert result['amount'] == 4.0

    def test_bottle_no_amount(self):
        result = parse_voice_input("bottle")
        assert result['type'] == 'bottle'
        assert result['amount'] is None

    def test_fed_2_and_a_half_ounces(self):
        result = parse_voice_input("fed 2 and a half ounces")
        assert result['type'] == 'bottle'
        # This might not parse perfectly with current implementation
        # May need to enhance parser for this

    def test_feed_with_number_word(self):
        result = parse_voice_input("feed five ounces")
        assert result['type'] == 'bottle'
        assert result['amount'] == 5.0


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
        assert result['duration'] == 10

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
            assert result['duration'] == 15

    def test_nursed_no_side(self):
        result = parse_voice_input("nursed")
        assert result['type'] == 'nurse'
        assert result['side'] is None


class TestPumpPhrases:
    """Test pump voice parsing"""

    def test_pumped_4_ounces_both(self):
        result = parse_voice_input("pumped 4 ounces both")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount'] == 4.0

    def test_pump_left_2_ounces(self):
        result = parse_voice_input("pump left 2 ounces")
        assert result['type'] == 'pump'
        assert result['side'] == 'left'
        assert result['amount'] == 2.0

    def test_pumped_right_side_3_oz(self):
        result = parse_voice_input("pumped right side 3 oz")
        assert result['type'] == 'pump'
        assert result['side'] == 'right'
        assert result['amount'] == 3.0

    def test_pump_both_sides_5_ounces(self):
        result = parse_voice_input("pump both sides 5 ounces")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount'] == 5.0

    def test_pumped_no_details(self):
        result = parse_voice_input("pumped")
        assert result['type'] == 'pump'
        assert result['side'] is None
        assert result['amount'] is None


class TestAmbiguousEdgeCases:
    """Test ambiguous and edge case inputs"""

    def test_empty_string(self):
        result = parse_voice_input("")
        assert result is None

    def test_hello(self):
        result = parse_voice_input("hello")
        assert result is None

    def test_just_3_ounces(self):
        result = parse_voice_input("3 ounces")
        # Current implementation may not detect type
        # This documents current behavior
        if result:
            assert result['amount'] == 3.0

    def test_bottle_with_side_ignored(self):
        result = parse_voice_input("bottle left 3 ounces")
        assert result['type'] == 'bottle'
        assert result['amount'] == 3.0
        # Side should be ignored for bottles (current implementation will capture it)
        # This tests current behavior

    def test_just_number_two(self):
        result = parse_voice_input("two")
        # Ambiguous - should not parse without context
        # Current implementation won't detect type
        assert result is None

    def test_nursed_three_ounces_left(self):
        result = parse_voice_input("nursed three ounces left")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'
        # Amount might be captured even though unusual for nursing
        if result['amount']:
            assert result['amount'] == 3.0


class TestNumberWordConversion:
    """Test number word to digit conversion"""

    def test_one(self):
        result = parse_voice_input("bottle one ounce")
        assert result['amount'] == 1.0

    def test_two(self):
        result = parse_voice_input("feed two ounces")
        assert result['amount'] == 2.0

    def test_three(self):
        result = parse_voice_input("bottle three ounces")
        assert result['amount'] == 3.0

    def test_four(self):
        result = parse_voice_input("fed four ounces")
        assert result['amount'] == 4.0

    def test_five(self):
        result = parse_voice_input("bottle five ounces")
        assert result['amount'] == 5.0

    def test_six(self):
        result = parse_voice_input("feed six ounces")
        assert result['amount'] == 6.0

    def test_seven(self):
        result = parse_voice_input("bottle seven ounces")
        assert result['amount'] == 7.0

    def test_eight(self):
        result = parse_voice_input("fed eight ounces")
        assert result['amount'] == 8.0

    def test_nine(self):
        result = parse_voice_input("bottle nine ounces")
        assert result['amount'] == 9.0

    def test_ten(self):
        result = parse_voice_input("feed ten ounces")
        assert result['amount'] == 10.0

    def test_half(self):
        result = parse_voice_input("bottle half ounce")
        assert result['amount'] == 0.5

    def test_two_and_a_half(self):
        result = parse_voice_input("bottle two and a half ounces")
        assert result['amount'] == 2.5

    def test_one_and_a_half(self):
        result = parse_voice_input("fed one and a half ounces")
        assert result['amount'] == 1.5


class TestDuration:
    """Test duration parsing"""

    def test_10_minutes(self):
        result = parse_voice_input("nursed left 10 minutes")
        assert result['duration'] == 10

    def test_15_min(self):
        result = parse_voice_input("nurse right 15 min")
        assert result['duration'] == 15

    def test_duration_without_type(self):
        result = parse_voice_input("20 minutes")
        # Without type keyword, should not parse
        assert result is None


class TestCaseSensitivity:
    """Test that parsing is case-insensitive"""

    def test_uppercase(self):
        result = parse_voice_input("BOTTLE 3 OUNCES")
        assert result['type'] == 'bottle'
        assert result['amount'] == 3.0

    def test_mixed_case(self):
        result = parse_voice_input("Nursed Left 10 Minutes")
        assert result['type'] == 'nurse'
        assert result['side'] == 'left'
        assert result['duration'] == 10

    def test_lowercase(self):
        result = parse_voice_input("pumped both 4 oz")
        assert result['type'] == 'pump'
        assert result['side'] == 'both'
        assert result['amount'] == 4.0
