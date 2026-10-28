# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

VibeFinder takes a short list of stated preferences (favorite genre, favorite mood, target energy, and whether you like acoustic sound) and returns a ranked top-K list of songs from a small, fixed catalog, each with a one-line reason for why it was picked. It assumes the user can clearly state their taste up front — it doesn't learn from listening history, skips, or likes, and it assumes the catalog actually contains something that fits (it has no way to say "nothing here matches you"). This is a classroom exploration project, not a production system: it's meant to make the mechanics of a content-based recommender visible and explainable, not to power a real app. It should not be used to make claims about real listener behavior, to rank or judge music quality, or to stand in for a properly evaluated production recommender — the 18-song catalog is far too small and too hand-curated to generalize from.

---

## 3. How the Model Works  

The recommender works like a judge scoring every song in the catalog against what you told it you like, then handing you the highest scorers. It looks at four things about each song: its genre, its mood, how energetic it is, and whether it leans acoustic. If a song's genre matches your favorite genre, it gets a big bonus. If the mood matches too, it gets a smaller bonus. Then it checks how close the song's energy level is to the energy you said you wanted — a song doesn't have to be the *most* energetic to score well, it just has to be *close* to what you asked for. Finally, if you said you like acoustic music and the song sounds acoustic, it gets one more small bonus. All those bonuses are added up into a single score, every song gets judged the same way, and the songs with the highest scores are returned first, along with a plain-English list of the reasons they scored the way they did. The starter code had no logic at all (it just returned the first few songs in the file, unranked) — the real change here was writing the actual point system and making it explain itself rather than just returning a silent number.

---

## 4. Data  

The catalog is `data/songs.csv`, 18 songs total: the 10 starter songs plus 8 I added to broaden the genre/mood coverage. Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, classical, hip-hop, country, metal, folk, electronic, reggae, and blues. Moods represented: happy, chill, intense, relaxed, moody, focused, peaceful, energetic, nostalgic, angry, melancholy, and sad. Each song also has four numeric features (0.0–1.0 scale, except `tempo_bpm`): `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness` — of these, only `energy` and `acousticness` currently feed the scoring logic. This is a tiny, hand-authored dataset (partly generated with AI assistance for variety), not a sample of real listening data, so there's exactly one song per genre/mood combination in most cases — it has no concept of artist popularity, release era, lyrical content, or regional/cultural music traditions, and a real user's taste almost certainly doesn't map cleanly onto these 18 songs.

---

## 5. Strengths  

VibeFinder works best for users with a clear, internally consistent taste — someone who wants "chill lofi" or "intense rock" gets a top-5 list that actually matches that vibe, because genre and mood agreeing with each other lets both weighted terms pull in the same direction (see the Chill Lofi and Deep Intense Rock results in Evaluation). The energy-closeness scoring correctly captures the idea that "vibe" isn't just "more energy is better" — a user who wants calm, low-energy music is never pushed toward the most energetic song in the catalog just because energy is a number. It also handles missing or nonsensical inputs (no genre given, or a genre that doesn't exist) without crashing, falling back gracefully to whatever signals it does have. And because every recommendation comes with a plain-language list of reasons, it's easy for anyone — not just someone who read the code — to see exactly why a song was picked, which matched my intuition every time I checked a result by hand.

---

## 6. Limitations and Bias 

The biggest bias discovered during testing is that **genre match (+2.0) outweighs mood match (+1.0) by design**, which means a song can completely miss a listener's mood and still beat a song that nails the mood but misses the genre — "Gym Hero" (mood=`intense`) outranked every happy-but-wrong-genre song for a "Happy Pop" listener purely because it shared the `pop` genre tag and had similar energy. This creates a mild filter bubble: listeners effectively get sorted by genre first and everything else second, so a listener with a strict genre preference will rarely see cross-genre songs that might actually match their mood better. The system also has no concept of an "unsatisfiable" request — when a user asked for `blues + sad + energy=0.9` (a near-contradiction, since the catalog's blues/sad songs are all low-energy), it silently returned its best available compromise rather than flagging that no song in the catalog really fits. Finally, because genre and mood are flat string matches, there is no partial credit for closely related categories (`pop` vs `indie pop`, `chill` vs `relaxed`), so near-misses are scored identically to total mismatches. With only 18 songs and no popularity or interaction data, the over-weighting of genre is also compounded by how little variety exists within any single genre, which limits how much room the mood/energy terms have to correct for it.

