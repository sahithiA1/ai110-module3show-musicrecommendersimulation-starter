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

The catalog in `data/songs.csv` contains **18 songs**. Each row has these columns:

| Column | Example | Description |
| --- | --- | --- |
| `id` | `1` | Unique song identifier |
| `title`, `artist` | `Sunrise City`, `Neon Echo` | Display information |
| `genre` | `pop`, `lofi`, `rock`, `jazz` | Musical category |
| `mood` | `happy`, `chill`, `intense` | Emotional label |
| `energy` | `0.82` | Intensity from 0.0 (calm) to 1.0 (energetic) |
| `tempo_bpm` | `118` | Tempo in beats per minute |
| `valence`, `danceability`, `acousticness` | `0.84`, `0.79`, `0.18` | Additional audio features from 0.0 to 1.0 |

The starter catalog had 10 songs. I added 8 fictional songs (IDs 11 to 18) to make the catalog more diverse. Each one is in a genre the original data did not include, and most use new moods:

| ID | Title | Genre | Mood | Energy |
| --- | --- | --- | --- | --- |
| 1 | Sunrise City | pop | happy | 0.82 |
| 2 | Midnight Coding | lofi | chill | 0.42 |
| 3 | Storm Runner | rock | intense | 0.91 |
| 4 | Library Rain | lofi | chill | 0.35 |
| 5 | Gym Hero | pop | intense | 0.93 |
| 6 | Spacewalk Thoughts | ambient | chill | 0.28 |
| 7 | Coffee Shop Stories | jazz | relaxed | 0.37 |
| 8 | Night Drive Loop | synthwave | moody | 0.75 |
| 9 | Focus Flow | lofi | focused | 0.40 |
| 10 | Rooftop Lights | indie pop | happy | 0.76 |
| 11 | Concrete Crown *(new)* | hip hop | confident | 0.78 |
| 12 | Dusty Porch Light *(new)* | country | nostalgic | 0.48 |
| 13 | Glass Garden Nocturne *(new)* | classical | peaceful | 0.18 |
| 14 | Iron Tempest *(new)* | metal | angry | 0.97 |
| 15 | Velvet Hours *(new)* | r&b | romantic | 0.55 |
| 16 | Pulse Horizon *(new)* | edm | energetic | 0.95 |
| 17 | Harbor Lullaby *(new)* | folk | sad | 0.30 |
| 18 | Island Time Radio *(new)* | reggae | happy | 0.60 |

The expanded catalog has 15 genres and 13 moods, and energy ranges from 0.18 to 0.97. It is still small and uneven: lofi has 3 songs, pop has 2, and every other genre has just 1.

### Song Features

A `Song` object represents one row of the catalog and stores every column above. The scoring logic uses three of them:

- `genre`: the song's category, such as `pop`, `lofi`, or `metal`
- `mood`: the song's emotional label, such as `happy`, `chill`, or `angry`
- `energy`: a number from 0.0 to 1.0 describing how energetic the song feels

The other features (`tempo_bpm`, `valence`, `danceability`, `acousticness`) are loaded but not scored. They are available for later experiments.

### UserProfile Features

A `UserProfile` object represents one listener's taste:

- `favorite_genre`: the genre the listener prefers, compared with `song.genre`
- `favorite_mood`: the mood the listener prefers, compared with `song.mood`
- `target_energy`: the energy level the listener wants, from 0.0 to 1.0, compared with `song.energy`
- `likes_acoustic`: whether the listener prefers acoustic songs (stored for future use and not part of the current formula)

The command-line runner in `src/main.py` uses the same preferences as a dictionary: `{"genre": "pop", "mood": "happy", "energy": 0.8}`.

### Is This Profile Enough?

**Strengths.** Genre, mood, and energy are enough to tell very different listeners apart. An "intense rock, energy 0.9" listener and a "chill lofi, energy 0.4" listener disagree on all three features, so their recommendations do not overlap at the top:

- For the lofi listener, Storm Runner (rock, intense, 0.91) scores only **0.147**.
- For the rock listener, Midnight Coding (lofi, chill, 0.42) scores only **0.156**.

The three features are also easy to understand, which makes every score easy to explain.

**Limitations.** The profile struggles with listeners whose tastes are *similar but not identical*:

