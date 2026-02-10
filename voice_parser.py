"""
Voice input parser - Python implementation for testing.
This mirrors the JavaScript parsing logic in the frontend.
"""

import re


def parse_voice_input(transcript):
    """
    Parse a voice transcript into structured feed data.

    Returns a dict with keys: type, side, amount, duration
    or None if the transcript can't be parsed.
    """
    if not transcript or not transcript.strip():
        return None

    lower = transcript.lower()

    result = {
        'type': None,
        'side': None,
        'amount': None,
        'duration': None
    }

    # Parse type (order matters - check specific terms first to avoid false positives)
    # "breastfed" contains "fed", so check nurse keywords first
    if any(word in lower for word in ['nurse', 'nursed', 'nursing', 'breastfed', 'breast']):
        result['type'] = 'nurse'
    elif any(word in lower for word in ['pump', 'pumped', 'pumping']):
        result['type'] = 'pump'
    elif any(word in lower for word in ['bottle', 'fed', 'feed']):
        result['type'] = 'bottle'

    # Parse side
    if 'left' in lower:
        result['side'] = 'left'
    elif 'right' in lower:
        result['side'] = 'right'
    elif 'both' in lower:
        result['side'] = 'both'

    # Parse amount (look for number + ml/milliliter)
    amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:ml|milliliter)', lower)
    if amount_match:
        result['amount'] = float(amount_match.group(1))
    else:
        # Try number words
        number_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            # 'half' is less common for ml but kept for completeness
        }

        # Check for single number words
        if result['amount'] is None:
            for word, num in number_words.items():
                pattern = rf'\b{word}\s+(?:ml|milliliter)'
                if re.search(pattern, lower):
                    result['amount'] = num
                    break

        # Check for just numbers like "Bottle 30" (assume ml if > 10)
        if result['amount'] is None:
            # Look for number at end of string or after type
            trailing_num = re.search(r'\b(\d+)\s*$', lower)
            if trailing_num:
                val = int(trailing_num.group(1))
                if val >= 5: # Assume ml if >= 5 (unlikely to be oz > 10 for a baby)
                    result['amount'] = val

    # Parse duration (look for number + minute/min)
    duration_match = re.search(r'(\d+)\s*(?:minute|min)', lower)
    if duration_match:
        result['duration'] = int(duration_match.group(1))

    # If no type was detected, return None (unrecognized)
    if result['type'] is None:
        return None
        
    # Standardize result keys
    final_result = {
        'type': result['type'],
        'side': result['side'],
        'amount_ml': result['amount'],
        'duration_min': result['duration']
    }

    return final_result


def format_parsed_result(parsed):
    """Format parsed result for display."""
    if not parsed:
        return "Could not parse input"

    parts = []

    if parsed.get('type'):
        parts.append(f"Type: {parsed['type']}")

    if parsed.get('side'):
        parts.append(f"Side: {parsed['side']}")

    if parsed.get('amount_ml') is not None:
        parts.append(f"Amount: {parsed['amount_ml']} ml")

    if parsed.get('duration_min') is not None:
        parts.append(f"Duration: {parsed['duration_min']} min")

    return " | ".join(parts) if parts else "No data parsed"
