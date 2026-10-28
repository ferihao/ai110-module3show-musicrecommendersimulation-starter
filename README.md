# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

**VibeFinder 1.0** is a small, CLI-first, content-based music recommender. It loads an 18-song catalog from `data/songs.csv`, scores every song against a user's stated genre/mood/energy/acoustic preferences using a hand-weighted point system (genre > mood > energy closeness > acoustic match), and prints a ranked top-K list with a plain-language explanation for each pick. See [model_card.md](model_card.md) for the full writeup of how it works, what it's good at, and where it's biased.

---

## How The System Works

Real-world recommenders (Spotify, YouTube, Netflix) work by representing both items and users as vectors of features — a song's genre, mood, tempo, and acoustic qualities on one side, a listener's taste profile on the other — then measuring how close they are. They blend two signals: a "content-based" signal (how similar is this item to things the user already likes, based on the item's own attributes, like genre or tempo) and a "collaborative" signal built from **user interaction history** (what did users with similar listening/skip/like behavior enjoy, even if the items don't share obvious attributes). They rank, rather than just filter, because the goal isn't a yes/no match but an ordered list of best guesses, and they constantly re-score as new interaction data comes in. My version is a simplified, purely content-based slice of that idea: no interaction history, no collaborative signal, just a hand-written scoring rule that compares a song's static attributes to a user's stated preferences. It prioritizes **genre** match above everything else (a user who said they like lofi rarely wants rock no matter how well the other numbers line up), then **mood** match, then **energy** closeness (scored by how near the song's energy is to the user's target, not simply "higher is better"), and finally a smaller bonus for matching the user's **acoustic** preference. The emphasis is on transparency over sophistication: every recommendation should be explainable in one sentence, even if the taste model itself is much cruder than a real production system.

**`Song` features used:** `genre`, `mood`, `energy`, `acousticness` (id/title/artist are for display/explanation only; `tempo_bpm`, `valence`, and `danceability` are loaded but not currently scored — see Experiments).

**`UserProfile` fields:** `favorite_genre`, `favorite_mood`, `target_energy`, `likes_acoustic`.

### Sample User Profile

```python
user_prefs = {
    "favorite_genre": "lofi",
    "favorite_mood": "chill",
    "target_energy": 0.4,
    "likes_acoustic": True,
}
```

**Does this differentiate "intense rock" from "chill lofi"?** Yes, on all three axes at once: genre (`lofi` vs `rock`) and mood (`chill` vs `intense`) both fail to match, and `target_energy=0.4` is far from an intense rock song's energy (typically ~0.9), so the energy-closeness term also scores low. The profile is narrow enough to clearly reject that song, but *not* too narrow in general — it would still correctly favor "chill lofi" over "chill jazz" (mood ties, genre breaks it) or over "focused lofi" (genre ties, mood breaks it), since genre and mood are independent fields rather than one combined label.

### Algorithm Recipe (finalized)

- **+2.0 points** for an exact `genre` match
- **+1.0 point** for an exact `mood` match
- **Up to +1.0 point** for energy similarity: `1 - abs(target_energy - song.energy)` (closer to the target scores higher, not simply "more energy is better")
- **+0.5 points** if `likes_acoustic` is true and the song's `acousticness` is above a threshold (e.g. `> 0.6`)

`score = 2.0 * genre_match + 1.0 * mood_match + 1.0 * (1 - abs(target_energy - song.energy)) + 0.5 * acoustic_match`

### Data Flow

```
Input (UserProfile)
      │
      ▼
Process — for each Song in songs.csv:
      compute score_song(user, song) → (score, reasons)
      │
      ▼
Output — Ranking:
      sort all (song, score) pairs descending by score
      take the top K
      return [(song, score, explanation), ...]
```

A single song's journey: CSV row → `Song` object → scored once against the `UserProfile` → placed into the full list of scored songs → sorted → kept or dropped depending on whether it lands in the top `K`.

### Expected Biases

- **Genre dominance:** at `+2.0` vs `+1.0` for mood and `+1.0` max for energy, a genre mismatch is very hard for mood/energy to outweigh — the system may bury a great mood/energy match just because it's filed under the "wrong" genre label (e.g. "indie pop" vs "pop" are practically neighbors but scored as a total genre miss).
- **No handling of blended or adjacent genres/moods** — the catalog treats genre and mood as flat categorical labels, so a song that's genuinely between two genres gets no partial credit.
- **Small, hand-curated catalog (18 songs):** the dataset was partly authored by an AI assistant for diversity, not sampled from real listening data, so it won't reflect actual genre/mood correlations or popularity skew found in a real catalog.
- **Cold-start blindness:** since this is purely content-based with no interaction history, the system can't learn "users like you also liked X" — it will never surprise a user with something outside their stated profile.

