import unicodedata

# F4 is COMPLETE: all 11 error rules from the PRD are implemented.
#   CRITICAL (3): too short, no dialogue, no scene headings
#   MODERATE (5): incomplete heading, cue with no speech, very long speech,
#                 no ending marker, inconsistent character name
#   MINOR    (3): repeated word, extra spaces, sentence starts lowercase
#
# F5 (scoring) is added in this step: calculate_score() and rating_tier().
# F6 (report + closing comment) comes in step 11.

# Hausa hooked letters are often typed as plain b, d, k and y,
# so we treat each hooked letter and its plain version as the same letter.
HOOKED_LETTERS = {"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y"}

# A script with fewer words than this is too short to judge (error rule 1).
MIN_WORDS = 300

# Words that tell us the time of day in a scene heading (error rule: incomplete heading).
TIME_OF_DAY = ["DAY", "NIGHT", "MORNING", "AFTERNOON", "EVENING", "DAWN", "DUSK",
               "SUNRISE", "SUNSET", "MIDNIGHT", "NOON", "LATER", "CONTINUOUS"]

# A speech longer than this many words is hard to read and hard to act (error rule: very long speech).
MAX_SPEECH_WORDS = 80

# Lines that finish a script. They are not character names.
END_MARKERS = ["THE END", "FADE OUT", "FADE TO BLACK", "CUT TO BLACK"]

# STARTER word lists. One list per genre and per language.
# Rules: a word belongs to ONE genre only, and everyday words (like "so") are never used.
# The Yoruba, Hausa, Igbo and Pidgin lists are small on purpose.
# Fluent speakers must review them before we trust the results.
GENRE_KEYWORDS = {
    "Action": {
        "English": ["gun", "guns", "gunfire", "explosion", "explode", "fight", "chase",
                    "shoot", "battle", "attack", "escape", "crash", "punch", "kill",
                    "weapon", "war"],
        "Pidgin": [],
        "Yoruba": ["ìjà", "ìbọn", "ìkọlù", "jàǹbá"],
        "Hausa": ["yaƙi", "bindiga", "fashewa", "harbi", "faɗa"],
        "Igbo": ["agha", "ọgụ", "égbè"],
    },
    "Comedy": {
        "English": ["laugh", "laughs", "laughing", "joke", "jokes", "funny", "silly",
                    "prank", "hilarious", "giggle", "clown", "goofy", "ridiculous"],
        "Pidgin": [],
        "Yoruba": ["ẹ̀rín", "awada"],
        "Hausa": ["dariya", "barkwanci"],
        "Igbo": ["ọchị"],
    },
    "Romance": {
        "English": ["love", "loved", "kiss", "kisses", "romantic", "romance", "wedding",
                    "darling", "sweetheart", "beloved", "embrace"],
        "Pidgin": [],
        "Yoruba": ["ìfẹ́", "ìfẹnukonu", "ìgbéyàwó", "fẹ́ràn"],
        "Hausa": ["soyayya", "aure", "sumba", "ƙauna", "masoyi"],
        "Igbo": ["ịhụnanya", "agbamakwụkwọ"],
    },
    "Emotional/Drama": {
        "English": ["cry", "cries", "crying", "tears", "sad", "grief", "pain", "loss",
                    "heartbreak", "lonely", "forgive", "sorrow", "mourn", "regret"],
        "Pidgin": ["wahala"],
        "Yoruba": ["ẹkún", "ìbànújẹ́", "ìrora", "omijé", "ẹ̀dùn"],
        "Hausa": ["kuka", "hawaye", "makoki", "nadama"],
        "Igbo": ["mwute", "mgbu", "nchegbu"],
    },
    "Horror": {
        "English": ["blood", "scream", "screams", "ghost", "monster", "haunted",
                    "nightmare", "creepy", "demon", "terror", "corpse", "graveyard", "fear"],
        "Pidgin": ["juju", "witchcraft"],
        "Yoruba": ["òkú", "ẹ̀jẹ̀", "iwin", "òkùnkùn", "ìbẹ̀rù"],
        "Hausa": ["duhu", "aljani", "fatalwa", "jini", "tsoro", "gawa"],
        "Igbo": ["mmụọ", "ọchịchịrị", "ọbara", "ụjọ", "ogbanje"],
    },
    "Fiction/Fantasy": {
        "English": ["magic", "dragon", "wizard", "kingdom", "spell", "portal", "quest",
                    "prophecy", "sword", "castle", "legend", "alien", "robot", "spaceship"],
        "Pidgin": [],
        "Yoruba": ["idán", "oṣó", "àsọtẹ́lẹ̀"],
        "Hausa": ["sihiri", "tatsuniya"],
        "Igbo": ["amụma"],
    },
    "Erotic": {
        "English": ["desire", "passion", "seduce", "temptation", "intimate", "sensual",
                    "longing"],
        "Pidgin": [],
        "Yoruba": [],
        "Hausa": [],
        "Igbo": [],
    },
}

