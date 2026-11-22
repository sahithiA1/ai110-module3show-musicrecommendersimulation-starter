# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

### The big idea: content-based filtering

The recommender uses **content-based filtering**. That means it recommends songs by looking at what the songs are like, not at what other people listened to. If you tell it what kind of music you want, it looks through the catalog for songs whose descriptions are closest to your request.

### What it knows about each song

Every song in the catalog has several descriptions, but the recommender pays attention to three of them:

- **Genre**: the style of music, such as pop, lofi, rock, or jazz.
- **Mood**: the feeling of the song, such as happy, chill, or intense.
- **Energy**: a number from 0.0 (very calm) to 1.0 (very energetic).

The catalog also lists tempo, valence (how positive a song sounds), danceability, and acousticness, but this version does not use them.

### What it knows about the listener

The listener gives three preferences that line up with the song features:

- a **favorite genre**
- a **favorite mood**
- a **target energy level** between 0.0 and 1.0

The listener profile also remembers whether the person likes acoustic music, but that preference is not used in the score yet.

### Step 1: Scoring each song

The recommender gives every song a score from 0.0 to 1.0 by asking three questions:

1. **Is it the right genre?** If yes, the song earns the full genre points. If no, it earns none. Genre is worth **40%** of the score, the largest share, because genre is usually the strongest clue about whether someone will like a song.
2. **Is it the right mood?** If yes, the song earns the full mood points. If no, it earns none. Mood is worth **30%**.
3. **How close is the energy?** This one gives partial credit. The recommender measures the gap between the song's energy and the listener's target and subtracts it from 1. A perfect match earns all of the energy points, and a small gap still earns most of them. Energy is worth **30%**.

The three parts are added together. For example, if a lofi fan who wants chill music at energy 0.40 is matched against a lofi, chill song with energy 0.42, the song gets all of the genre points (0.40), all of the mood points (0.30), and almost all of the energy points (0.98 of 0.30, which is 0.294), for a total of 0.994 out of 1.0.

Each song is scored on its own. A song's score does not depend on which other songs are in the catalog.

### Step 2: Ranking and returning the top k songs

After every song has a score, the recommender lines them up from highest to lowest score and returns the top few. The number of songs returned is called **k**. Asking for 5 recommendations returns the 5 highest-scoring songs. Changing k only changes how many songs you get back; it never changes anyone's score. If two songs tie, they stay in the same order they appear in the catalog. If there are no songs, or if k is zero, the recommender returns an empty list instead of crashing.

### Step 3: Explaining each recommendation

Along with each song and its score, the recommender explains how it got that score in plain language. For each feature, it says whether the genre matched, whether the mood matched, and how similar the energy was as a percentage. For example:

> genre matches your favorite (pop); mood is intense, not happy; energy 0.93 is 87% similar to your target 0.80

Because the score is just the sum of three understandable parts, the user can always see exactly why one song ranked above another.

### Changes from the starter logic

The starter code returned the first few songs in the file and a placeholder explanation. I replaced that with the weighted scoring, ranking, and explanation steps described above, and I made the song loader read the real catalog file. Genre and mood comparisons ignore uppercase letters and extra spaces, so "Pop" and "pop" count as the same genre.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The biggest weakness is that genre and mood are scored as exact, all-or-nothing labels, so one label match can outweigh how a song actually sounds. In the Conflicting Preferences test (folk, sad, energy 0.9), Harbor Lullaby ranked #1 with a confident-looking 0.82 even though its energy (0.30) is only 40% similar to what the user asked for. Every song after it scored below 0.30 and was ranked by energy alone, so the user got either a quiet folk ballad or loud rock, pop, EDM, and metal tracks with nothing sad about them. The small catalog makes this worse: 13 of the 15 genres have only one song, so listeners with those favorite genres get one strong match followed by filler, while lofi (3 songs) and pop (2 songs) listeners get several real options. The explanation text also never warns the user that their preferences conflict or that the catalog has nothing that fits all of them.

Other limitations found while reviewing `src/recommender.py` and `data/songs.csv`:

