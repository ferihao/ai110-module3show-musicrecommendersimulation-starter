"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from src.recommender import load_songs, recommend_songs


# Evaluation profiles: 3 "normal" tastes + 3 adversarial/edge cases
# (see model_card.md Evaluation section for discussion of each)
PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.3, "likes_acoustic": True},
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False},
    # Adversarial: contradictory signal (wants max energy but a "sad" mood,
    # a combination that barely exists in the catalog)
    "Conflicting Signals (sad + high energy)": {"genre": "blues", "mood": "sad", "energy": 0.9, "likes_acoustic": True},
    # Edge case: no genre key at all
    "No Genre Preference": {"mood": "chill", "energy": 0.3},
    # Edge case: a genre that doesn't exist anywhere in the catalog
    "Unknown Genre (k-pop)": {"genre": "k-pop", "mood": "happy", "energy": 0.8},
}


def print_recommendations(songs, user_prefs, k=5) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=k)
    for rank, rec in enumerate(recommendations, start=1):
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{rank}. {song['title']} by {song['artist']} - Score: {score:.2f}")
        print(f"   Because: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, user_prefs in PROFILES.items():
        print(f"\n=== Profile: {name} ({user_prefs}) ===\n")
        print_recommendations(songs, user_prefs, k=5)


if __name__ == "__main__":
    main()
