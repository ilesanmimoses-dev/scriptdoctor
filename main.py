import unicodedata

# CRITICAL (3): too short, no dialogue, no scene headings
# MODERATE (5): incomplete heading, cue with no speech, very long speech,
#               no ending marker, inconsistent character name
# MINOR    (3): repeated word, extra spaces, sentence starts lowercase
#
# Step 12: parse_scenes()             - split script at INT./EXT. headings
# Step 13: detect_language()          - guess main language
# Step 14: count_speeches(), dialogue_ratio(), estimate_length()
# Step 15: explain_simply()           - plain-words explanation (facts only)
# Step 16: find_props_and_costumes()  - named items only, never invented
# Step 17a: ask_yes_no(), build_schedule(), print_schedule()
# Step 17b: ask_schedule_preferences() - user chooses pages/day or scenes/day

HOOKED_LETTERS = {"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y"}
MIN_WORDS = 300
TIME_OF_DAY = ["DAY", "NIGHT", "MORNING", "AFTERNOON", "EVENING", "DAWN", "DUSK",
               "SUNRISE", "SUNSET", "MIDNIGHT", "NOON", "LATER", "CONTINUOUS"]
MAX_SPEECH_WORDS = 80
END_MARKERS = ["THE END", "FADE OUT", "FADE TO BLACK", "CUT TO BLACK"]
WORDS_PER_PAGE = 250

PROPS = [
    "gun", "candle", "chain", "phone",
    "knife", "letter", "book", "bag", "money", "key", "ring", "mirror",
    "bottle", "cup", "chair", "table", "door", "window", "car", "bicycle",
    "umbrella", "clock", "photograph",
    "calabash", "kola", "pot", "mat", "broom",
]

COSTUMES = [
    "uniform", "dress", "suit",
    "shirt", "trousers", "hat", "shoe", "coat", "jacket",
    "gown", "skirt", "tie", "glasses", "watch", "scarf", "boots",
    "veil", "robe", "apron", "helmet",
    "wrapper", "gele", "agbada", "kaftan", "babariga",
]

GENRE_KEYWORDS = {
    "Action": {"English": ["gun", "guns", "gunfire", "explosion", "explode", "fight",
                           "chase", "shoot", "battle", "attack", "escape", "crash",
                           "punch", "kill", "weapon", "war"],
               "Pidgin": [], "Yoruba": ["ìjà", "ìbọn", "ìkọlù", "jàǹbá"],
               "Hausa": ["yaƙi", "bindiga", "fashewa", "harbi", "faɗa"],
               "Igbo": ["agha", "ọgụ", "égbè"]},
    "Comedy": {"English": ["laugh", "laughs", "laughing", "joke", "jokes", "funny",
                           "silly", "prank", "hilarious", "giggle", "clown", "goofy",
                           "ridiculous"],
               "Pidgin": [], "Yoruba": ["ẹ̀rín", "awada"],
               "Hausa": ["dariya", "barkwanci"], "Igbo": ["ọchị"]},
    "Romance": {"English": ["love", "loved", "kiss", "kisses", "romantic", "romance",
                            "wedding", "darling", "sweetheart", "beloved", "embrace"],
                "Pidgin": [], "Yoruba": ["ìfẹ́", "ìfẹnukonu", "ìgbéyàwó", "fẹ́ràn"],
                "Hausa": ["soyayya", "aure", "sumba", "ƙauna", "masoyi"],
                "Igbo": ["ịhụnanya", "agbamakwụkwọ"]},
    "Emotional/Drama": {"English": ["cry", "cries", "crying", "tears", "sad", "grief",
                                    "pain", "loss", "heartbreak", "lonely", "forgive",
                                    "sorrow", "mourn", "regret"],
                        "Pidgin": ["wahala"],
                        "Yoruba": ["ẹkún", "ìbànújẹ́", "ìrora", "omijé", "ẹ̀dùn"],
                        "Hausa": ["kuka", "hawaye", "makoki", "nadama"],
                        "Igbo": ["mwute", "mgbu", "nchegbu"]},
    "Horror": {"English": ["blood", "scream", "screams", "ghost", "monster", "haunted",
                           "nightmare", "creepy", "demon", "terror", "corpse",
                           "graveyard", "fear"],
               "Pidgin": ["juju", "witchcraft"],
               "Yoruba": ["òkú", "ẹ̀jẹ̀", "iwin", "òkùnkùn", "ìbẹ̀rù"],
               "Hausa": ["duhu", "aljani", "fatalwa", "jini", "tsoro", "gawa"],
               "Igbo": ["mmụọ", "ọchịchịrị", "ọbara", "ụjọ", "ogbanje"]},
    "Fiction/Fantasy": {"English": ["magic", "dragon", "wizard", "kingdom", "spell",
                                    "portal", "quest", "prophecy", "sword", "castle",
                                    "legend", "alien", "robot", "spaceship"],
                        "Pidgin": [], "Yoruba": ["idán", "oṣó", "àsọtẹ́lẹ̀"],
                        "Hausa": ["sihiri", "tatsuniya"], "Igbo": ["amụma"]},
    "Erotic": {"English": ["desire", "passion", "seduce", "temptation", "intimate",
                           "sensual", "longing"],
               "Pidgin": [], "Yoruba": [], "Hausa": [], "Igbo": []},
}

