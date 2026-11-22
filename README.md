# 🎵 Music Recommender Simulation

## Project Summary

This project builds a small music recommender that predicts which songs in `data/songs.csv` a listener is likely to enjoy. It uses **content-based filtering**: every song is described by attributes such as genre, mood, and energy, and a `UserProfile` records the kind of music the listener prefers. The recommender compares each song with the profile, gives it a score, and returns the best matches.

Scoring uses a weighted formula in which genre counts for 40%, mood for 30%, and energy similarity for 30%. This makes the system a simplified, transparent version of how real music platforms turn song and listener data into recommendations.

### How Real Platforms Recommend Music

Platforms such as Spotify and YouTube combine two main approaches:

- **Collaborative filtering** learns from the behavior of many listeners. Likes, skips, replays, playlist additions, follows, and watch or listen time are all signals. If many people who saved song A also saved song B, a listener who likes A is likely to be shown B. A skip within the first few seconds is a strong negative signal, while adding a track to a playlist is a strong positive one. This approach answers: *"What did listeners similar to you enjoy?"*
- **Content-based filtering** compares the items themselves. It uses song attributes such as genre, mood, tempo, and audio features like energy, danceability, valence, and acousticness, plus metadata such as artist or title. This approach answers: *"What sounds similar to what you already like?"*

Each approach covers the other's weaknesses. Collaborative filtering struggles with brand-new songs that nobody has played yet (the *cold-start* problem), while content-based filtering can recommend them immediately from their attributes. Real systems blend both kinds of signals with context such as time of day, device, and recent listening. This project implements only the content-based side.

---

## How The System Works

### Data

The catalog in `data/songs.csv` contains 10 songs. Each row has these columns:

| Column | Example | Description |
| --- | --- | --- |
| `id` | `1` | Unique song identifier |
| `title`, `artist` | `Sunrise City`, `Neon Echo` | Display information |
| `genre` | `pop`, `lofi`, `rock`, `jazz` | Musical category |
| `mood` | `happy`, `chill`, `intense` | Emotional label |
| `energy` | `0.82` | Intensity from 0.0 (calm) to 1.0 (energetic) |
| `tempo_bpm` | `118` | Tempo in beats per minute |
| `valence`, `danceability`, `acousticness` | `0.84`, `0.79`, `0.18` | Additional audio features from 0.0 to 1.0 |

### Song Features

A `Song` object represents one row of the catalog and stores every column above. The first version of the scoring logic uses three of them:

- `genre`: the song's category, such as `pop`, `lofi`, or `ambient`
- `mood`: the song's emotional label, such as `happy`, `chill`, or `moody`
- `energy`: a number from 0.0 to 1.0 describing how energetic the song feels

The other features (`tempo_bpm`, `valence`, `danceability`, `acousticness`) are loaded but not scored yet. They are available for later experiments.

### UserProfile Features

A `UserProfile` object represents one listener's taste:

- `favorite_genre`: the genre the listener prefers, compared with `song.genre`
- `favorite_mood`: the mood the listener prefers, compared with `song.mood`
- `target_energy`: the energy level the listener wants, from 0.0 to 1.0, compared with `song.energy`
- `likes_acoustic`: whether the listener prefers acoustic songs (stored for future use and not part of the current formula)

### Scoring a Song

The recommender compares every song with the profile and turns each feature comparison into a value between 0 and 1:

| Component | Rule | Weight |
| --- | --- | --- |
| Genre match | `1` if `song.genre == user.favorite_genre`, otherwise `0` | 40% |
| Mood match | `1` if `song.mood == user.favorite_mood`, otherwise `0` | 30% |
| Energy similarity | `1 - abs(song.energy - user.target_energy)` | 30% |

The final score is the weighted sum:

```text
score = 0.40 * genre_match + 0.30 * mood_match + 0.30 * energy_similarity
```

Because the weights add up to 1.0 and each component is between 0 and 1, every score falls between **0.0** (nothing matches and the energy is as far away as possible) and **1.0** (a perfect match). Genre has the largest weight, so it has the strongest influence. Energy similarity gives partial credit, so a song that is close to the target energy still earns most of those points.

**Example.** Suppose a user has `favorite_genre="lofi"`, `favorite_mood="chill"`, and `target_energy=0.40`.

| Song | Genre | Mood | Energy similarity | Score |
| --- | --- | --- | --- | --- |
| Midnight Coding (lofi, chill, 0.42) | 1 | 1 | 1 - 0.02 = 0.98 | 0.40 + 0.30 + 0.294 = **0.994** |
| Focus Flow (lofi, focused, 0.40) | 1 | 0 | 1 - 0.00 = 1.00 | 0.40 + 0.00 + 0.300 = **0.700** |
| Spacewalk Thoughts (ambient, chill, 0.28) | 0 | 1 | 1 - 0.12 = 0.88 | 0.00 + 0.30 + 0.264 = **0.564** |
| Storm Runner (rock, intense, 0.91) | 0 | 0 | 1 - 0.51 = 0.49 | 0.00 + 0.00 + 0.147 = **0.147** |

### Scoring vs. Ranking

These are two separate steps:

- **Scoring** looks at **one song at a time** and answers, "How well does this song match the user?" It produces a single number using the formula above. A song's score does not depend on any other song in the catalog.
- **Ranking** looks at **all of the scores together** and answers, "Which songs should be shown first?" It sorts the songs from highest to lowest score and keeps the top `k`.

Changing `k` only changes how many songs are returned from the top of the ranked list. It does not change any song's score. In the example above, asking for `k=2` returns Midnight Coding and Focus Flow.

The full flow is:

```text
UserProfile + each Song -> score each song -> sort by score (descending) -> return top k
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies:

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

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
# e.g.:
# User profile: genre=indie, mood=chill, energy=low
# Recommendations:
#   1. ...
#   2. ...
#   3. ...
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

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

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



