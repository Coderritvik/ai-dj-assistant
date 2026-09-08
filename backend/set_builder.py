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
        return [t for t in tracks if 118 <= t["bpm"] <= 145]
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
        start = min(remaining, key=lambda t: t["energy"])
    elif context == "closing":
        start = max(remaining, key=lambda t: t["energy"])
    else:  # peak
        start = max(remaining, key=lambda t: (t["energy"], t["danceability"]))

    ordered_set = [start]
    remaining.remove(start)

    current = start
    total_tracks = len(remaining)
    step = 0

    while remaining:
        step += 1
        progress = step / total_tracks  # 0.0 at start, approaches 1.0 near the end

        # Build a filtered pool based on context and how far into the set we are
        if context == "opening":
            # Energy floor rises over time — later tracks must be at least this energetic
            energy_floor = current["energy"] * (0.85 + 0.3 * progress)
            pool = [t for t in remaining if t["energy"] >= energy_floor]
        elif context == "closing":
            # Energy ceiling falls over time — later tracks must be at or below this
            energy_ceiling = current["energy"] * (1.15 - 0.3 * progress)
            pool = [t for t in remaining if t["energy"] <= energy_ceiling]
        else:
            pool = remaining

        # If the strict filter leaves nothing, fall back to the full remaining list
        # rather than crash — a slightly-off transition beats no track at all
        if len(pool) == 0:
            pool = remaining

        scored = []
        for candidate in pool:
            transition_score = score_transition(current, candidate)
            scored.append((transition_score, candidate))

        scored.sort(key=lambda x: x[0], reverse=True)
        next_track = scored[0][1]

        ordered_set.append(next_track)
        remaining.remove(next_track)
        current = next_track

    return ordered_set