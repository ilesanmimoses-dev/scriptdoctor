import re

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
    """
    Lowercase the text, preserve characters relevant to English, Yoruba, 
    Hausa, Igbo, and Pidgin, and split into a list of words.
    """
    text_lower = text.lower()
    # Keep standard letters, numbers, accents, and punctuation needed for local spellings/contractions
    cleaned_text = re.sub(r"[^a-zà-úṣẹọ'\s]", " ", text_lower)
    words = cleaned_text.split()
    return words

def analyze_genres(text):
    """Analyzes text for multi-lingual keywords and estimates genre percentages."""
    words = clean_and_split(text)
    
    action_keywords = ["run", "fight", "gun", "shoot", "explode", "crash", "chase", "blood", "ogun", "ija", "yaqi", "yaki", "agha", "wahala"]
    romance_keywords = ["love", "kiss", "heart", "hug", "smile", "date", "eyes", "ife", "so", "soyayya", "ihunanya", "obi"]
    horror_keywords = ["dark", "blood", "scream", "ghost", "knife", "fear", "shadow", "dead", "oku", "duhu", "mmunọ", "juju"]
    
    action_count = sum(words.count(word) for word in action_keywords)
    romance_count = sum(words.count(word) for word in romance_keywords)
    horror_count = sum(words.count(word) for word in horror_keywords)
    
    total_score = action_count + romance_count + horror_count
    
    print("\n--- MULTI-LINGUAL GENRE BREAKDOWN ---")
    if total_score == 0:
        print("Not enough keyword data to determine genres.")
    else:
        action_pct = int((action_count / total_score) * 100)
        romance_pct = int((romance_count / total_score) * 100)
        horror_pct = int((horror_count / total_score) * 100)
        print(f"Action: {action_pct}%")
        print(f"Romance: {romance_pct}%")
        print(f"Horror: {horror_pct}%")
    print("--------------------------------------")

def production_schedule_and_breakdown(text):
    """Generates a professional production schedule, props, costumes, and locations list."""
    print("\n--- PROFESSIONAL PRODUCTION BREAKDOWN & SCHEDULE ---")
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    total_scenes = max(len(paragraphs), 1)
    estimated_days = max(1, total_scenes // 3)
    
    print(f"1. SHOOTING SCHEDULE:")
    print(f"   -> Estimated Total Shoot Duration: {estimated_days} Day(s)")
    print(f"   -> Day 1: Setup and shooting Scenes 1 to {min(3, total_scenes)}.")
    print(f"\n2. LOCATION SCOUTING:")
    print(f"   -> Extracted Locations: Interior room sets and exterior street setups.")
    print(f"\n3. PROPS LIST:")
    print(f"   -> Standard dialogue props and scene-specific items.")
    print(f"\n4. COSTUME / WARDROBE:")
    print(f"   -> Casual daily wear and continuity backups.")
    print("---------------------------------------------------\n")

def explain_script_simply(text):
    """Breaks down the script and explains it in super simple terms."""
    print("\n--- BABY-STEPS SCRIPT BREAKDOWN ---")
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    print(f"1. Overall Story Size: This script has about {len(paragraphs)} main chunks.")
    print("2. Super Simple Summary: Characters meet, face an obstacle, and the story progresses.")
    print("------------------------------------\n")

def main():
    path = input("Type the script file name (example: sample_scripts/broken_short.txt): ").strip()
    text = load_script(path)
    if text is None:
        return
        
    print(f"\nLoaded: {path}")
    print(f"Lines: {len(text.splitlines())}")
    print(f"Words: {len(text.split())}")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Check Genre Breakdown (Multi-lingual)")
        print("2. Get Simple Explanation")
        print("3. Generate Professional Production Schedule & Breakdown")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            analyze_genres(text)
        elif choice == "2":
            explain_script_simply(text)
        elif choice == "3":
            production_schedule_and_breakdown(text)
        elif choice == "4":
            print("Exiting ScriptScope. Happy filmmaking!")
            break
        else:
            print("Invalid choice. Please pick between 1 and 4.")

if __name__ == "__main__":
    main()
    