- **Exact-match labels.** `indie pop` gets no credit for a `pop` fan, `metal` gets none for a `rock` fan, and `relaxed` or `focused` get none for a `chill` fan.
- **Filter bubble.** Because a genre match is worth 0.40, the top results keep repeating the user's stated genre. There is no exploration or diversity step, and the system cannot learn anything new about the user.
- **Underrepresented genres.** Ambient, jazz, synthwave, hip hop, country, classical, metal, r&b, edm, folk, reggae, rock, and indie pop each have one song. The catalog is also mostly Western genres.
- **Conflicting preferences.** The scoring adds features independently, so it cannot detect that "sad" and "energy 0.9" rarely appear together in this catalog.
- **Energy similarity is soft and linear.** `1 - |difference|` gives a lot of partial credit: even the worst possible match for a 0.9 target (Glass Garden Nocturne, 0.18) still gets 28% similarity. Songs that miss on genre and mood all land between about 0.2 and 0.3, so those positions in the list are decided by tiny energy differences.
- **Unused features.** `tempo_bpm`, `valence`, `danceability`, `acousticness`, and the `likes_acoustic` preference are loaded but never scored. Valence would be a natural way to tell a "sad" song from an "intense" one.
- **No listening history.** The model uses only three stated preferences. It has no likes, skips, replays, or playlists, so it cannot correct mistakes, and everyone with the same three preferences gets the same list.

---

## 7. Evaluation  

### Profiles tested

I ran the real `recommend_songs()` function (40% genre / 30% mood / 30% energy, `k=5`) on the 18-song catalog for four profiles:

| Profile | Genre | Mood | Energy | Purpose |
| --- | --- | --- | --- | --- |
| High-Energy Pop | pop | happy | 0.8 | Typical listener whose genre has 2 songs |
| Chill Lofi | lofi | chill | 0.4 | Typical listener whose genre has 3 songs |
| Deep Intense Rock | rock | intense | 0.9 | Listener whose genre has only 1 song |
| Conflicting Preferences | folk | sad | 0.9 | Adversarial edge case |

**Why the fourth profile is adversarial.** Sad folk music is usually quiet and slow, and the only folk song in the catalog (Harbor Lullaby) is also the only sad song, with energy 0.30. Asking for sad folk at energy 0.9 creates a preference that no song can satisfy. This tests whether the recommender handles a contradiction sensibly or hides it behind a high score.

### Actual results (40 / 30 / 30)

These outputs were captured from running the recommender. Scores are shown to three decimals.

**1. High-Energy Pop** (`genre=pop, mood=happy, energy=0.8`)

```text
1. Sunrise City (pop, happy, 0.82) - Score: 0.994
   Because: genre matches your favorite (pop); mood matches your favorite (happy); energy 0.82 is 98% similar to your target 0.80
2. Gym Hero (pop, intense, 0.93) - Score: 0.661
   Because: genre matches your favorite (pop); mood is intense, not happy; energy 0.93 is 87% similar to your target 0.80
3. Rooftop Lights (indie pop, happy, 0.76) - Score: 0.588
   Because: genre is indie pop, not pop; mood matches your favorite (happy); energy 0.76 is 96% similar to your target 0.80
4. Island Time Radio (reggae, happy, 0.60) - Score: 0.540
   Because: genre is reggae, not pop; mood matches your favorite (happy); energy 0.60 is 80% similar to your target 0.80
5. Concrete Crown (hip hop, confident, 0.78) - Score: 0.294
   Because: genre is hip hop, not pop; mood is confident, not happy; energy 0.78 is 98% similar to your target 0.80
```

**2. Chill Lofi** (`genre=lofi, mood=chill, energy=0.4`)

```text
1. Midnight Coding (lofi, chill, 0.42) - Score: 0.994
   Because: genre matches your favorite (lofi); mood matches your favorite (chill); energy 0.42 is 98% similar to your target 0.40
2. Library Rain (lofi, chill, 0.35) - Score: 0.985
   Because: genre matches your favorite (lofi); mood matches your favorite (chill); energy 0.35 is 95% similar to your target 0.40
3. Focus Flow (lofi, focused, 0.40) - Score: 0.700
   Because: genre matches your favorite (lofi); mood is focused, not chill; energy 0.40 is 100% similar to your target 0.40
4. Spacewalk Thoughts (ambient, chill, 0.28) - Score: 0.564
   Because: genre is ambient, not lofi; mood matches your favorite (chill); energy 0.28 is 88% similar to your target 0.40
5. Coffee Shop Stories (jazz, relaxed, 0.37) - Score: 0.291
   Because: genre is jazz, not lofi; mood is relaxed, not chill; energy 0.37 is 97% similar to your target 0.40
```

**3. Deep Intense Rock** (`genre=rock, mood=intense, energy=0.9`)

