import pytest

from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    genre_match,
    mood_match,
    energy_similarity,
    weighted_score,
    load_songs,
    score_song,
    recommend_songs,
)


def make_song(id, genre, mood, energy, title=None) -> Song:
    return Song(
        id=id,
        title=title or f"Song {id}",
        artist="Test Artist",
        genre=genre,
        mood=mood,
        energy=energy,
        tempo_bpm=100,
        valence=0.5,
        danceability=0.5,
        acousticness=0.5,
    )


LOFI_USER = UserProfile(
    favorite_genre="lofi",
    favorite_mood="chill",
    target_energy=0.4,
    likes_acoustic=True,
)


# --- Component scores -------------------------------------------------------

def test_genre_match():
    assert genre_match("pop", "pop") == 1.0
    assert genre_match("Pop ", "pop") == 1.0
    assert genre_match("rock", "pop") == 0.0
    # "indie pop" is a different genre than "pop"
    assert genre_match("indie pop", "pop") == 0.0


def test_mood_match():
    assert mood_match("chill", "chill") == 1.0
    assert mood_match("CHILL", "chill") == 1.0
    assert mood_match("intense", "chill") == 0.0


def test_energy_similarity():
    assert energy_similarity(0.8, 0.8) == pytest.approx(1.0)
    assert energy_similarity(0.42, 0.40) == pytest.approx(0.98)
    assert energy_similarity(0.91, 0.40) == pytest.approx(0.49)
    assert energy_similarity(0.0, 1.0) == pytest.approx(0.0)
    # Symmetric: order of arguments does not matter
    assert energy_similarity(0.3, 0.7) == pytest.approx(energy_similarity(0.7, 0.3))


def test_weighted_score():
    assert weighted_score(1, 1, 1) == pytest.approx(1.0)
    assert weighted_score(0, 0, 0) == pytest.approx(0.0)
    assert weighted_score(1, 0, 0) == pytest.approx(0.4)
    assert weighted_score(0, 1, 0) == pytest.approx(0.3)
    assert weighted_score(0, 0, 1) == pytest.approx(0.3)
    assert weighted_score(1, 1, 0.8) == pytest.approx(0.94)


def test_recommender_score_matches_readme_example():
    rec = Recommender([])
    cases = [
        (make_song(1, "lofi", "chill", 0.42), 0.994),
        (make_song(2, "lofi", "focused", 0.40), 0.700),
        (make_song(3, "ambient", "chill", 0.28), 0.564),
        (make_song(4, "rock", "intense", 0.91), 0.147),
    ]
    for song, expected in cases:
        score, reasons = rec.score(LOFI_USER, song)
        assert score == pytest.approx(expected)
        assert len(reasons) == 3


# --- Ranking and top-k ------------------------------------------------------

def test_recommend_ranks_highest_score_first():
    songs = [
        make_song(1, "rock", "intense", 0.91),   # 0.147
        make_song(2, "ambient", "chill", 0.28),  # 0.564
        make_song(3, "lofi", "chill", 0.42),     # 0.994
        make_song(4, "lofi", "focused", 0.40),   # 0.700
    ]
    results = Recommender(songs).recommend(LOFI_USER, k=4)
    assert [s.id for s in results] == [3, 4, 2, 1]


def test_recommend_returns_top_k():
    songs = [make_song(i, "lofi", "chill", i / 10) for i in range(1, 10)]
    results = Recommender(songs).recommend(LOFI_USER, k=3)
    assert len(results) == 3
    # Closest energies to 0.4 are 0.4, then 0.3 and 0.5 (tie keeps catalog order)
    assert [s.id for s in results] == [4, 3, 5]


def test_recommend_k_larger_than_catalog_returns_all():
    songs = [make_song(1, "pop", "happy", 0.8), make_song(2, "lofi", "chill", 0.4)]
    assert len(Recommender(songs).recommend(LOFI_USER, k=10)) == 2


def test_recommend_k_zero_or_negative_returns_empty():
    songs = [make_song(1, "lofi", "chill", 0.4)]
    assert Recommender(songs).recommend(LOFI_USER, k=0) == []
    assert Recommender(songs).recommend(LOFI_USER, k=-1) == []


def test_recommend_empty_song_list():
    assert Recommender([]).recommend(LOFI_USER, k=5) == []


def test_recommend_does_not_reorder_original_catalog():
    songs = [make_song(1, "rock", "intense", 0.9), make_song(2, "lofi", "chill", 0.4)]
    rec = Recommender(songs)
    rec.recommend(LOFI_USER, k=2)
    assert [s.id for s in rec.songs] == [1, 2]


def test_explain_recommendation_mentions_matches():
    song = make_song(1, "lofi", "chill", 0.42)
    explanation = Recommender([song]).explain_recommendation(LOFI_USER, song)
    assert "0.99" in explanation
    assert "genre matches" in explanation
    assert "mood matches" in explanation
    assert "energy" in explanation


def test_explain_recommendation_mentions_mismatches():
    song = make_song(1, "rock", "intense", 0.91)
    explanation = Recommender([song]).explain_recommendation(LOFI_USER, song)
    assert "not lofi" in explanation
    assert "not chill" in explanation


# --- Functional version used by src/main.py ---------------------------------

def test_load_songs_reads_catalog():
    songs = load_songs("data/songs.csv")
    assert len(songs) == 10
    first = songs[0]
    assert first["title"] == "Sunrise City"
    assert first["genre"] == "pop"
    assert isinstance(first["id"], int)
    assert first["energy"] == pytest.approx(0.82)


def test_score_song_returns_score_and_reasons():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.82}
    score, reasons = score_song(prefs, song)
    assert score == pytest.approx(0.994)
    assert isinstance(reasons, list) and len(reasons) == 3


def test_recommend_songs_on_real_catalog():
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}
    results = recommend_songs(prefs, load_songs("data/songs.csv"), k=3)
    assert len(results) == 3
    titles = [song["title"] for song, _, _ in results]
    assert titles[0] == "Sunrise City"
    scores = [score for _, score, _ in results]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(explanation, str) and explanation for _, _, explanation in results)


def test_recommend_songs_empty_list():
    assert recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, [], k=5) == []