---

## 7. Evaluation  

Six profiles were tested via `src/main.py` (full terminal output in README.md under "Stress Test: Diverse & Adversarial Profiles"): three ordinary tastes (High-Energy Pop, Chill Lofi, Deep Intense Rock) and three adversarial/edge cases (Conflicting Signals, No Genre Preference, Unknown Genre). For each, I looked at whether the #1 result matched my own intuition for that taste, and whether anything in the top 5 felt out of place.

**High-Energy Pop vs. Deep Intense Rock:** these two profiles share the same `energy=0.9` target but opposite genre/mood, and they correctly produced almost entirely disjoint top-5 lists (Sunrise City/Gym Hero/Rooftop Lights vs. Storm Runner/Gym Hero/Iron Collapse) — this makes sense because genre is the single heaviest-weighted signal, so changing it swings the whole list even with energy held constant. The one song both lists share, "Gym Hero" (pop, mood=intense, energy=0.93), makes sense once you notice it has pop's genre tag *and* rock-like intensity/energy, so it legitimately scores well for both audiences — it isn't a bug, but it is a reminder that a single "intense pop" song can quietly dominate multiple very different-sounding profiles in a catalog this small.

**High-Energy Pop vs. Chill Lofi:** as expected, these are near-total opposites — the high-energy profile surfaces upbeat, loud songs while the chill profile surfaces quiet, mellow, acoustic-leaning songs (Library Rain, Midnight Coding), confirming the energy-closeness term is doing its job of pulling toward the *target*, not just toward "more energy."

**Conflicting Signals vs. a "normal" profile:** asking for `blues + sad + energy=0.9` still returned "Lonesome Highway" at #1 (the catalog's only blues/sad song) despite its real energy being only 0.30 — genre+mood match (+3.0) beat every energy-only match, which is mathematically correct given the weights but was the most surprising result: the system will happily recommend a song that fails one of your stated preferences by a wide margin (energy closeness only +0.40) as long as it wins on the other two.

**No Genre Preference vs. Unknown Genre (k-pop):** these behaved almost identically to each other (both fall back to ranking by mood + energy closeness) and differently from a normal pop profile — confirming that an unsatisfiable genre and a missing genre are functionally the same to the scorer, which is a correctness win (no crash) but also means the system can't tell the user "nothing in this catalog matches what you asked for."

No numeric accuracy metrics were computed since there's no ground-truth "correct" ranking for a taste-based system like this; evaluation here is qualitative, based on whether rankings matched reasonable human intuition for each profile.

---

## 8. Future Work  

If I kept developing this, I'd want to: (1) add partial credit for related genres/moods instead of exact-string matching, so "indie pop" isn't a total miss for a "pop" fan and "relaxed" isn't a total miss for a "chill" fan; (2) add a simple diversity rule to the ranking step (e.g. cap how many songs from the same artist or genre can appear in the top K), since right now two songs from the same artist can both land in the top 5 even when more varied options exist; and (3) let the system say "no strong matches found" when every song scores low, instead of always confidently returning K songs even for an unsatisfiable or contradictory profile.

---

## 9. Personal Reflection  

My biggest learning moment was seeing how much a recommender's "personality" comes down to a handful of weight constants — moving genre's weight from 2.0 to 1.0 didn't just shuffle numbers, it changed which *kind* of match the system trusted more, and that single number quietly decides how much a listener's genre loyalty gets respected versus their mood or energy. Using an AI assistant was fastest for the repetitive, well-specified parts — writing the CSV loader, wiring up sorting, drafting plain-language explanations for the model card — but I had to slow down and double-check anything involving actual numbers: verifying the weight-shift experiment by rerunning it rather than trusting a plausible-sounding guess at the new rankings, and checking that the "conflicting signals" result (energy off by 0.6 but still ranked #1) was really coming from the math and not a bug. What surprised me most is how convincingly a system this simple can "feel" like it understands taste — a handful of if-statements and one absolute-value formula produced explanations that read like a thoughtful recommendation, which is a useful reminder that feeling personalized and actually understanding a user are two very different things. If I extended this, I'd want to test it against a real friend's stated preferences and see where their intuition and the scoring recipe disagree.
