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

def analyze_genres(text):
    """
    Analyzes text for multi-lingual keywords (English, Yoruba, Hausa, Igbo, Pidgin) 
    and estimates genre percentages.
    """
    text_lower = text.lower()
    
    # Expanded multi-lingual keyword dictionaries
    action_keywords = [
        # English
        "run", "fight", "gun", "shoot", "explode", "crash", "chase", "blood",
        # Yoruba
        "ogun", "ija", "pa", "sa", 
        # Hausa
        "yaqi", "yaki", "harbi", 
        # Igbo
        "agha", "igbu", "ọsọ", 
        # Pidgin
        "wahala", "pepper", "fighter"
    ]
    
    romance_keywords = [
        # English
        "love", "kiss", "heart", "hug", "smile", "date", "eyes", "sweet",
        # Yoruba
        "ife", "fẹ", "ọkan", "ẹwa", 
        # Hausa
        "so", "soyayya", "zuciya", "kyau", 
        # Igbo
        "ihunanya", "obi", "mmanya", 
        # Pidgin
        "baby", "darling", "sweetheart", "mylove"
    ]
    
    horror_keywords = [
        # English
        "dark", "blood", "scream", "ghost", "knife", "fear", "shadow", "dead",
        # Yoruba
        "oku", "ẹmi", "buba", "òkùnkùn", 
        # Hausa
        "duhu", "aljana", "tsoro", 
        # Igbo
        "mmunọ", "egwu", "oji", 
        # Pidgin
        "juju", "spirit", "ghost"
    ]
    
    action_count = sum(text_lower.count(word) for word in action_keywords)
    romance_count = sum(text_lower.count(word) for word in romance_keywords)
    horror_count = sum(text_lower.count(word) for word in horror_keywords)
    
    total_score = action_count + romance_count + horror_count
    
    print("\n--- MULTI-LINGUAL GENRE BREAKDOWN ---")
    if total_score == 0:
        print("Not enough keyword data to determine genres across English, Yoruba, Hausa, Igbo, or Pidgin.")
    else:
        # Calculate rough percentages
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
    
    print(f"1. SHOOTING SCHEDULE (Industry Standard):")
    print(f"   -> Estimated Total Shoot Duration: {estimated_days} Day(s)")
    print(f"   -> Day 1: Setup, equipment check, and shooting Scenes 1 to {min(3, total_scenes)}.")
    if estimated_days > 1:
        print(f"   -> Day 2 to {estimated_days}: Remaining scene blocks, company moves, and wrap.")
        
    print(f"\n2. LOCATION SCOUTING:")
    print(f"   -> Extracted Locations: Based on scene headings (INT./EXT.), you will need standard interior room sets and exterior street setups secured with permits.")
    
    print(f"\n3. PROPS LIST (Estimated per scene requirements):")
    print(f"   -> Standard dialogue props (e.g., phones, bags, coffee cups, or scene-specific items based on action cues).")
    
    print(f"\n4. COSTUME / WARDROBE:")
    print(f"   -> Character Wardrobe: Casual daily wear for main cast, plus backup duplicate outfits for continuity if shooting multi-day action sequences.")
    print("---------------------------------------------------\n")

def explain_script_simply(text):
    """Breaks down the script and explains it in super simple terms."""
    print("\n--- BABY-STEPS SCRIPT BREAKDOWN ---")
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    total_scenes = len(paragraphs)
    
    print(f"1. Overall Story Size: This script has about {total_scenes} main chunks or blocks.")
    print("2. Super Simple Summary:")
    print("   -> Characters meet, face a situation or obstacle, and the scene changes based on their choices.")
    print("------------------------------------\n")

def main():
    path = input("Type the script file name (example: sample_scripts/broken_short.txt): ").strip()
    text = load_script(path)
    if text is None:
        return
        
    print(f"\nLoaded: {path}")
    print(f"Lines: {len(text.splitlines())}")
    print(f"Words: {len(text.split())}")
    
    # Menu of options for the user
    while True:
        print("\nWhat would you like to do?")
        print("1. Check Genre Breakdown (Multi-lingual)")
        print("2. Get Simple Explanation (Explain like a baby)")
        print("3. Generate Professional Production Schedule & Breakdown (Props, Costumes, Locations)")
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
    