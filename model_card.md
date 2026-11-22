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

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

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
