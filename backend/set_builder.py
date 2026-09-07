from camelot import get_camelot, is_harmonically_compatible


def score_transition(current, candidate):
    """How good is it to play `candidate` right after `current`?"""
    bpm_diff = abs(candidate["bpm"] - current["bpm"])

    current_key_parts = current["key"].split(" ", 1)
    candidate_key_parts = candidate["key"].split(" ", 1)
    current_camelot = get_camelot(current_key_parts[0], current_key_parts[1])
    candidate_camelot = get_camelot(candidate_key_parts[0], candidate_key_parts[1])

    harmonic_match = is_harmonically_compatible(current_camelot, candidate_camelot)

    score = 0
    if harmonic_match:
        score += 100
    score -= bpm_diff

    return score


def deduplicate_tracks(tracks):
    """Keep only one entry per unique filename."""
    seen_filenames = set()
    unique_tracks = []
    for track in tracks:
        if track["filename"] not in seen_filenames:
            seen_filenames.add(track["filename"])
            unique_tracks.append(track)
    return unique_tracks


def filter_by_context(tracks, context):
    """Only consider tracks in a tempo range that makes sense for this context."""
    if context == "peak":
        # Peak sets stay in a tight, danceable tempo band
        return [t for t in tracks if 118 <= t["bpm"] <= 145]
    # Opening and closing can use a wider range, since they're meant to ease in/out
    return tracks


def build_set(tracks, context):
    """
    tracks: list of track dicts (from the database)
    context: "opening", "peak", or "closing"
    Returns an ordered list representing the built set.
    """
    tracks = deduplicate_tracks(tracks)
    tracks = filter_by_context(tracks, context)

    if len(tracks) == 0:
        return []

    remaining = tracks.copy()

    # Pick the starting track based on context
    if context == "opening":
        # Start with the lowest energy track
        start = min(remaining, key=lambda t: t["energy"])
    elif context == "closing":
        # Start with a high energy track, since we're winding down FROM peak energy
        start = max(remaining, key=lambda t: t["energy"])
    else:  # peak
        # Start with the highest energy, most danceable track
        start = max(remaining, key=lambda t: (t["energy"], t["danceability"]))

    ordered_set = [start]
    remaining.remove(start)

    current = start

    while remaining:
        # Score every remaining track as a potential next track
        scored = []
        for candidate in remaining:
            transition_score = score_transition(current, candidate)

            # Nudge the score based on the set's context and direction
            if context == "opening":
                # Prefer tracks with slightly higher energy than current (building up)
                if candidate["energy"] >= current["energy"]:
                    transition_score += 20
            elif context == "closing":
                # Prefer tracks with slightly lower energy than current (winding down)
                if candidate["energy"] <= current["energy"]:
                    transition_score += 20
            # "peak" has no energy-direction bonus, just wants strong transitions throughout

            scored.append((transition_score, candidate))

        # Pick the best-scoring next track
        scored.sort(key=lambda x: x[0], reverse=True)
        next_track = scored[0][1]

        ordered_set.append(next_track)
        remaining.remove(next_track)
        current = next_track

    return ordered_set