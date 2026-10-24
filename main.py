import unicodedata

# Hausa hooked letters are often typed as plain b, d, k and y,
# so we treat each hooked letter and its plain version as the same letter.
HOOKED_LETTERS = {"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y"}

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
        # Keep letters, digits, apostrophes and tone marks. Everything else becomes a space.
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
    print("Keyword matches per genre:")
    for genre in counts:
        print(f"  {genre:<16} {counts[genre]}")


if __name__ == "__main__":
    main()
    