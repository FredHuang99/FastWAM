"""11-24 plan v20 card 5 (press_told): the sentence that tells the model the two press counts. ONE definition, used by
the simulator adapter (closed loop: the scene's card values, privileged, diagnostic only) and by
scripts/fullft/press_told_text.py (training: each demo's own press counts). Pure Python, no imports."""

WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}


def told_sentence(n1: int, n2: int) -> str:
    """Appended to the task instruction (leading space included)."""
    return f" Press the left button {WORDS[int(n1)]} times and the middle button {WORDS[int(n2)]} times."


def combos():
    """Every (card_id_1, card_id_2) the env can draw: card_id_1 in 1..9, card_id_2 in 1..10 - card_id_1 (45 pairs)."""
    return [(a, b) for a in range(1, 10) for b in range(1, 11 - a)]
