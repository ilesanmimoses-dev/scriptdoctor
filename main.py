import unicodedata

# CRITICAL (3): too short, no dialogue, no scene headings
# MODERATE (5): incomplete heading, cue with no speech, very long speech,
#               no ending marker, inconsistent character name
# MINOR    (3): repeated word, extra spaces, sentence starts lowercase
#
# Step 12: parse_scenes() splits the script at each INT./EXT. heading.
# Step 13: detect_language() guesses the main language from common words.
# Step 14: count_speeches(), dialogue_ratio(), estimate_length().

HOOKED_LETTERS = {"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y"}
MIN_WORDS = 300
TIME_OF_DAY = ["DAY", "NIGHT", "MORNING", "AFTERNOON", "EVENING", "DAWN", "DUSK",
               "SUNRISE", "SUNSET", "MIDNIGHT", "NOON", "LATER", "CONTINUOUS"]
MAX_SPEECH_WORDS = 80
END_MARKERS = ["THE END", "FADE OUT", "FADE TO BLACK", "CUT TO BLACK"]

# Screenwriting rule of thumb: about 250 words per screenplay page,
# and about 1 page = 1 minute of screen time.
WORDS_PER_PAGE = 250

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

RESET            = "\033[0m"
COLOUR_CRITICAL  = "\033[91m"
COLOUR_MODERATE  = "\033[93m"
COLOUR_MINOR     = "\033[96m"
COLOUR_EXCELLENT = "\033[92m"
COLOUR_PERFECT   = "\033[1;92m"

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

LANGUAGE_COMMON_WORDS = {
    "English": ["the", "and", "you", "is", "are", "what", "this", "that", "have",
                "not", "with", "for", "but", "was", "were", "will", "from", "they"],
    "Pidgin": ["dey", "wan", "wetin", "abeg", "sabi", "don", "make", "shey",
               "waka", "chop", "gist", "biko", "oya", "nna", "wahala"],
    "Yoruba": ["ni", "ti", "mo", "wa", "fun", "pe", "ko", "se", "àti", "ṣe",
               "náà", "bi", "lati", "jẹ", "nígbà"],
    "Hausa": ["da", "ka", "ki", "ya", "ta", "ne", "ce", "mu", "su", "ina",
              "yaya", "yau", "gobe", "nan", "wannan"],
    "Igbo": ["nke", "ya", "anyị", "ha", "bụ", "dị", "ka", "maka", "ebe",
             "mgbe", "gị", "mụ", "nna", "nne", "ọ"],
}


def load_script(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"Sorry, I could not find '{path}'. Check the name and the folder.")
        return None


def clean_and_split(text):
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
    keyword_sets = {}
    for genre, languages in GENRE_KEYWORDS.items():
        genre_words = set()
        for language, keywords in languages.items():
            for keyword in keywords:
                genre_words.add(normalize_word(keyword))
        keyword_sets[genre] = genre_words
    return keyword_sets


def count_genre_matches(words):
    keyword_sets = build_keyword_sets()
    normalized_words = [normalize_word(word) for word in words]
    counts = {}
    for genre, keywords in keyword_sets.items():
        matches = [word for word in normalized_words if word in keywords]
        counts[genre] = len(matches)
    return counts


def calculate_percentages(counts):
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
    return len(line.strip().split()) >= 3


def looks_like_speech(line):
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
    errors = []
    errors.extend(find_critical_errors(lines))
    errors.extend(find_moderate_errors(lines))
    errors.extend(find_minor_errors(lines))
    return errors


def print_errors(errors):
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
    critical = len([e for e in errors if e["severity"] == "CRITICAL"])
    moderate = len([e for e in errors if e["severity"] == "MODERATE"])
    minor    = len([e for e in errors if e["severity"] == "MINOR"])

    loss_critical = 20 * critical
    loss_moderate = min(5 * moderate, 30)
    loss_minor    = min(1 * minor, 10)

    score = max(0, 100 - loss_critical - loss_moderate - loss_minor)
    return score, rating_tier(score)


