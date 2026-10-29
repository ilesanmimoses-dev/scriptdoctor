ScriptScope — resume point (end of Phase 2)

STATUS: Phase 1, 1.1, and 2 complete.
Gates 1, 2, 3 cleared.
Last commit: 2b07185 "Step 17c: free-text schedule preferences"
Repo: github.com/ilesanmimoses-dev/scriptdoctor

WHAT'S BUILT:
- Full rule-based script analysis: genres, errors, score, report
- Scenes, language detection, characters, dialogue ratio, length
- Plain-words explanation (facts only)
- Props and costumes (named items only)
- Optional schedule: pages/day or scenes/day, keyword preferences

NEXT DECISIONS (before Phase 3):
1. Use it on a real script first. Find what's actually wrong.
2. Only after real feedback: decide if Phase 3 AI is needed.
3. Phase 3 needs: provider choice, API key security, dependency install, cost budget.

IF STARTING PHASE 3, first step is:
- Pick OpenAI or Anthropic
- Set up billing
- Store key in .env (never in code, .env in .gitignore)
- pip install <sdk>
- Add a separate optional "AI mode" so the rule-based mode still works offline