# ---- Colour (ANSI, no extra libraries) -----------------------------------
# Colour is a signal, never the only signal. Every colour is paired with a
# plain text label so the report stays readable for colour-blind users.
# Colours are always on. If you redirect output to a file you will see the
# raw ANSI codes, so print to the terminal when you want the colours.
RESET            = "\033[0m"
COLOUR_CRITICAL  = "\033[91m"    # red
COLOUR_MODERATE  = "\033[93m"    # yellow
COLOUR_MINOR     = "\033[96m"    # cyan
COLOUR_EXCELLENT = "\033[92m"    # green
COLOUR_PERFECT   = "\033[1;92m"  # bold green

SEVERITY_COLOURS = {
    "CRITICAL": COLOUR_CRITICAL,
    "MODERATE": COLOUR_MODERATE,
    "MINOR":    COLOUR_MINOR,
}

TIER_COLOURS = {
    "POOR":      COLOUR_CRITICAL,
    "AVERAGE":   COLOUR_MODERATE,
    "GOOD":      COLOUR_MINOR,
    "EXCELLENT": COLOUR_EXCELLENT,
    "PERFECT":   COLOUR_PERFECT,
}


def load_script(path):
    """Read a script file and return its text, or None if the file is missing."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"Sorry, I could not find '{path}'. Check the name and the folder.")
        return None


def clean_and_split(text):
    """Lowercase the text, remove punctuation, keep the letters of every
    language we support, and split the text into a list of words."""
    text = text.lower().replace("’", "'")
    kept = []
    for ch in text:
        if ch.isalpha() or ch.isdigit() or ch == "'" or unicodedata.category(ch) == "Mn":
            kept.append(ch)
        else:
            kept.append(" ")
    cleaned = "".join(kept)

    words = []
    for piece in cleaned.split():
        piece = piece.strip("'")
        if piece:
            words.append(piece)
    return words


def normalize_word(word):
    """Remove tone marks and dots under letters, so 'ìfẹ́' and 'ife' become the same word."""
    word = word.lower()
    for hooked, plain in HOOKED_LETTERS.items():
        word = word.replace(hooked, plain)
    decomposed = unicodedata.normalize("NFD", word)
    kept = []
    for ch in decomposed:
        if unicodedata.category(ch) != "Mn":
            kept.append(ch)
    return "".join(kept)


def build_keyword_sets():
    """Join the lists of all languages into ONE set of normalized words for each genre."""
    keyword_sets = {}
    for genre, languages in GENRE_KEYWORDS.items():
        genre_words = set()
        for language, keywords in languages.items():
            for keyword in keywords:
                genre_words.add(normalize_word(keyword))
        keyword_sets[genre] = genre_words
    return keyword_sets


def count_genre_matches(words):
    """Count how many words of the script belong to each genre."""
    keyword_sets = build_keyword_sets()
    normalized_words = [normalize_word(word) for word in words]
    counts = {}
    for genre, keywords in keyword_sets.items():
        matches = [word for word in normalized_words if word in keywords]
        counts[genre] = len(matches)
    return counts


def calculate_percentages(counts):
    """Turn genre counts into percentages (one decimal) that add up to exactly 100."""
    total = sum(counts.values())
    if total == 0:
        return {genre: 0.0 for genre in counts}

    tenths = {}
    leftovers = {}
    for genre in counts:
        tenths[genre] = counts[genre] * 1000 // total
        leftovers[genre] = counts[genre] * 1000 % total

    missing = 1000 - sum(tenths.values())
    for genre in sorted(leftovers, key=leftovers.get, reverse=True)[:missing]:
        tenths[genre] = tenths[genre] + 1

    return {genre: tenths[genre] / 10 for genre in tenths}


def percent_of(pair):
    return pair[1]


def print_genre_report(counts, percentages):
    """Print every genre from the biggest percentage to the smallest, with a small bar."""
    print("")
    print("Genres")
    ranked = sorted(percentages.items(), key=percent_of, reverse=True)
    for genre, percent in ranked:
        bar = "#" * int(percent / 3.5)
        print(f"  {genre:<16} {percent:5.1f}%  {bar}")
    print(f"Genre keywords found: {sum(counts.values())}")
    if sum(counts.values()) == 0:
        print("No genre keywords were found, so every genre shows 0.0%.")


def is_scene_heading(line):
    return line.strip().upper().startswith(("INT.", "EXT."))


def is_ending_marker(line):
    return line.strip().upper().strip(" .:!-*~") in END_MARKERS


def heading_has_time(line):
    cleaned = line.upper()
    for symbol in ".,-–—/()":
        cleaned = cleaned.replace(symbol, " ")
    found = [word for word in cleaned.split() if word in TIME_OF_DAY]
    return len(found) > 0


def is_character_cue(line):
    text = line.strip()
    if text == "" or is_scene_heading(text) or is_ending_marker(text):
        return False
    if text != text.upper() or text == text.lower():
        return False
    if text.endswith(".") or text.endswith(":"):
        return False
    return len(text.split()) <= 4


def looks_like_action_phrase(line):
    """True if an ALL-CAPS line reads like an action beat, not a name.
    Three or more ALL-CAPS words are almost certainly action."""
    return len(line.strip().split()) >= 3


def looks_like_speech(line):
    """True if a line reads like spoken dialogue, not action or a cue."""
    text = line.strip()
    if text == "":
        return False
    if is_scene_heading(text) or is_ending_marker(text):
        return False
    if text.startswith("(") and text.endswith(")"):
        return False
    if is_character_cue(text) and not looks_like_action_phrase(text):
        return False
    if text == text.upper() and len(text.split()) <= 5:
        return False
    return True


def has_dialogue(lines):
    """True if a real character name is followed by actual speech.
    All-caps action lines like 'THE CROWD CHEERS' are NOT treated as cues."""
    for i in range(len(lines) - 1):
        cue = lines[i]
        if not is_character_cue(cue):
            continue
        if looks_like_action_phrase(cue):
            continue
        if looks_like_speech(lines[i + 1]):
            return True
    return False


def make_error(line_number, severity, message, fix):
    return {"line": line_number, "severity": severity, "message": message, "fix": fix}


def find_critical_errors(lines):
    """Apply the three CRITICAL rules: too short, no dialogue, no scene headings."""
    errors = []

    word_count = sum([len(line.split()) for line in lines])
    if word_count < MIN_WORDS:
        errors.append(make_error(
            None, "CRITICAL",
            f"Too short ({word_count} words, the minimum is {MIN_WORDS})",
            "Write more scenes and dialogue until the script passes 300 words"))

    if not has_dialogue(lines):
        errors.append(make_error(
            None, "CRITICAL",
            "No dialogue found (no character name followed by a spoken line)",
            "Put each character name in CAPITALS on its own line, with the speech on the next line"))

    scene_headings = [line for line in lines if is_scene_heading(line)]
    if len(scene_headings) == 0:
        errors.append(make_error(
            None, "CRITICAL",
            "No scene headings (no line starting with INT. or EXT.)",
            "Start every scene with a heading such as INT. KITCHEN - DAY"))

    return errors


def get_speech(lines, cue_index):
    speech = []
    for line in lines[cue_index + 1:]:
        if line.strip() == "" or is_scene_heading(line):
            break
        speech.append(line)
    return speech


def find_moderate_errors(lines):
    """Apply all five MODERATE rules."""
    errors = []

    for i, line in enumerate(lines):
        line_number = i + 1

        if is_scene_heading(line) and not heading_has_time(line):
            errors.append(make_error(
                line_number, "MODERATE",
                f"Scene heading has no time of day: {line.strip()}",
                "Add DAY, NIGHT or similar, for example INT. KITCHEN - DAY"))

        if is_character_cue(line):
            speech = get_speech(lines, i)
            if len(speech) == 0:
                errors.append(make_error(
                    line_number, "MODERATE",
                    f"{line.strip()} has no spoken line",
                    "Write the speech on the line right under the name, or remove the name"))
            else:
                speech_words = sum([len(speech_line.split()) for speech_line in speech])
                if speech_words > MAX_SPEECH_WORDS:
                    errors.append(make_error(
                        line_number, "MODERATE",
                        f"Speech runs over {MAX_SPEECH_WORDS} words ({line.strip()} speaks {speech_words} words)",
                        "Break the speech into shorter parts with action lines or another character's reply"))

    errors.extend(find_ending_errors(lines))
    errors.extend(find_name_errors(lines))
    return errors


def has_ending_marker(non_blank_lines):
    last_lines = non_blank_lines[-5:]
    found = [line for line in last_lines if is_ending_marker(line)]
    return len(found) > 0


def find_ending_errors(lines):
    errors = []
    non_blank = [line for line in lines if line.strip() != ""]
    if len(non_blank) > 0 and not has_ending_marker(non_blank):
        errors.append(make_error(
            None, "MODERATE",
            "No ending marker (no FADE OUT, THE END or similar near the end)",
            "Finish the script with a line such as FADE OUT. or THE END"))
    return errors


def get_character_names(lines):
    names = {}
    for i, line in enumerate(lines):
        if is_character_cue(line):
            name = line.split("(")[0].strip()
            if name != "" and name not in names:
                names[name] = i + 1
    return names


def names_look_alike(first, second):
    if first == second or len(first) < 3 or len(second) < 3:
        return False

    if len(first) == len(second):
        different_places = 0
        for i in range(len(first)):
            if first[i] != second[i]:
                different_places = different_places + 1
        return different_places == 1

    if abs(len(first) - len(second)) == 1:
        if len(first) > len(second):
            longer, shorter = first, second
        else:
            longer, shorter = second, first
        for i in range(len(longer)):
            if longer[:i] + longer[i + 1:] == shorter:
                return True

    return False


def find_name_errors(lines):
    errors = []
    names = get_character_names(lines)
    name_list = list(names)
    for i in range(len(name_list)):
        for j in range(i + 1, len(name_list)):
            earlier = name_list[i]
            later = name_list[j]
            if names_look_alike(earlier, later):
                errors.append(make_error(
                    names[later], "MODERATE",
                    f"Name {later} looks like a different spelling of {earlier} (first seen on line {names[earlier]})",
                    "Use one spelling for each character. If they are two different people, give them names that look less alike"))
    return errors


def find_repeated_word_errors(lines):
    errors = []
    for i, line in enumerate(lines):
        tokens = line.lower().split()
        for a, b in zip(tokens, tokens[1:]):
            if a != b:
                continue
            clean = a.strip(".,;:!?\"'()[]-")
            if clean.isalpha():
                errors.append(make_error(
                    i + 1, "MINOR",
                    f'Repeated word "{a} {b}"',
                    "Remove the duplicate word"))
                break
    return errors


def find_extra_space_errors(lines):
    errors = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if "  " in stripped:
            errors.append(make_error(
                i + 1, "MINOR",
                "Extra spaces in this line",
                "Use a single space between words"))
    return errors


def find_lowercase_start_errors(lines):
    errors = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped == "":
            continue
        if is_scene_heading(line) or is_ending_marker(line):
            continue
        if stripped.startswith("("):
            continue
        first = stripped[0]
        if first.isalpha() and first.islower():
            preview = stripped[:30] + ("..." if len(stripped) > 30 else "")
            errors.append(make_error(
                i + 1, "MINOR",
                f'Line starts in lowercase: "{preview}"',
                "Start the line with a capital letter"))
    return errors


def find_minor_errors(lines):
    errors = []
    errors.extend(find_repeated_word_errors(lines))
    errors.extend(find_extra_space_errors(lines))
    errors.extend(find_lowercase_start_errors(lines))
    return errors


def find_errors(lines):
    """Run every error rule and return one list of errors. All 11 rules are in."""
    errors = []
    errors.extend(find_critical_errors(lines))
    errors.extend(find_moderate_errors(lines))
    errors.extend(find_minor_errors(lines))
    return errors


def print_errors(errors):
    """Print error counts and each error with its fix.
    Severity tags are colour-coded: red CRITICAL, yellow MODERATE, cyan MINOR."""
    critical = len([e for e in errors if e["severity"] == "CRITICAL"])
    moderate = len([e for e in errors if e["severity"] == "MODERATE"])
    minor    = len([e for e in errors if e["severity"] == "MINOR"])

    print("")
    print(f"Errors found: {COLOUR_CRITICAL}{critical} CRITICAL{RESET}, "
          f"{COLOUR_MODERATE}{moderate} MODERATE{RESET}, "
          f"{COLOUR_MINOR}{minor} MINOR{RESET}")
    if len(errors) == 0:
        print("  No errors found.")
    for error in errors:
        colour = SEVERITY_COLOURS.get(error["severity"], "")
        where = "Script" if error["line"] is None else f"Line {error['line']}"
        print(f"  {colour}[{error['severity']}]{RESET} {where}: {error['message']}")
        print(f"      Fix: {error['fix']}")


def rating_tier(score):
    """Turn a score into a rating tier. Tighter than v1 so EXCELLENT and
    PERFECT are hard to reach (see PRD v2)."""
    if score <= 39:
        return "POOR"
    elif score <= 59:
        return "AVERAGE"
    elif score <= 74:
        return "GOOD"
    elif score <= 89:
        return "EXCELLENT"
    else:
        return "PERFECT"


def calculate_score(errors):
    """Apply the PRD penalty formula and return (score, tier).

    Formula: max(0, 100 - 20*C - min(5*M, 30) - min(m, 10))
    C = CRITICAL count (no cap)
    M = MODERATE count (loss capped at 30)
    m = MINOR count (loss capped at 10)
    """
    critical = len([e for e in errors if e["severity"] == "CRITICAL"])
    moderate = len([e for e in errors if e["severity"] == "MODERATE"])
    minor    = len([e for e in errors if e["severity"] == "MINOR"])

    loss_critical = 20 * critical
    loss_moderate = min(5 * moderate, 30)
    loss_minor    = min(1 * minor, 10)

    score = max(0, 100 - loss_critical - loss_moderate - loss_minor)
    return score, rating_tier(score)


def main():
    path = input("Type the script file name (example: sample_scripts/broken_short.txt): ").strip()
    text = load_script(path)
    if text is None:
        return
    print(f"Loaded: {path}")
    print(f"Lines: {len(text.splitlines())}")
    print(f"Words: {len(text.split())}")

    words = clean_and_split(text)
    print(f"Clean words: {len(words)}")

    counts = count_genre_matches(words)
    percentages = calculate_percentages(counts)
    print_genre_report(counts, percentages)

    errors = find_errors(text.splitlines())
    print_errors(errors)

    score, tier = calculate_score(errors)
    tier_colour = TIER_COLOURS.get(tier, "")
    print("")
    print(f"Score: {score} / 100   Rating: {tier_colour}{tier}{RESET}")


if __name__ == "__main__":
    main()
    