```text
1. Storm Runner (rock, intense, 0.91) - Score: 0.997
   Because: genre matches your favorite (rock); mood matches your favorite (intense); energy 0.91 is 99% similar to your target 0.90
2. Gym Hero (pop, intense, 0.93) - Score: 0.591
   Because: genre is pop, not rock; mood matches your favorite (intense); energy 0.93 is 97% similar to your target 0.90
3. Pulse Horizon (edm, energetic, 0.95) - Score: 0.285
   Because: genre is edm, not rock; mood is energetic, not intense; energy 0.95 is 95% similar to your target 0.90
4. Iron Tempest (metal, angry, 0.97) - Score: 0.279
   Because: genre is metal, not rock; mood is angry, not intense; energy 0.97 is 93% similar to your target 0.90
5. Sunrise City (pop, happy, 0.82) - Score: 0.276
   Because: genre is pop, not rock; mood is happy, not intense; energy 0.82 is 92% similar to your target 0.90
```

**4. Conflicting Preferences** (`genre=folk, mood=sad, energy=0.9`)

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

### What matched musical intuition

- Each of the three typical profiles got a #1 song that matches all three preferences (Sunrise City, Midnight Coding, Storm Runner), each scoring above 0.99.
- The Chill Lofi list is the most convincing: the top four are all calm songs between 0.28 and 0.42 energy, and both lofi/chill songs come first.
- The pop and lofi listeners, who disagree on everything, share no songs in their top 5.
- Rooftop Lights (indie pop, happy) and Island Time Radio (reggae, happy) are reasonable picks for a happy pop listener.

### What was surprising

- **Gym Hero beats happier songs for the pop listener.** Gym Hero is an intense workout track, but it ranks #2 for "happy pop" ahead of Rooftop Lights, which matches the mood and is closer in energy. The genre label alone is worth more than the mood match.
- **Iron Tempest ranks below an EDM track for the rock listener.** Many people would call metal the closest style to intense rock, but `metal` and `angry` earn no credit, so Iron Tempest (0.279) falls behind Pulse Horizon (0.285) by a tiny energy difference.
- **Sunrise City, a happy pop song, appears in the rock top 5.** It is there only because the catalog has nothing better; its 0.276 score is almost entirely energy.
- **The conflicting profile gets a high score for a poor fit.** Harbor Lullaby scores 0.820, which looks like a strong match, but it is a quiet song for someone who asked for energy 0.9. The other four results contain nothing folk and nothing sad.

### Explaining one score: Gym Hero for High-Energy Pop

Gym Hero is pop, intense, energy 0.93. Against `pop / happy / 0.8`:

```text
genre  : pop == pop          -> 1  x 0.40 = 0.400
mood   : intense != happy    -> 0  x 0.30 = 0.000
energy : 1 - |0.93 - 0.80|   -> 0.87 x 0.30 = 0.261
total                                       = 0.661
```

Rooftop Lights gets `0 + 0.300 + 0.96 x 0.30 = 0.588`. Gym Hero wins by 0.073 because a genre match (0.40) is worth more than a mood match (0.30), and the energy part cannot close a gap that large.

### How genre, mood, energy, and the small catalog shape the rankings

- **Genre (0.40)** is the biggest single factor. Any song that matches both genre and mood scores at least 0.70, and a song that matches neither can never score above 0.30.
- **Mood (0.30)** separates songs within the same genre (Midnight Coding vs. Focus Flow) and lifts songs from other genres when the genre is rare (Gym Hero for the rock listener).
- **Energy (0.30)** gives partial credit, so it acts mainly as a tie-breaker. Below the label-matching songs, the list is ordered by energy alone.
- **The small catalog** decides how many good options exist. Lofi has 3 songs, so the lofi list stays strong for four spots. Rock and folk each have 1 song, so those lists drop below 0.30 right after #1.

### Pairwise comparisons