- **Related genres count as complete misses.** For the rock listener, Iron Tempest (metal, angry, 0.97) is arguably the closest song in the catalog after Storm Runner, but it scores only 0.279 and ranks 4th. It gets no credit for genre (`metal` is not `rock`) or mood (`angry` is not `intense`).
- **Energy alone cannot separate some styles.** Gym Hero (pop, 0.93) and Storm Runner (rock, 0.91) have almost the same energy, so energy can't tell a workout-pop fan from a rock fan. Only the genre label separates them.
- **Useful features are ignored.** Rock and lofi also differ strongly in tempo (Storm Runner 152 BPM vs. Midnight Coding 78 BPM) and acousticness (0.10 vs. 0.71), but the score does not use them. `likes_acoustic` is stored but never used.
- **Only one favorite per feature.** A listener cannot say "rock *or* metal", give a range of energy levels, or mark genres they dislike.

### Algorithm Recipe

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

Genre and mood comparisons ignore uppercase letters and extra spaces. Because the weights add up to 1.0 and each component is between 0 and 1, every score falls between **0.0** (nothing matches and the energy is as far away as possible) and **1.0** (a perfect match). Energy similarity gives partial credit, so a song that is close to the target energy still earns most of those points.

**Example.** Suppose a user has `favorite_genre="lofi"`, `favorite_mood="chill"`, and `target_energy=0.40`.

| Song | Genre | Mood | Energy similarity | Score |
| --- | --- | --- | --- | --- |
| Midnight Coding (lofi, chill, 0.42) | 1 | 1 | 1 - 0.02 = 0.98 | 0.40 + 0.30 + 0.294 = **0.994** |
| Focus Flow (lofi, focused, 0.40) | 1 | 0 | 1 - 0.00 = 1.00 | 0.40 + 0.00 + 0.300 = **0.700** |
| Spacewalk Thoughts (ambient, chill, 0.28) | 0 | 1 | 1 - 0.12 = 0.88 | 0.00 + 0.30 + 0.264 = **0.564** |
| Storm Runner (rock, intense, 0.91) | 0 | 0 | 1 - 0.51 = 0.49 | 0.00 + 0.00 + 0.147 = **0.147** |

**Why this weighting works.** Genre is often the strongest single clue about whether someone will enjoy a song, so it gets the largest weight. Mood and energy together still make up 60% of the score, so a song in the right genre with the wrong feel won't automatically win. The formula is simple, predictable, and easy to explain: every score can be broken down into the three parts shown above.

### Potential Bias From Emphasizing Genre

Giving genre the largest weight builds in an assumption that genre matters most, and this has side effects:

- **Genre matches beat better-fitting songs.** Any song that matches both genre and mood scores at least 0.70. A song in a different genre can score at most 0.60, even with a perfect mood and energy match. For the pop listener, Gym Hero (pop, *intense*) scores 0.661 and outranks Rooftop Lights (0.588) and Island Time Radio (0.540), which both have the requested *happy* mood.
- **Popular genres in the catalog get more chances.** Lofi has 3 songs and pop has 2, so those listeners get several strong matches. Fans of the 13 genres with only one song get one strong match followed by low-scoring filler.
- **Exact labels penalize subgenres and blends.** `indie pop` gets no credit for a `pop` fan, and `metal` gets none for a `rock` fan, so songs that blend or sit between genres are pushed down.
- **The labels are a human choice.** Whoever writes the CSV decides each song's single genre and mood, and those decisions directly control the rankings.

### Scoring vs. Ranking

These are two separate steps:

- **Scoring** looks at **one song at a time** and answers, "How well does this song match the user?" It produces a single number using the formula above. A song's score does not depend on any other song in the catalog.
- **Ranking** looks at **all of the scores together** and answers, "Which songs should be shown first?" It sorts the songs from highest to lowest score and keeps the top `k`. Songs with the same score keep their order from the CSV.

Changing `k` only changes how many songs are returned from the top of the ranked list. It does not change any song's score.

### Data Flow

