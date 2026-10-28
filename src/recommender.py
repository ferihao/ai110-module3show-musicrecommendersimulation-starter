import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

ACOUSTIC_THRESHOLD = 0.6

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def _score_song_dataclass(user: UserProfile, song: Song) -> Tuple[float, List[str]]:
    """Applies the Algorithm Recipe to a Song/UserProfile pair."""
    score = 0.0
    reasons = []

    if song.genre == user.favorite_genre:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if song.mood == user.favorite_mood:
        score += 1.0
        reasons.append("mood match (+1.0)")

    energy_score = max(0.0, 1.0 - abs(user.target_energy - song.energy))
    score += energy_score
    reasons.append(f"energy closeness (+{energy_score:.2f})")

    if user.likes_acoustic and song.acousticness > ACOUSTIC_THRESHOLD:
        score += 0.5
        reasons.append("acoustic match (+0.5)")

    return score, reasons

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs for a user, sorted highest score first."""
        scored = [(song, _score_song_dataclass(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable explanation of a song's score for a user."""
        score, reasons = _score_song_dataclass(user, song)
        reason_text = ", ".join(reasons) if reasons else "no strong matches"
        return f"{song.title} scored {score:.2f} because: {reason_text}"

def load_songs(csv_path: str) -> List[Dict]:
    """Loads songs from a CSV file into a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Scores a single song dict against a user_prefs dict using the Algorithm Recipe."""
    score = 0.0
    reasons = []

    if "genre" in user_prefs and song.get("genre") == user_prefs["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if "mood" in user_prefs and song.get("mood") == user_prefs["mood"]:
        score += 1.0
        reasons.append("mood match (+1.0)")

    if "energy" in user_prefs:
        energy_score = max(0.0, 1.0 - abs(user_prefs["energy"] - song.get("energy", 0.0)))
        score += energy_score
        reasons.append(f"energy closeness (+{energy_score:.2f})")

    if user_prefs.get("likes_acoustic") and song.get("acousticness", 0.0) > ACOUSTIC_THRESHOLD:
        score += 0.5
        reasons.append("acoustic match (+0.5)")

    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Scores every song against user_prefs and returns the top k, ranked highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
