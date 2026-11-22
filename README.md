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

Output of `python -m src.main` using the default profile in `src/main.py` (`genre="pop"`, `mood="happy"`, `energy=0.8`, `k=5`):

```text
Loading songs from data/songs.csv...
Loaded 10 songs.

Top recommendations:

Sunrise City - Score: 0.99
Because: genre matches your favorite (pop); mood matches your favorite (happy); energy 0.82 is 98% similar to your target 0.80

Gym Hero - Score: 0.66
Because: genre matches your favorite (pop); mood is intense, not happy; energy 0.93 is 87% similar to your target 0.80

Rooftop Lights - Score: 0.59
Because: genre is indie pop, not pop; mood matches your favorite (happy); energy 0.76 is 96% similar to your target 0.80

Night Drive Loop - Score: 0.28
Because: genre is synthwave, not pop; mood is moody, not happy; energy 0.75 is 95% similar to your target 0.80

Storm Runner - Score: 0.27
Because: genre is rock, not pop; mood is intense, not happy; energy 0.91 is 89% similar to your target 0.80
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

All scores below come from running `recommend_songs()` on `data/songs.csv` with the 40/30/30 weights. Scores are rounded to three decimals.

### Experiment 1: Pop, happy, energy 0.8

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Sunrise City | pop / happy / 0.82 | 0.994 |
| 2 | Gym Hero | pop / intense / 0.93 | 0.661 |
| 3 | Rooftop Lights | indie pop / happy / 0.76 | 0.588 |

Sunrise City matches all three features. Gym Hero ranks second only because it shares the genre: the 0.40 genre weight beats Rooftop Lights' 0.30 mood match, even though Rooftop Lights is closer in energy (0.76 vs. 0.93) and has the right mood. Rooftop Lights gets no genre credit because `indie pop` is treated as a completely different string from `pop`.

### Experiment 2: Lofi, chill, energy 0.4

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Midnight Coding | lofi / chill / 0.42 | 0.994 |
| 2 | Library Rain | lofi / chill / 0.35 | 0.985 |
| 3 | Focus Flow | lofi / focused / 0.40 | 0.700 |

The results move completely to the calm end of the catalog; none of the pop songs from Experiment 1 appear. This profile has the closest competition at the top because the catalog has three lofi songs and two of them are also `chill`, so energy similarity decides the order (0.42 is closer to 0.4 than 0.35 is). Focus Flow has a *perfect* energy match but loses 0.30 because its mood is `focused` instead of `chill`. Spacewalk Thoughts (ambient, chill) is fourth with 0.564, so a calm song in a different genre is held below every lofi song.

### Experiment 3: Rock, intense, energy 0.9

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Storm Runner | rock / intense / 0.91 | 0.997 |
| 2 | Gym Hero | pop / intense / 0.93 | 0.591 |
| 3 | Sunrise City | pop / happy / 0.82 | 0.276 |

There is only one rock song, so after Storm Runner the scores drop sharply. Gym Hero is second because it shares the `intense` mood and has very similar energy. Third place, Sunrise City, scores only 0.276: it earns points from energy alone and is recommended mostly because nothing better exists. This shows how a small catalog limits users whose favorite genre is rare.

### Why the recommendations changed

The three profiles produced three completely different #1 songs, and each top song matched all three preferences. Below the top match, the ranking follows a clear pattern caused by the weights:

1. Songs that match **genre** (worth 0.40) come next.
2. Then songs that match **mood** (worth 0.30).
3. Songs that match neither are sorted only by **energy**, and their scores stay below 0.30.

### Experiment 4: Changing the weights

To test how much the weights matter, I temporarily changed the weights to **genre 0.2 / mood 0.3 / energy 0.5** in a separate script, without changing `src/recommender.py`.

| Profile | Top 3 with 0.4 / 0.3 / 0.3 | Top 3 with 0.2 / 0.3 / 0.5 |
| --- | --- | --- |
| Pop, happy, 0.8 | Sunrise City (0.994), Gym Hero (0.661), Rooftop Lights (0.588) | Sunrise City (0.990), **Rooftop Lights (0.780)**, Gym Hero (0.635) |
| Lofi, chill, 0.4 | Midnight Coding (0.994), Library Rain (0.985), Focus Flow (0.700) | Midnight Coding (0.990), Library Rain (0.975), **Spacewalk Thoughts (0.740)** |
| Rock, intense, 0.9 | Storm Runner (0.997), Gym Hero (0.591), Sunrise City (0.276) | Storm Runner (0.995), Gym Hero (0.785), Sunrise City (0.460) |

With less weight on genre, songs from *other* genres that match the mood and energy move up: Rooftop Lights passes Gym Hero, and Spacewalk Thoughts (ambient) replaces Focus Flow (lofi). The #1 songs did not change. The weights mostly decide how strongly the system sticks to a single genre.

### Experiment 5: A genre that is not in the catalog

A profile of **hip hop, happy, energy 0.7** returned Rooftop Lights (0.582), Sunrise City (0.564), and Night Drive Loop (0.285). No song can earn the 0.40 genre points, so the best possible score for this user is 0.60, and the recommendations are based only on mood and energy.

---

## Limitations and Risks

- **Exact-match genre and mood labels.** Genre and mood are either a perfect match or worth nothing. `indie pop` gets zero genre credit for a `pop` fan, and `relaxed` or `focused` get zero mood credit for a `chill` fan, even though these labels are closely related. The system has no idea which genres or moods are similar to each other.
- **Very small dataset.** The catalog has only 10 songs. Some genres have several songs (3 lofi, 2 pop), while rock, jazz, ambient, synthwave, and indie pop have only one each. A rock fan gets one strong recommendation and then weak filler (Experiment 3), and a hip hop fan can never score above 0.60 (Experiment 5). Results reflect what happens to be in the CSV more than the user's actual taste.
- **The 40/30/30 weights shape everything.** Because genre is worth more than mood, a song in the right genre with the wrong mood usually beats a song in the wrong genre with the right mood (Gym Hero over Rooftop Lights). Experiment 4 showed that changing the weights reorders the results. The weights were chosen by hand, not learned from real listener data, so they reflect a design assumption that genre matters most.
- **No real listening history.** The recommender only knows three stated preferences. It does not use likes, skips, replays, or playlists, so it cannot learn that a user actually skips a song it recommended, and it cannot discover tastes the user did not describe. Everyone with the same three preferences gets the exact same list.
- **Limited musical diversity.** Only genre, mood, and energy are scored. Tempo, valence, danceability, acousticness, lyrics, language, and artist are ignored (including the stored `likes_acoustic` preference). The catalog itself covers a narrow set of mostly Western, English-titled genres, so many listeners' music is not represented at all.
- **Filter bubbles.** Because the top results always repeat the user's favorite genre and mood, the system keeps showing more of the same and rarely introduces something new. In a real app, the user would mostly click on these familiar songs, which would reinforce the same preferences over time. There is no element of exploration or variety in the ranking.
- **Ties and ordering.** Songs with equal scores keep their order from the CSV, so position in the file can quietly affect which song is shown first.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