```text
 INPUT                        SCORING (each song)                 RANKING              OUTPUT
+------------------+        +-------------------------------+    +---------------+    +--------------+
| User preferences |        | genre_match      x 0.40       |    | sort all 18   |    | top k songs  |
| genre, mood,     | -----> | mood_match       x 0.30       | -> | scores from   | -> | with score + |
| energy           |        | energy_similarity x 0.30      |    | high to low   |    | explanation  |
+------------------+        | = score (0.0 to 1.0)          |    +---------------+    +--------------+
| data/songs.csv   | -----> |                               |
| (18 songs)       |        +-------------------------------+
+------------------+
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
Loaded 18 songs.

Top recommendations:

Sunrise City - Score: 0.99
Because: genre matches your favorite (pop); mood matches your favorite (happy); energy 0.82 is 98% similar to your target 0.80

Gym Hero - Score: 0.66
Because: genre matches your favorite (pop); mood is intense, not happy; energy 0.93 is 87% similar to your target 0.80

Rooftop Lights - Score: 0.59
Because: genre is indie pop, not pop; mood matches your favorite (happy); energy 0.76 is 96% similar to your target 0.80

Island Time Radio - Score: 0.54
Because: genre is reggae, not pop; mood matches your favorite (happy); energy 0.60 is 80% similar to your target 0.80

Concrete Crown - Score: 0.29
Because: genre is hip hop, not pop; mood is confident, not happy; energy 0.78 is 98% similar to your target 0.80
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

All scores below come from running `recommend_songs()` on the expanded 18-song `data/songs.csv` with the 40/30/30 weights. Scores are rounded to three decimals. I first ran these experiments on the original 10 songs, then reran all of them after adding 8 songs. The results here are from the rerun, and I note where a result changed.

### Experiment 1: Pop, happy, energy 0.8

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Sunrise City | pop / happy / 0.82 | 0.994 |
| 2 | Gym Hero | pop / intense / 0.93 | 0.661 |
| 3 | Rooftop Lights | indie pop / happy / 0.76 | 0.588 |

Sunrise City matches all three features. Gym Hero ranks second only because it shares the genre: the 0.40 genre weight beats Rooftop Lights' 0.30 mood match, even though Rooftop Lights is closer in energy (0.76 vs. 0.93) and has the right mood. Rooftop Lights gets no genre credit because `indie pop` is treated as a completely different string from `pop`.

After the catalog was expanded, the top 3 stayed the same. The new song Island Time Radio (reggae, happy, 0.60) is now 4th with 0.540: it matches the mood but has no genre credit and is further away in energy.

### Experiment 2: Lofi, chill, energy 0.4

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Midnight Coding | lofi / chill / 0.42 | 0.994 |
| 2 | Library Rain | lofi / chill / 0.35 | 0.985 |
| 3 | Focus Flow | lofi / focused / 0.40 | 0.700 |

The results move completely to the calm end of the catalog; none of the pop songs from Experiment 1 appear. This profile has the closest competition at the top because the catalog has three lofi songs and two of them are also `chill`, so energy similarity decides the order (0.42 is closer to 0.4 than 0.35 is). Focus Flow has a *perfect* energy match but loses 0.30 because its mood is `focused` instead of `chill`. Spacewalk Thoughts (ambient, chill) is fourth with 0.564, so a calm song in a different genre is held below every lofi song.

The top 3 stayed the same after the catalog was expanded. The new calm songs, Dusty Porch Light (country, 0.276), Harbor Lullaby (folk, 0.270), and Glass Garden Nocturne (classical, 0.234), all score below 0.30 because they match neither the genre nor the mood.

### Experiment 3: Rock, intense, energy 0.9

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Storm Runner | rock / intense / 0.91 | 0.997 |
| 2 | Gym Hero | pop / intense / 0.93 | 0.591 |
| 3 | Pulse Horizon | edm / energetic / 0.95 | 0.285 |

There is only one rock song, so after Storm Runner the scores drop sharply. Gym Hero is second because it shares the `intense` mood and has very similar energy. Third place, Pulse Horizon, scores only 0.285: it earns points from energy alone and is recommended mostly because nothing better exists. This shows how a small catalog limits users whose favorite genre is rare.

**What changed after the expansion:** on the original 10 songs, third place was Sunrise City (0.276). Now Pulse Horizon (edm) takes third, and Iron Tempest (metal, angry, 0.97) is 4th with 0.279. Many listeners would call the metal song the closest match to intense rock, but it gets no genre or mood credit, so it can only compete on energy.

### Why the recommendations changed

The three profiles produced three completely different #1 songs, and each top song matched all three preferences. Below the top match, the ranking follows a clear pattern caused by the weights:

1. Songs that match **genre** (worth 0.40) come next.
2. Then songs that match **mood** (worth 0.30).
3. Songs that match neither are sorted only by **energy**, and their scores stay below 0.30.

### Experiment 4: Changing the weights

To test how much the weights matter, I temporarily changed the weights to **genre 0.2 / mood 0.3 / energy 0.5** in a separate script, without changing `src/recommender.py`.

| Profile | Top 3 with 0.4 / 0.3 / 0.3 | Top 3 with 0.2 / 0.3 / 0.5 |
| --- | --- | --- |
| Pop, happy, 0.8 | Sunrise City (0.994), Gym Hero (0.661), Rooftop Lights (0.588) | Sunrise City (0.990), **Rooftop Lights (0.780)**, **Island Time Radio (0.700)** |
| Lofi, chill, 0.4 | Midnight Coding (0.994), Library Rain (0.985), Focus Flow (0.700) | Midnight Coding (0.990), Library Rain (0.975), **Spacewalk Thoughts (0.740)** |
| Rock, intense, 0.9 | Storm Runner (0.997), Gym Hero (0.591), Pulse Horizon (0.285) | Storm Runner (0.995), Gym Hero (0.785), Pulse Horizon (0.475) |

With less weight on genre, songs from *other* genres that match the mood and energy move up. For the pop listener, Rooftop Lights (indie pop) and Island Time Radio (reggae) both pass Gym Hero, so Gym Hero (pop, intense) drops out of the top 3. For the lofi listener, Spacewalk Thoughts (ambient) replaces Focus Flow (lofi). The #1 songs did not change. The weights mostly decide how strongly the system sticks to a single genre.

### Experiment 5: A genre that is not in the catalog

On the original 10 songs, a profile of **hip hop, happy, energy 0.7** returned Rooftop Lights (0.582), Sunrise City (0.564), and Night Drive Loop (0.285). No song could earn the 0.40 genre points, so the best possible score was 0.60, and the recommendations were based only on mood and energy.

After the expansion, the catalog has one hip hop song, and the same profile returns:

| Rank | Song | Genre / Mood / Energy | Score |
| --- | --- | --- | --- |
| 1 | Concrete Crown | hip hop / confident / 0.78 | 0.676 |
| 2 | Rooftop Lights | indie pop / happy / 0.76 | 0.582 |
| 3 | Island Time Radio | reggae / happy / 0.60 | 0.570 |

Adding a single song in the user's genre immediately put it in first place, even though its mood (`confident`) does not match. This shows how much the results depend on what is in the catalog.

### Experiment 6: Adversarial profile (folk, sad, energy 0.9)

Sad folk music is usually quiet, and the catalog's only folk song, which is also its only sad song, has energy 0.30. Asking for sad folk at energy 0.9 is a contradiction that no song can satisfy. Actual output:

```text
1. Harbor Lullaby (folk, sad, 0.30) - Score: 0.820
   Because: genre matches your favorite (folk); mood matches your favorite (sad); energy 0.30 is 40% similar to your target 0.90
