def load_script(path):
    """Read a script file and return its text, or None if the file is missing."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except FileNotFoundError:
        print(f"Sorry, I could not find '{path}'. Check the name and the folder.")
        return None


def main():
    path = input("Type the script file name (example: sample_scripts/broken_short.txt): ").strip()
    text = load_script(path)
    if text is None:
        return
    print(f"Loaded: {path}")
    print(f"Lines: {len(text.splitlines())}")
    print(f"Words: {len(text.split())}")


if __name__ == "__main__":
    main()
    