def choose_comment(percentages, score):
    ranked = sorted(percentages.items(), key=percent_of, reverse=True)
    leader, lead_percent = ranked[0]
    second_percent = ranked[1][1] if len(ranked) > 1 else 0.0

    if score < 40:
        return ("Interesting: every great writer started rough. Fix the CRITICAL "
                "problems first and run the script again — you will see the score jump.")

    if lead_percent >= 40 and (lead_percent - second_percent) >= 15:
        fun_facts = {
            "Action": "Action scripts live on verbs — keep the chase moving.",
            "Comedy": "Comedy is the hardest genre to score; laughter is subjective.",
            "Romance": "Romance lives on small gestures, not big speeches.",
            "Emotional/Drama": "Drama works best when the quiet moments carry the weight.",
            "Horror": "Horror is about what you don't show as much as what you do.",
            "Fiction/Fantasy": "Fantasy needs its rules clear before the magic lands.",
            "Erotic": "Tension, not explicitness, is what makes this genre work.",
        }
        return f"Interesting: {leader} leads clearly here ({lead_percent:.1f}%). {fun_facts[leader]}"

    return ("Interesting: your script blends several genres, and most great films "
            "do exactly that!")


def parse_scenes(lines):
    scenes = []
    current = None

    for i, line in enumerate(lines):
        line_number = i + 1

        if is_scene_heading(line):
            if current is not None:
                scenes.append(current)

            heading_upper = line.strip().upper()

            if heading_upper.startswith("EXT."):
                interior = "EXT"
            elif heading_upper.startswith("INT."):
                interior = "INT"
            else:
                interior = "UNKNOWN"

            rest = heading_upper
            for prefix in ("INT./EXT.", "EXT./INT.", "INT.", "EXT."):
                if rest.startswith(prefix):
                    rest = rest[len(prefix):].strip()
                    break

            parts = rest.replace("–", "-").replace("—", "-").split("-")
            location_part = parts[0].strip() if parts else ""
            time_part = " - ".join(parts[1:]).strip() if len(parts) > 1 else ""

            time_found = "UNKNOWN"
            for word in time_part.split():
                clean_word = word.strip(".,()")
                if clean_word in TIME_OF_DAY:
                    time_found = clean_word
                    break
            if time_found == "UNKNOWN":
                for word in heading_upper.replace(".", " ").replace("-", " ").split():
                    clean_word = word.strip(".,()/")
                    if clean_word in TIME_OF_DAY:
                        time_found = clean_word
                        break

            location = location_part.strip(" .,-–—/").strip()
            if location == "":
                location = "UNKNOWN"

            current = {
                "location": location,
                "time": time_found,
                "interior": interior,
                "first_line": line_number,
                "lines": [],
                "word_count": 0,
            }
        else:
            if current is not None:
                current["lines"].append(line)
                current["word_count"] += len(line.split())

    if current is not None:
        scenes.append(current)

    return scenes


def detect_language(words):
    if len(words) < 10:
        return "Unknown"

    normalised = [normalize_word(w) for w in words]

    counts = {}
    for language, common in LANGUAGE_COMMON_WORDS.items():
        keyword_set = {normalize_word(w) for w in common}
        matches = [w for w in normalised if w in keyword_set]
        counts[language] = len(matches)

    total = sum(counts.values())
    if total < 5:
        return "Unknown"

    ranked = sorted(counts.items(), key=percent_of, reverse=True)
    leader, leader_count = ranked[0]
    second_count = ranked[1][1] if len(ranked) > 1 else 0

    if leader_count < 2 or leader_count < second_count * 2:
        return "Mixed"

    return leader


# ---- Step 14: character list, dialogue ratio, length estimate ------------

def count_speeches(lines):
    """Count how many speeches each character has and how many words each speaks.

    Returns a dict: {name: {"speeches": N, "words": M}}
    Sorted by speeches (biggest first) when read by the caller.
    """
    result = {}
    for i, line in enumerate(lines):
        if not is_character_cue(line):
            continue
        if looks_like_action_phrase(line):
            continue
        name = line.split("(")[0].strip()
        if name == "":
            continue
        speech = get_speech(lines, i)
        if len(speech) == 0:
            continue
        speech_words = sum(len(s.split()) for s in speech)
        if name not in result:
            result[name] = {"speeches": 0, "words": 0}
        result[name]["speeches"] += 1
        result[name]["words"] += speech_words
    return result