2. Storm Runner (rock, intense, 0.91) - Score: 0.297
   Because: genre is rock, not folk; mood is intense, not sad; energy 0.91 is 99% similar to your target 0.90
3. Gym Hero (pop, intense, 0.93) - Score: 0.291
   Because: genre is pop, not folk; mood is intense, not sad; energy 0.93 is 97% similar to your target 0.90
4. Pulse Horizon (edm, energetic, 0.95) - Score: 0.285
   Because: genre is edm, not folk; mood is energetic, not sad; energy 0.95 is 95% similar to your target 0.90
5. Iron Tempest (metal, angry, 0.97) - Score: 0.279
   Because: genre is metal, not folk; mood is angry, not sad; energy 0.97 is 93% similar to your target 0.90
```

The two label matches give the quiet ballad a high-looking 0.820 even though its energy is far from the target. The rest of the list is sorted by energy alone, and four of those five songs also appear in the rock listener's top 5. The system never tells the user that their preferences conflict.

### Experiment 7: Halving genre, doubling energy (normalized)

I reran the four Phase 4 profiles with genre 0.20, mood 0.30, energy 0.60, normalized to **0.182 / 0.273 / 0.545** because the raw values add up to 1.10. The experiment ran in a temporary script, and `src/recommender.py` still uses 40/30/30.

| Profile | #1 changed? | Main change in the top 5 |
| --- | --- | --- |
| High-Energy Pop | No (Sunrise City) | Gym Hero fell from #2 to #4; Rooftop Lights and Island Time Radio moved up |
| Chill Lofi | No (Midnight Coding) | Spacewalk Thoughts (ambient, chill) passed Focus Flow (lofi, focused) |
| Deep Intense Rock | No (Storm Runner) | Same order; Gym Hero rose from 0.591 to 0.802 |
| Conflicting Preferences | No (Harbor Lullaby) | Same order; Harbor Lullaby's lead shrank from 0.523 to 0.133 |

Full outputs, score breakdowns, and six pairwise profile comparisons are in section 7 of the [model card](model_card.md).

---

## Limitations and Risks

- **Exact-match genre and mood labels.** Genre and mood are either a perfect match or worth nothing. `indie pop` gets zero genre credit for a `pop` fan, `metal` gets none for a `rock` fan, and `relaxed` or `focused` get zero mood credit for a `chill` fan, even though these labels are closely related. The system has no idea which genres or moods are similar to each other.
- **Very small dataset.** Even after the expansion, the catalog has only 18 songs. Lofi has 3 songs and pop has 2, while the other 13 genres have only one each. A rock fan gets one strong recommendation and then weak filler (Experiment 3). Experiment 5 showed that adding one hip hop song completely changed that listener's #1 result. Results reflect what happens to be in the CSV more than the user's actual taste.
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