RESET            = "\033[0m"
COLOUR_CRITICAL  = "\033[91m"
COLOUR_MODERATE  = "\033[93m"
COLOUR_MINOR     = "\033[96m"
COLOUR_EXCELLENT = "\033[92m"
COLOUR_PERFECT   = "\033[1;92m"

SEVERITY_COLOURS = {"CRITICAL": COLOUR_CRITICAL, "MODERATE": COLOUR_MODERATE, "MINOR": COLOUR_MINOR}
TIER_COLOURS = {"POOR": COLOUR_CRITICAL, "AVERAGE": COLOUR_MODERATE, "GOOD": COLOUR_MINOR,
                "EXCELLENT": COLOUR_EXCELLENT, "PERFECT": COLOUR_PERFECT}

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
            return file.read()
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
    words = []
    for piece in "".join(kept).split():
        piece = piece.strip("'")
        if piece:
            words.append(piece)
    return words


def normalize_word(word):
    word = word.lower()
    for hooked, plain in HOOKED_LETTERS.items():
        word = word.replace(hooked, plain)
    decomposed = unicodedata.normalize("NFD", word)
    return "".join(ch for ch in decomposed if unicodedata.category(ch) != "Mn")


def singular_fallback(word):
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def build_keyword_sets():
    return {genre: {normalize_word(k) for kws in langs.values() for k in kws}
            for genre, langs in GENRE_KEYWORDS.items()}


def count_genre_matches(words):
    keyword_sets = build_keyword_sets()
    normalized = [normalize_word(w) for w in words]
    return {genre: len([w for w in normalized if w in kws])
            for genre, kws in keyword_sets.items()}


def calculate_percentages(counts):
    total = sum(counts.values())
    if total == 0:
        return {genre: 0.0 for genre in counts}
    tenths, leftovers = {}, {}
    for genre in counts:
        tenths[genre] = counts[genre] * 1000 // total
        leftovers[genre] = counts[genre] * 1000 % total
    missing = 1000 - sum(tenths.values())
    for genre in sorted(leftovers, key=leftovers.get, reverse=True)[:missing]:
        tenths[genre] += 1
    return {genre: tenths[genre] / 10 for genre in tenths}


def percent_of(pair):
    return pair[1]


def print_genre_report(counts, percentages):
    print("")
    print("Genres")
    for genre, percent in sorted(percentages.items(), key=percent_of, reverse=True):
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
    return any(word in TIME_OF_DAY for word in cleaned.split())


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
        if not is_character_cue(lines[i]):
            continue
        if looks_like_action_phrase(lines[i]):
            continue
        if looks_like_speech(lines[i + 1]):
            return True
    return False


def make_error(line_number, severity, message, fix):
    return {"line": line_number, "severity": severity, "message": message, "fix": fix}


