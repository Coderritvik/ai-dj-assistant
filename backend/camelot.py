# Maps musical key + scale to Camelot wheel notation
CAMELOT_MAP = {
    "Ab minor": "1A", "B major": "1B",
    "Eb minor": "2A", "F# major": "2B",
    "Bb minor": "3A", "Db major": "3B",
    "F minor": "4A", "Ab major": "4B",
    "C minor": "5A", "Eb major": "5B",
    "G minor": "6A", "Bb major": "6B",
    "D minor": "7A", "F major": "7B",
    "A minor": "8A", "C major": "8B",
    "E minor": "9A", "G major": "9B",
    "B minor": "10A", "D major": "10B",
    "F# minor": "11A", "A major": "11B",
    "C# minor": "12A", "E major": "12B",
}

def get_camelot(key, scale):
    lookup_key = f"{key} {scale}"
    return CAMELOT_MAP.get(lookup_key, "Unknown")


def is_harmonically_compatible(camelot1, camelot2):
    if camelot1 == "Unknown" or camelot2 == "Unknown":
        return False

    if camelot1 == camelot2:
        return True

    num1, letter1 = int(camelot1[:-1]), camelot1[-1]
    num2, letter2 = int(camelot2[:-1]), camelot2[-1]

    # Same letter, adjacent number (wheel wraps around from 12 to 1)
    if letter1 == letter2:
        if abs(num1 - num2) == 1 or abs(num1 - num2) == 11:
            return True

    # Same number, opposite letter (relative major/minor)
    if num1 == num2 and letter1 != letter2:
        return True

    return False