def dialogue_ratio(lines):
    """How much of the script is speech vs action (description).

    Returns {"dialogue_words": N, "action_words": M, "dialogue_pct": X}
    The percentage is dialogue words divided by total words, one decimal.
    """
    total_words = sum(len(line.split()) for line in lines)

    dialogue_words = 0
    for i, line in enumerate(lines):
        if not is_character_cue(line):
            continue
        if looks_like_action_phrase(line):
            continue
        speech = get_speech(lines, i)
        dialogue_words += sum(len(s.split()) for s in speech)

    action_words = max(0, total_words - dialogue_words)
    pct = round(dialogue_words / total_words * 100, 1) if total_words > 0 else 0.0
    return {"dialogue_words": dialogue_words, "action_words": action_words,
            "dialogue_pct": pct}


def estimate_length(words):
    """Estimate pages and screen minutes from word count.

    Rule of thumb: about 250 words per page, 1 page = 1 minute.
    Always an estimate, never a fact.
    """
    page_count = round(len(words) / WORDS_PER_PAGE, 1)
    minutes = round(page_count)
    return {"pages": page_count, "minutes": minutes}


# ---- Step 14: print helpers -----------------------------------------------

def print_characters(speech_counts):
    """Print the character list, sorted by how often each one speaks."""
    print("")
    print(f"Characters: {len(speech_counts)}")
    if len(speech_counts) == 0:
        print("  No speaking characters found.")
        return
    ranked = sorted(speech_counts.items(),
                    key=lambda pair: pair[1]["speeches"], reverse=True)
    for name, info in ranked:
        print(f"  {name:<20} {info['speeches']:>2} speeches   {info['words']} words")


def print_dialogue_ratio(ratio):
    """Print the dialogue vs action split."""
    print("")
    print(f"Dialogue vs action: {ratio['dialogue_pct']}% dialogue, "
          f"{round(100 - ratio['dialogue_pct'], 1)}% action")
    print(f"  Dialogue words: {ratio['dialogue_words']}")
    print(f"  Action words:   {ratio['action_words']}")


def print_length_estimate(estimate):
    """Print the estimated pages and screen minutes. Always labelled estimate."""
    print("")
    print(f"Estimated length: ~{estimate['pages']} pages  (~{estimate['minutes']} minutes)")


def print_language(language):
    print("")
    print(f"Language: {language}")


def print_scene_list(scenes):
    print("")
    print(f"Scenes found: {len(scenes)}")
    if len(scenes) == 0:
        print("  No scene headings (INT. or EXT.) were found.")
        return
    for n, scene in enumerate(scenes, start=1):
        print(f"  Scene {n}: {scene['interior']}. {scene['location']} - {scene['time']} "
              f"(line {scene['first_line']}, {scene['word_count']} words)")


def print_report(counts, percentages, errors, score, tier, comment,
                 scenes, language, speech_counts, ratio, estimate):
    """Print the full report in the PRD's sample layout."""
    print("=" * 47)
    print("SCRIPTSCOPE REPORT".center(47))
    print("=" * 47)

    print_language(language)

    print_genre_report(counts, percentages)

    print_scene_list(scenes)

    print_characters(speech_counts)
    print_dialogue_ratio(ratio)
    print_length_estimate(estimate)

    print_errors(errors)

    tier_colour = TIER_COLOURS.get(tier, "")
    print("")
    print(f"Score: {score} / 100   Rating: {tier_colour}{tier}{RESET}")

    print("-" * 47)
    print(comment)


def main():
    path = input("Type the script file name (example: sample_scripts/broken_short.txt): ").strip()
    text = load_script(path)
    if text is None:
        return

    lines = text.splitlines()
    words = clean_and_split(text)
    counts = count_genre_matches(words)
    percentages = calculate_percentages(counts)

    errors = find_errors(lines)
    score, tier = calculate_score(errors)
    comment = choose_comment(percentages, score)
    scenes = parse_scenes(lines)
    language = detect_language(words)

    speech_counts = count_speeches(lines)
    ratio = dialogue_ratio(lines)
    estimate = estimate_length(words)

    print_report(counts, percentages, errors, score, tier, comment,
                 scenes, language, speech_counts, ratio, estimate)


if __name__ == "__main__":
    main()