**Ranking:** every song is scored independently, then sorted descending by score and truncated to the top `k`.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Output of `python -m src.main` for the default profile (`genre=pop, mood=happy, energy=0.8`):

```
Loaded songs: 18

Top recommendations:

1. Sunrise City by Neon Echo - Score: 3.98
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.98)

2. Gym Hero by Max Pulse - Score: 2.87
   Because: genre match (+2.0), energy closeness (+0.87)

3. Rooftop Lights by Indigo Parade - Score: 1.96
   Because: mood match (+1.0), energy closeness (+0.96)

4. Concrete Dreams by MC Vantage - Score: 1.00
   Because: energy closeness (+1.00)

5. Night Drive Loop by Neon Echo - Score: 0.95
   Because: energy closeness (+0.95)
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Stress Test: Diverse & Adversarial Profiles

`src/main.py` now runs the recommender against six profiles: three ordinary tastes and three edge cases meant to try to "trick" the scoring logic (conflicting signals, a missing field, and a genre that doesn't exist in the catalog). Full output of `python -m src.main`:

```
=== Profile: High-Energy Pop ({'genre': 'pop', 'mood': 'happy', 'energy': 0.9, 'likes_acoustic': False}) ===

1. Sunrise City by Neon Echo - Score: 3.92
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.92)

2. Gym Hero by Max Pulse - Score: 2.97
   Because: genre match (+2.0), energy closeness (+0.97)

3. Rooftop Lights by Indigo Parade - Score: 1.86
   Because: mood match (+1.0), energy closeness (+0.86)

4. Storm Runner by Voltline - Score: 0.99
   Because: energy closeness (+0.99)

5. Neon Pulse Club by Static Bloom - Score: 0.98
   Because: energy closeness (+0.98)


=== Profile: Chill Lofi ({'genre': 'lofi', 'mood': 'chill', 'energy': 0.3, 'likes_acoustic': True}) ===

1. Library Rain by Paper Lanterns - Score: 4.45
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.95), acoustic match (+0.5)

2. Midnight Coding by LoRoom - Score: 4.38
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.88), acoustic match (+0.5)

3. Focus Flow by LoRoom - Score: 3.40
   Because: genre match (+2.0), energy closeness (+0.90), acoustic match (+0.5)

4. Spacewalk Thoughts by Orbit Bloom - Score: 2.48
   Because: mood match (+1.0), energy closeness (+0.98), acoustic match (+0.5)

5. Lonesome Highway by Delta Moon - Score: 1.50
   Because: energy closeness (+1.00), acoustic match (+0.5)


=== Profile: Deep Intense Rock ({'genre': 'rock', 'mood': 'intense', 'energy': 0.9, 'likes_acoustic': False}) ===

1. Storm Runner by Voltline - Score: 3.99
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.99)

2. Gym Hero by Max Pulse - Score: 1.97
   Because: mood match (+1.0), energy closeness (+0.97)

3. Neon Pulse Club by Static Bloom - Score: 0.98
   Because: energy closeness (+0.98)

4. Iron Collapse by Graveyard Volt - Score: 0.93
   Because: energy closeness (+0.93)

5. Sunrise City by Neon Echo - Score: 0.92
   Because: energy closeness (+0.92)


=== Profile: Conflicting Signals (sad + high energy) ({'genre': 'blues', 'mood': 'sad', 'energy': 0.9, 'likes_acoustic': True}) ===

1. Lonesome Highway by Delta Moon - Score: 3.90
   Because: genre match (+2.0), mood match (+1.0), energy closeness (+0.40), acoustic match (+0.5)

2. Midnight Coding by LoRoom - Score: 1.02
   Because: energy closeness (+0.52), acoustic match (+0.5)

3. Focus Flow by LoRoom - Score: 1.00
   Because: energy closeness (+0.50), acoustic match (+0.5)

4. Storm Runner by Voltline - Score: 0.99
   Because: energy closeness (+0.99)

5. Neon Pulse Club by Static Bloom - Score: 0.98
   Because: energy closeness (+0.98)


=== Profile: No Genre Preference ({'mood': 'chill', 'energy': 0.3}) ===

1. Spacewalk Thoughts by Orbit Bloom - Score: 1.98
   Because: mood match (+1.0), energy closeness (+0.98)

2. Library Rain by Paper Lanterns - Score: 1.95
   Because: mood match (+1.0), energy closeness (+0.95)

3. Midnight Coding by LoRoom - Score: 1.88
   Because: mood match (+1.0), energy closeness (+0.88)

4. Lonesome Highway by Delta Moon - Score: 1.00
   Because: energy closeness (+1.00)

5. Riverside Letters by Willow Creek - Score: 0.97
   Because: energy closeness (+0.97)