1. **High-Energy Pop vs. Chill Lofi:** no songs in common. The pop list sits at energy 0.60 to 0.93 and the lofi list at 0.28 to 0.42, so different genre, mood, and energy preferences fully separate the two listeners.
2. **High-Energy Pop vs. Deep Intense Rock:** both lists contain Gym Hero at #2 and Sunrise City. The pop listener gets Gym Hero for its genre, and the rock listener gets it for its mood and energy. Sunrise City is #1 for pop but only #5 filler for rock.
3. **High-Energy Pop vs. Conflicting Preferences:** Gym Hero appears in both (#2 vs. #3). For the folk/sad listener it shows up purely because its energy is 0.93, even though it is neither folk nor sad, which shows how energy drives the list once the labels stop matching.
4. **Chill Lofi vs. Deep Intense Rock:** no songs in common. The two profiles are opposites, and the earlier README check showed each one's top song scores under 0.16 for the other listener.
5. **Chill Lofi vs. Conflicting Preferences:** no songs in common, yet Harbor Lullaby, the conflicting profile's #1, is a calm acoustic song a lofi listener might enjoy. It scores only 0.270 for the lofi listener because it matches neither label. The two lists also behave differently below #1: the lofi list stays calm, while the conflicting list jumps to loud songs.
6. **Deep Intense Rock vs. Conflicting Preferences:** four of five songs are shared (Storm Runner, Gym Hero, Pulse Horizon, Iron Tempest). Asking for energy 0.9 made the folk/sad listener's results almost identical to the rock fan's. After the single folk song, nothing in the catalog matches folk or sad, so energy alone sorts the rest.

### Weight sensitivity experiment

To test how much the ranking depends on genre, I halved the genre weight and doubled the energy weight: genre 0.20, mood 0.30, energy 0.60. These add up to 1.10, so I divided each by 1.10 to keep scores between 0 and 1:

```text
genre  = 0.20 / 1.10 = 0.182
mood   = 0.30 / 1.10 = 0.273
energy = 0.60 / 1.10 = 0.545
```

The experiment ran in a separate temporary script that reused the existing `genre_match`, `mood_match`, and `energy_similarity` functions. `src/recommender.py` was not changed and still uses 0.40 / 0.30 / 0.30.

```text
High-Energy Pop             40/30/30                      Normalized 20/30/60
  1  Sunrise City          0.994              Sunrise City          0.989
  2  Gym Hero              0.661              Rooftop Lights        0.796
  3  Rooftop Lights        0.588              Island Time Radio     0.709
  4  Island Time Radio     0.540              Gym Hero              0.656
  5  Concrete Crown        0.294              Concrete Crown        0.535

Chill Lofi
  1  Midnight Coding       0.994              Midnight Coding       0.989
  2  Library Rain          0.985              Library Rain          0.973
  3  Focus Flow            0.700              Spacewalk Thoughts    0.753
  4  Spacewalk Thoughts    0.564              Focus Flow            0.727
  5  Coffee Shop Stories   0.291              Coffee Shop Stories   0.529

Deep Intense Rock
  1  Storm Runner          0.997              Storm Runner          0.995
  2  Gym Hero              0.591              Gym Hero              0.802
  3  Pulse Horizon         0.285              Pulse Horizon         0.518
  4  Iron Tempest          0.279              Iron Tempest          0.507
  5  Sunrise City          0.276              Sunrise City          0.502

Conflicting Preferences
  1  Harbor Lullaby        0.820              Harbor Lullaby        0.673
  2  Storm Runner          0.297              Storm Runner          0.540
  3  Gym Hero              0.291              Gym Hero              0.529
  4  Pulse Horizon         0.285              Pulse Horizon         0.518
  5  Iron Tempest          0.279              Iron Tempest          0.507
```

**Impact:**

- **The same five songs appeared for every profile; only the order changed.** No #1 song changed.
- **High-Energy Pop:** Gym Hero dropped from #2 to #4. Rooftop Lights and Island Time Radio, the two other-genre songs with the happy mood, moved up to #2 and #3. Gym Hero's score is now `0.182 + 0.545 x 0.87 = 0.656`, while Rooftop Lights gets `0.273 + 0.545 x 0.96 = 0.796`.
- **Chill Lofi:** Spacewalk Thoughts (ambient, chill) passed Focus Flow (lofi, focused), so a mood match now beats a genre match.
- **Deep Intense Rock:** the order did not change, but Gym Hero rose from 0.591 to 0.802 and the filler songs rose from about 0.28 to about 0.51, so the gap between "good match" and "filler" became much smaller.
- **Conflicting Preferences:** Harbor Lullaby stayed #1, but its lead shrank from 0.523 to 0.133. More energy weight pushes the system toward the loud songs the user's energy setting asked for, but the folk + sad labels (together still worth 0.455) are enough to keep the quiet song on top.

The new weights made the results more accurate for the pop listener because happy songs now outrank an intense one. They made the results less genre-focused for the lofi listener, which is better or worse depending on whether that listener cares more about "lofi" or about "chill". They also raised the scores of weak filler songs, which makes poor matches look better than they are.

### Why the top recommendations changed, in plain language

With the original weights, matching the user's genre is the most valuable thing a song can do, so a same-genre song with the wrong feel (Gym Hero) beats a different-genre song with the right feel (Rooftop Lights). After genre was cut in half and energy doubled, matching the mood (0.273) became worth more than matching the genre (0.182), and having the right energy became worth more than both labels combined. Songs that *sound* like what the user asked for moved up, and songs that only share a genre name moved down. The #1 songs did not move because they already matched everything. Only the songs in the middle of each list, where the features disagree, switched places.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