def find_critical_errors(lines):
    errors = []
    word_count = sum(len(line.split()) for line in lines)
    if word_count < MIN_WORDS:
        errors.append(make_error(None, "CRITICAL",
            f"Too short ({word_count} words, the minimum is {MIN_WORDS})",
            "Write more scenes and dialogue until the script passes 300 words"))
    if not has_dialogue(lines):
        errors.append(make_error(None, "CRITICAL",
            "No dialogue found (no character name followed by a spoken line)",
            "Put each character name in CAPITALS on its own line, with the speech on the next line"))
    if not any(is_scene_heading(line) for line in lines):
        errors.append(make_error(None, "CRITICAL",
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
        ln = i + 1
        if is_scene_heading(line) and not heading_has_time(line):
            errors.append(make_error(ln, "MODERATE",
                f"Scene heading has no time of day: {line.strip()}",
                "Add DAY, NIGHT or similar, for example INT. KITCHEN - DAY"))
        if is_character_cue(line):
            speech = get_speech(lines, i)
            if len(speech) == 0:
                errors.append(make_error(ln, "MODERATE",
                    f"{line.strip()} has no spoken line",
                    "Write the speech on the line right under the name, or remove the name"))
            else:
                sw = sum(len(s.split()) for s in speech)
                if sw > MAX_SPEECH_WORDS:
                    errors.append(make_error(ln, "MODERATE",
                        f"Speech runs over {MAX_SPEECH_WORDS} words ({line.strip()} speaks {sw} words)",
                        "Break the speech into shorter parts with action lines or another character's reply"))
    errors.extend(find_ending_errors(lines))
    errors.extend(find_name_errors(lines))
    return errors


def has_ending_marker(non_blank_lines):
    return any(is_ending_marker(line) for line in non_blank_lines[-5:])


def find_ending_errors(lines):
    non_blank = [l for l in lines if l.strip() != ""]
    if len(non_blank) > 0 and not has_ending_marker(non_blank):
        return [make_error(None, "MODERATE",
            "No ending marker (no FADE OUT, THE END or similar near the end)",
            "Finish the script with a line such as FADE OUT. or THE END")]
    return []


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
        return sum(1 for i in range(len(first)) if first[i] != second[i]) == 1
    if abs(len(first) - len(second)) == 1:
        longer, shorter = (first, second) if len(first) > len(second) else (second, first)
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
            earlier, later = name_list[i], name_list[j]
            if names_look_alike(earlier, later):
                errors.append(make_error(names[later], "MODERATE",
                    f"Name {later} looks like a different spelling of {earlier} (first seen on line {names[earlier]})",
                    "Use one spelling for each character. If they are two different people, give them names that look less alike"))
    return errors


def find_repeated_word_errors(lines):
    errors = []
    for i, line in enumerate(lines):
        tokens = line.lower().split()
        for a, b in zip(tokens, tokens[1:]):
            if a == b and a.strip(".,;:!?\"'()[]-").isalpha():
                errors.append(make_error(i + 1, "MINOR",
                    f'Repeated word "{a} {b}"', "Remove the duplicate word"))
                break
    return errors


def find_extra_space_errors(lines):
    return [make_error(i + 1, "MINOR", "Extra spaces in this line",
                       "Use a single space between words")
            for i, line in enumerate(lines) if "  " in line.strip()]


def find_lowercase_start_errors(lines):
    errors = []
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped == "":
            continue
        if is_scene_heading(line) or is_ending_marker(line) or stripped.startswith("("):
            continue
        first = stripped[0]
        if first.isalpha() and first.islower():
            preview = stripped[:30] + ("..." if len(stripped) > 30 else "")
            errors.append(make_error(i + 1, "MINOR",
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
    c = len([e for e in errors if e["severity"] == "CRITICAL"])
    m = len([e for e in errors if e["severity"] == "MODERATE"])
    n = len([e for e in errors if e["severity"] == "MINOR"])
    print("")
    print(f"Errors found: {COLOUR_CRITICAL}{c} CRITICAL{RESET}, "
          f"{COLOUR_MODERATE}{m} MODERATE{RESET}, {COLOUR_MINOR}{n} MINOR{RESET}")
    if not errors:
        print("  No errors found.")
    for error in errors:
        colour = SEVERITY_COLOURS.get(error["severity"], "")
        where = "Script" if error["line"] is None else f"Line {error['line']}"
        print(f"  {colour}[{error['severity']}]{RESET} {where}: {error['message']}")
        print(f"      Fix: {error['fix']}")


def rating_tier(score):
    if score <= 39:   return "POOR"
    if score <= 59:   return "AVERAGE"
    if score <= 74:   return "GOOD"
    if score <= 89:   return "EXCELLENT"
    return "PERFECT"


def calculate_score(errors):
    c = len([e for e in errors if e["severity"] == "CRITICAL"])
    m = len([e for e in errors if e["severity"] == "MODERATE"])
    n = len([e for e in errors if e["severity"] == "MINOR"])
    loss = 20 * c + min(5 * m, 30) + min(1 * n, 10)
    score = max(0, 100 - loss)
    return score, rating_tier(score)


def choose_comment(percentages, score):
    ranked = sorted(percentages.items(), key=percent_of, reverse=True)
    leader, lead = ranked[0]
    second = ranked[1][1] if len(ranked) > 1 else 0.0
    if score < 40:
        return ("Interesting: every great writer started rough. Fix the CRITICAL "
                "problems first and run the script again — you will see the score jump.")
    if lead >= 40 and (lead - second) >= 15:
        facts = {"Action": "Action scripts live on verbs — keep the chase moving.",
                 "Comedy": "Comedy is the hardest genre to score; laughter is subjective.",
                 "Romance": "Romance lives on small gestures, not big speeches.",
                 "Emotional/Drama": "Drama works best when the quiet moments carry the weight.",
                 "Horror": "Horror is about what you don't show as much as what you do.",
                 "Fiction/Fantasy": "Fantasy needs its rules clear before the magic lands.",
                 "Erotic": "Tension, not explicitness, is what makes this genre work."}
        return f"Interesting: {leader} leads clearly here ({lead:.1f}%). {facts[leader]}"
    return ("Interesting: your script blends several genres, and most great films "
            "do exactly that!")


def parse_scenes(lines):
    scenes = []
    current = None
    for i, line in enumerate(lines):
        ln = i + 1
        if is_scene_heading(line):
            if current is not None:
                scenes.append(current)
            h = line.strip().upper()
            if h.startswith("EXT."):   interior = "EXT"
            elif h.startswith("INT."): interior = "INT"
            else:                      interior = "UNKNOWN"
            rest = h
            for prefix in ("INT./EXT.", "EXT./INT.", "INT.", "EXT."):
                if rest.startswith(prefix):
                    rest = rest[len(prefix):].strip()
                    break
            parts = rest.replace("–", "-").replace("—", "-").split("-")
            loc_part = parts[0].strip() if parts else ""
            time_part = " - ".join(parts[1:]).strip() if len(parts) > 1 else ""
            time_found = "UNKNOWN"
            for word in time_part.split():
                cw = word.strip(".,()")
                if cw in TIME_OF_DAY:
                    time_found = cw; break
            if time_found == "UNKNOWN":
                for word in h.replace(".", " ").replace("-", " ").split():
                    cw = word.strip(".,()/")
                    if cw in TIME_OF_DAY:
                        time_found = cw; break
            location = loc_part.strip(" .,-–—/").strip() or "UNKNOWN"
            current = {"location": location, "time": time_found, "interior": interior,
                       "first_line": ln, "lines": [], "word_count": 0}
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
    norm = [normalize_word(w) for w in words]
    counts = {}
    for lang, common in LANGUAGE_COMMON_WORDS.items():
        ks = {normalize_word(w) for w in common}
        counts[lang] = len([w for w in norm if w in ks])
    if sum(counts.values()) < 5:
        return "Unknown"
    ranked = sorted(counts.items(), key=percent_of, reverse=True)
    leader, lc = ranked[0]
    sc = ranked[1][1] if len(ranked) > 1 else 0
    if lc < 2 or lc < sc * 2:
        return "Mixed"
    return leader


def count_speeches(lines):
    result = {}
    for i, line in enumerate(lines):
        if not is_character_cue(line) or looks_like_action_phrase(line):
            continue
        name = line.split("(")[0].strip()
        if name == "":
            continue
        speech = get_speech(lines, i)
        if len(speech) == 0:
            continue
        sw = sum(len(s.split()) for s in speech)
        if name not in result:
            result[name] = {"speeches": 0, "words": 0}
        result[name]["speeches"] += 1
        result[name]["words"] += sw
    return result


def dialogue_ratio(lines):
    total = sum(len(line.split()) for line in lines)
    dl = 0
    for i, line in enumerate(lines):
        if not is_character_cue(line) or looks_like_action_phrase(line):
            continue
        dl += sum(len(s.split()) for s in get_speech(lines, i))
    act = max(0, total - dl)
    pct = round(dl / total * 100, 1) if total > 0 else 0.0
    return {"dialogue_words": dl, "action_words": act, "dialogue_pct": pct}


def estimate_length(words):
    pages = round(len(words) / WORDS_PER_PAGE, 1)
    return {"pages": pages, "minutes": round(pages)}


def explain_simply(words, language, scenes, speech_counts, percentages, estimate):
    sentences = []
    wt = len(words)
    if wt < MIN_WORDS:
        sentences.append(f"This is a short {language} script with only {wt} words.")
    elif wt < 1000:
        sentences.append(f"This is a {language} script with about {wt} words.")
    else:
        sentences.append(f"This is a longer {language} script with about {wt} words.")

    n = len(scenes)
    if n == 0:
        sentences.append("No scene headings were found, so the place is not clear.")
    elif n == 1:
        loc = scenes[0]["location"]
        s = "The whole story happens in one scene"
        if loc != "UNKNOWN":
            s += f" ({loc}, {scenes[0]['time']})"
        sentences.append(s + ".")
    else:
        locs = []
        for sc in scenes:
            if sc["location"] != "UNKNOWN" and sc["location"] not in locs:
                locs.append(sc["location"])
        if not locs:
            sentences.append(f"The script has {n} scenes, but their locations are not named.")
        elif len(locs) <= 3:
            joined = ", ".join(locs[:-1]) + " and " + locs[-1] if len(locs) > 1 else locs[0]
            sentences.append(f"The script has {n} scenes, mostly in {joined}.")
        else:
            sentences.append(f"The script has {n} scenes, including {', '.join(locs[:3])} and others.")

    if not speech_counts:
        sentences.append("No speaking characters were found.")
    else:
        ranked = sorted(speech_counts.items(), key=lambda p: p[1]["speeches"], reverse=True)
        names = [nm for nm, _ in ranked]
        lead, info = ranked[0]
        if len(names) == 1:
            sentences.append(f"The only speaking character is {names[0]}.")
        elif len(names) <= 3:
            joined = ", ".join(names[:-1]) + " and " + names[-1]
            sentences.append(f"The speaking characters are {joined}. "
                             f"{lead} speaks the most ({info['speeches']} times).")
        else:
            sentences.append(f"The main characters are {', '.join(names[:3])}, and others. "
                             f"{lead} speaks the most ({info['speeches']} times).")

    ranked_g = sorted(percentages.items(), key=percent_of, reverse=True)
    lg, lp = ranked_g[0]
    if lp == 0.0:
        sentences.append("No genre keywords were found, so the mood is not clear.")
    elif lp >= 60:
        sentences.append(f"The mood clearly leans {lg} ({lp:.1f}%).")
    elif lp >= 30:
        sentences.append(f"The mood leans {lg} ({lp:.1f}%), with other genres mixed in.")
    else:
        sentences.append(f"The genres are spread out, with {lg} slightly ahead ({lp:.1f}%).")

    sentences.append(f"Estimated length: about {estimate['pages']} pages "
                     f"(about {estimate['minutes']} minutes of screen time).")
    return sentences


def find_props_and_costumes(scenes):
    props_set = {normalize_word(w) for w in PROPS}
    costumes_set = {normalize_word(w) for w in COSTUMES}
    found_props = {}
    found_costumes = {}
    for n, scene in enumerate(scenes, start=1):
        body_words = clean_and_split("\n".join(scene["lines"]))
        for raw in body_words:
            word = normalize_word(raw)
            candidate = singular_fallback(word)
            for test_word in (word, candidate):
                if test_word in props_set:
                    found_props.setdefault(test_word, []).append(n)
                    break
                if test_word in costumes_set:
                    found_costumes.setdefault(test_word, []).append(n)
                    break
    for item in found_props:
        found_props[item] = sorted(set(found_props[item]))
    for item in found_costumes:
        found_costumes[item] = sorted(set(found_costumes[item]))
    return {"props": found_props, "costumes": found_costumes}


# ---- Step 17a/17b: schedule -------------------------------------------------

def ask_yes_no(question):
    """Ask a yes/no question. True for 'y' or 'yes', False for anything else."""
    answer = input(question + " (yes/no): ").strip().lower()
    return answer in ("y", "yes")


def ask_schedule_preferences():
    """Ask the user how to measure pace and how many per day.

    Returns (unit, number) where unit is 'pages' or 'scenes'.
    Defaults: 5 pages per day, or 4 scenes per day.
    """
    print("")
    print("How do you want to measure pace?")
    print("  1) Pages per day (standard)")
    print("  2) Scenes per day")
    choice = input("Choose [1]: ").strip()

    if choice == "2":
        unit = "scenes"
        default_number = 4.0
    else:
        unit = "pages"
        default_number = 5.0

    prompt = f"{unit.capitalize()} per day (press Enter for {int(default_number)}): "
    raw = input(prompt).strip()
    if raw == "":
        return unit, default_number

    try:
        number = float(raw)
        if number > 0:
            return unit, number
    except ValueError:
        pass

    print(f"Not a valid number. Using {int(default_number)} {unit} per day.")
    return unit, default_number


def build_schedule(scenes, unit="pages", number_per_day=5.0):
    """Group scenes by location and estimate days.

    unit = 'pages': days = pages_at_location / number_per_day
    unit = 'scenes': days = scenes_at_location / number_per_day
    Everything is an ESTIMATE, never a production plan.
    """
    if not scenes:
        return {"by_location": [], "total_days": 0.0,
                "unit": unit, "number": number_per_day}

    groups = {}
    for scene in scenes:
        loc = scene["location"]
        if loc not in groups:
            groups[loc] = {"scenes": 0, "words": 0}
        groups[loc]["scenes"] += 1
        groups[loc]["words"] += scene["word_count"]

    by_location = []
    total_days = 0.0
    for loc, info in groups.items():
        pages = round(info["words"] / WORDS_PER_PAGE, 1)
        if unit == "scenes":
            days = round(info["scenes"] / number_per_day, 1) if number_per_day > 0 else 0.0
        else:
            days = round(pages / number_per_day, 1) if number_per_day > 0 else 0.0
        by_location.append({
            "location": loc,
            "scenes": info["scenes"],
            "words": info["words"],
            "pages": pages,
            "days": days,
        })
        total_days += days

    by_location.sort(key=lambda x: x["days"], reverse=True)
    return {"by_location": by_location,
            "total_days": round(total_days, 1),
            "unit": unit, "number": number_per_day}


def print_schedule(schedule):
    """Print the schedule estimate. Always labelled as an estimate."""
    unit = schedule["unit"]
    number = schedule["number"]
    print("")
    print(f"Schedule estimate (rough guide only, based on {number:g} {unit} per day):")
    if not schedule["by_location"]:
        print("  No scenes to schedule.")
        return
    for entry in schedule["by_location"]:
        scene_word = "scene" if entry["scenes"] == 1 else "scenes"
        if unit == "scenes":
            print(f"  {entry['location']:<18} {entry['scenes']} {scene_word}   "
                  f"~{entry['days']} days")
        else:
            print(f"  {entry['location']:<18} {entry['scenes']} {scene_word}   "
                  f"{entry['words']} words   ~{entry['pages']} pages   ~{entry['days']} days")
    print("")
    day_word = "day" if schedule["total_days"] == 1.0 else "days"
    print(f"  Total: ~{schedule['total_days']} {day_word}")


# ---- Print helpers --------------------------------------------------------

def print_explanation(sentences):
    print("")
    print("In plain words:")
    for s in sentences:
        print(f"  {s}")


def print_language(language):
    print("")
    print(f"Language: {language}")


def print_scene_list(scenes):
    print("")
    print(f"Scenes found: {len(scenes)}")
    if not scenes:
        print("  No scene headings (INT. or EXT.) were found.")
        return
    for n, sc in enumerate(scenes, start=1):
        print(f"  Scene {n}: {sc['interior']}. {sc['location']} - {sc['time']} "
              f"(line {sc['first_line']}, {sc['word_count']} words)")


def print_characters(speech_counts):
    print("")
    print(f"Characters: {len(speech_counts)}")
    if not speech_counts:
        print("  No speaking characters found.")
        return
    ranked = sorted(speech_counts.items(), key=lambda p: p[1]["speeches"], reverse=True)
    for name, info in ranked:
        print(f"  {name:<20} {info['speeches']:>2} speeches   {info['words']} words")


def print_dialogue_ratio(ratio):
    print("")
    print(f"Dialogue vs action: {ratio['dialogue_pct']}% dialogue, "
          f"{round(100 - ratio['dialogue_pct'], 1)}% action")
    print(f"  Dialogue words: {ratio['dialogue_words']}")
    print(f"  Action words:   {ratio['action_words']}")


def print_length_estimate(estimate):
    print("")
    print(f"Estimated length: ~{estimate['pages']} pages  (~{estimate['minutes']} minutes)")


def print_props_and_costumes(items):
    props = items["props"]
    costumes = items["costumes"]

    print("")
    print(f"Props named ({len(props)}):")
    if not props:
        print("  No props from the word list were named in the script.")
    else:
        for name in sorted(props):
            scene_list = ", ".join(str(s) for s in props[name])
            plural = "s" if len(props[name]) > 1 else ""
            print(f"  {name:<20} scene{plural} {scene_list}")

    print("")
    print(f"Costumes named ({len(costumes)}):")
    if not costumes:
        print("  No costumes from the word list were named in the script.")
    else:
        for name in sorted(costumes):
            scene_list = ", ".join(str(s) for s in costumes[name])
            plural = "s" if len(costumes[name]) > 1 else ""
            print(f"  {name:<20} scene{plural} {scene_list}")


def print_report(counts, percentages, errors, score, tier, comment,
                 scenes, language, speech_counts, ratio, estimate, explanation,
                 items):
    print("=" * 47)
    print("SCRIPTSCOPE REPORT".center(47))
    print("=" * 47)
    print_language(language)
    print_genre_report(counts, percentages)
    print_scene_list(scenes)
    print_characters(speech_counts)
    print_dialogue_ratio(ratio)
    print_length_estimate(estimate)
    print_explanation(explanation)
    print_props_and_costumes(items)
    print_errors(errors)
    tc = TIER_COLOURS.get(tier, "")
    print("")
    print(f"Score: {score} / 100   Rating: {tc}{tier}{RESET}")
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
    explanation = explain_simply(words, language, scenes, speech_counts, percentages, estimate)
    items = find_props_and_costumes(scenes)
    print_report(counts, percentages, errors, score, tier, comment,
                 scenes, language, speech_counts, ratio, estimate, explanation, items)

    if ask_yes_no("Would you also like a schedule estimate?"):
        unit, number = ask_schedule_preferences()
        schedule = build_schedule(scenes, unit=unit, number_per_day=number)
        print_schedule(schedule)


if __name__ == "__main__":
    main()