=== Profile: Unknown Genre (k-pop) ({'genre': 'k-pop', 'mood': 'happy', 'energy': 0.8}) ===

1. Sunrise City by Neon Echo - Score: 1.98
   Because: mood match (+1.0), energy closeness (+0.98)

2. Rooftop Lights by Indigo Parade - Score: 1.96
   Because: mood match (+1.0), energy closeness (+0.96)

3. Concrete Dreams by MC Vantage - Score: 1.00
   Because: energy closeness (+1.00)

4. Night Drive Loop by Neon Echo - Score: 0.95
   Because: energy closeness (+0.95)

5. Neon Pulse Club by Static Bloom - Score: 0.92
   Because: energy closeness (+0.92)
```

**Observation — why "Gym Hero" (mood=`intense`) shows up for a "happy pop" listener:** it ranks #2 for High-Energy Pop purely on genre (+2.0) and energy closeness (+0.97) — mood contributes nothing there. Because genre is worth 2x what mood is worth, a song can completely miss your mood and still outrank songs that nail the mood but miss the genre. That's the single biggest thing the current weighting gets "wrong" relative to intuition.

**Observation — conflicting signals degrade gracefully, not randomly:** when asked for `blues/sad/energy=0.9` (a combination that barely exists — blues and sad songs in this catalog are low-energy), the system doesn't fall over; it correctly prefers the one song that matches genre+mood even though its energy is far off (closeness only +0.40), because 2.0 + 1.0 still beats anything winning on energy alone. This shows genre/mood matches dominate energy closeness by design, for better or worse.

**Observation — missing/unknown fields fail safely:** dropping `genre` entirely, or asking for a genre that doesn't exist in the catalog (`k-pop`), doesn't crash — `score_song` just never awards that bonus, so recommendations fall back to mood + energy closeness. The system never raises a `KeyError`, but it also never tells the user that the preference it asked for was unsatisfiable.

---

## Experiments You Tried

**Weight shift (energy ×2, genre ÷2):** Temporarily changed the recipe from `2.0×genre + 1.0×mood + 1.0×energy_closeness` to `1.0×genre + 1.0×mood + 2.0×energy_closeness` and re-ran all three core profiles.

- **High-Energy Pop — before:** Sunrise City (3.92), Gym Hero (2.97), Rooftop Lights (1.86), Storm Runner (0.99), Neon Pulse Club (0.98)
- **High-Energy Pop — after:** Sunrise City (3.84), Gym Hero (2.94), Rooftop Lights (2.72), Storm Runner (1.98), Neon Pulse Club (1.96)
- **Chill Lofi — before:** Library Rain (4.45), Midnight Coding (4.38), Focus Flow (3.40), **Spacewalk Thoughts (2.48)**, Lonesome Highway (1.50)
- **Chill Lofi — after:** Library Rain (4.40), Midnight Coding (4.26), **Spacewalk Thoughts (3.46)**, Focus Flow (3.30), Lonesome Highway (2.50)

For High-Energy Pop the top-5 order didn't actually change — the genre-matching songs here also happen to have the closest energy, so genre and energy were pulling in the same direction. The more telling result is Chill Lofi: **Spacewalk Thoughts** (mood match only, no genre match — it's `ambient`, not `lofi`) swapped places with **Focus Flow** (genre match only, no mood match) once energy was weighted more heavily, because Spacewalk's energy (0.28) happens to sit closer to the 0.3 target than Focus Flow's (0.40). This confirms the weights really do control *which kind* of match wins ties between a genre-only match and a mood-only match — it didn't feel more "accurate," just differently biased toward energy. The change was reverted; the shipped weights remain `2.0 / 1.0 / 1.0 / 0.5`.

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

[**Model Card**](model_card.md) — full details, including a personal reflection on the engineering process, live there.

Building this made concrete something that's easy to say abstractly: a recommender turns a *prediction problem* ("will this user like this song?") into an *arithmetic problem* (assign numeric weights to a handful of comparisons and add them up). There's no understanding of music happening anywhere in this system — just string equality checks and one absolute-value formula — yet the output reads as a confident, personalized suggestion with a plausible-sounding reason attached. That gap between how the system actually works and how its output *feels* is, I think, the core thing worth understanding about real recommenders too.

Bias shows up here exactly where it would in a real system: in the weights. Genre being worth twice what mood is worth isn't a neutral design choice — it's a bet about what matters more to listeners, baked in by whoever wrote the scoring function, and it quietly determines which songs a strict-genre listener will never see even if the mood/energy fit perfectly (see "Gym Hero" in the Stress Test section above). At production scale, with the same dynamic multiplied across millions of users and dozens of signals instead of four, that kind of single-axis over-weighting is exactly how filter bubbles and unintentionally unfair rankings get built — not through malice, but through a handful of coefficients nobody revisited after they were first chosen.



