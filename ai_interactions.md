# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I didn't hand the whole project over in one shot — I went phase by phase, the way the module was structured, and gave the agent one scoped task at a time instead of "build the whole recommender." Concept phase, implementation phase, evaluation phase, and model card phase were each their own conversation turn, and within each one I asked for specific things rather than a blanket rewrite, so I was still the one deciding what the recipe should actually be and whether a result made sense.

**Prompts used:**

These followed the module's own prompts pretty closely:

- "Analyze the available data in songs.csv and suggest which features would be most effective for a simple content-based recommender."
- "How do I calculate a score for a numerical feature like energy that rewards songs closer to my target, not just higher or lower values?" and "why do I need both a Scoring Rule and a Ranking Rule?"
- "Implement `load_songs` using Python's csv module, converting numeric fields to floats."
- "Here's my Algorithm Recipe — genre match worth more than mood match, energy scored by closeness — implement `score_song` so it returns both a numeric score and a list of reasons."
- "What's the most Pythonic way to loop through all songs, score them, and return the top k sorted highest to lowest? Also, what's the difference between `.sort()` and `sorted()`?"
- "Suggest adversarial or edge-case user profiles that could break or expose weaknesses in my scoring logic."
- "Explain why this specific song ranked #1 given my current weights."
- "Apply this one weight change (double energy, halve genre) and verify the math is still valid."
- "Look at recommender.py and songs.csv and identify potential filter bubbles or biases in the scoring logic."
- "Fill out the model card sections in plain language based on what we found."

**What did the agent generate or change?**

- `data/songs.csv` — added 8 songs to get from 10 to 18, in genres/moods the starter set didn't cover
- `src/recommender.py` — turned the `# TODO` stubs into real `load_songs`, `score_song`, `recommend_songs`, and `Recommender` class logic based on the recipe I gave it
- `src/main.py` — fixed a broken import that was stopping the file from running at all, and added the stress-test profiles
- `README.md` and `model_card.md` — wrote up the design reasoning, sample output, stress-test results, and model card sections, which I then read through and adjusted

**What did you verify or fix manually?**

This is the part the module kept emphasizing — stay in control, don't just accept what the AI gives you — so a few things I specifically double-checked instead of taking on faith: I ran `python -m src.main` myself and watched the broken import actually throw a `ModuleNotFoundError` before accepting the fix. When the agent first summarized the weight-shift experiment (doubling energy, halving genre), the numbers it described didn't actually get re-run — I pushed back and had it verify with a real script, which caught that its first guess at the new ranking was wrong. I ran `pytest` after each phase to make sure nothing broke silently, and I read the CLI output for each test profile myself to judge whether the recommendations actually matched my own intuition (e.g., does the "Chill Lofi" profile really surface chill, low-energy songs) rather than trusting that the code just compiling meant it was correct.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

Not attempted — the project stayed small enough (one scoring function, one ranking function, a couple of dataclasses) that reaching for a named pattern like Strategy or Factory would have been overkill for an 18-song catalog. Leaving this section blank.
