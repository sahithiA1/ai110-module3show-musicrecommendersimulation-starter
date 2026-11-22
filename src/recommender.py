import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Scoring weights (they add up to 1.0, so every score is between 0.0 and 1.0)
GENRE_WEIGHT = 0.4
MOOD_WEIGHT = 0.3
ENERGY_WEIGHT = 0.3


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


# ---------------------------------------------------------------------------
# Scoring building blocks (shared by the OOP and functional versions)
# ---------------------------------------------------------------------------

def genre_match(song_genre: str, favorite_genre: str) -> float:
    """Returns 1.0 if the genres are the same (ignoring case/spaces), else 0.0."""
    return 1.0 if song_genre.strip().lower() == favorite_genre.strip().lower() else 0.0


def mood_match(song_mood: str, favorite_mood: str) -> float:
    """Returns 1.0 if the moods are the same (ignoring case/spaces), else 0.0."""
    return 1.0 if song_mood.strip().lower() == favorite_mood.strip().lower() else 0.0


def energy_similarity(song_energy: float, target_energy: float) -> float:
    """Returns 1 - |song_energy - target_energy|, never below 0.0."""
    return max(0.0, 1.0 - abs(song_energy - target_energy))


def weighted_score(genre: float, mood: float, energy: float) -> float:
    """Combines the three component values using the 40/30/30 weights."""
    return GENRE_WEIGHT * genre + MOOD_WEIGHT * mood + ENERGY_WEIGHT * energy


def score_features(
    song_genre: str,
    song_mood: str,
    song_energy: float,
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
) -> Tuple[float, List[str]]:
    """
    Scores one song's features against the user's preferences.
    Returns (score, reasons) where reasons is a list of readable strings.
    """
    g = genre_match(song_genre, favorite_genre)
    m = mood_match(song_mood, favorite_mood)
    e = energy_similarity(song_energy, target_energy)
    score = weighted_score(g, m, e)

    reasons = []
    if g:
        reasons.append(f"genre matches your favorite ({song_genre})")
    else:
        reasons.append(f"genre is {song_genre}, not {favorite_genre}")
    if m:
        reasons.append(f"mood matches your favorite ({song_mood})")
    else:
        reasons.append(f"mood is {song_mood}, not {favorite_mood}")
    reasons.append(
        f"energy {song_energy:.2f} is {e:.0%} similar to your target {target_energy:.2f}"
    )
    return score, reasons


# ---------------------------------------------------------------------------
# OOP version (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Scores a single Song for a UserProfile. Returns (score, reasons)."""
        return score_features(
            song.genre, song.mood, song.energy,
            user.favorite_genre, user.favorite_mood, user.target_energy,
        )

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top k songs, sorted from highest to lowest score."""
        if k <= 0:
            return []
        # sorted() is stable, so songs with equal scores keep their catalog order
        ranked = sorted(self.songs, key=lambda song: self.score(user, song)[0], reverse=True)
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a sentence explaining how the song's score was calculated."""
        score, reasons = self.score(user, song)
        return f"Score {score:.2f}: " + "; ".join(reasons) + "."


# ---------------------------------------------------------------------------
# Functional version (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded {len(songs)} songs.")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    user_prefs uses the keys "genre", "mood", and "energy".
    Returns (score, reasons).
    """
    return score_features(
        song["genre"], song["mood"], song["energy"],
        user_prefs["genre"], user_prefs["mood"], user_prefs["energy"],
    )

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Returns a list of (song_dict, score, explanation), highest score first.
    """
    if k <= 0:
        return []
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored.append((song, score, "; ".join(reasons)))
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
