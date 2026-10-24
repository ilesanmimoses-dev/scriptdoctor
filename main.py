import unicodedata

# Hausa hooked letters are often typed as plain b, d, k and y,
# so we treat each hooked letter and its plain version as the same letter.
HOOKED_LETTERS = {"ɓ": "b", "ɗ": "d", "ƙ": "k", "ƴ": "y"}


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
    print("First 10 words:   ", words[:10])
    print("After normalizing:", [normalize_word(word) for word in words[:10]])


if __name__ == "__main__":
    main()
    