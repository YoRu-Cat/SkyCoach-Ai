# Activity Corpus Dataset

**Location:** `services/auto_judge.py` / `ACTIVITY_CORPUS` dictionary

## Dataset Size
- **Total Activities:** 100+ distinct activities
- **Outdoor:** 50+ activities
- **Indoor:** 50+ activities

## Activity Categories

### Outdoor Activities (50+)
**Sports:**
- Soccer, Football, Baseball, Basketball, Volleyball, Tennis
- Cricket, Golf, Skateboarding, Skiing, Snowboarding
- Rock climbing, Surfing, Windsurfing, Kayaking, Canoeing

**Physical Activities:**
- Running, Jogging, Cycling, Biking, Hiking, Trekking, Walking
- Swimming, Dog walking, Pet walking, Sports

**Yard & Garden Work:**
- Gardening, Mowing lawn, Raking leaves, Hedge trimming
- Car washing, Outdoor cooking, BBQ

**Leisure:**
- Picnic, Camping, Fishing, Photography, Bird watching
- Nature walk, Outdoor games

### Indoor Activities (50+)
**Work & Study:**
- Homework, Studying, Working, Office work, Coding, Programming

**Entertainment:**
- Gaming, Video games, Watching movies, Streaming
- Watching streams, Listening to music, Podcasts, Audiobooks
- Board games, Puzzles

**Creative & Hobby:**
- Reading, Writing, Drawing, Sketching, Painting, Art
- Crafting, Knitting, Sewing, Quilting, Building (Lego)
- Photo editing, Video editing, Blogging

**Physical & Wellness:**
- Yoga, Exercise, Workout, Meditation, Stretching, Dancing

**Household:**
- Cooking, Baking, Cleaning, Laundry, Ironing, Organizing
- Shopping, Grocery shopping

**Music & Learning:**
- Playing music, Playing instruments, Music lessons
- Online courses

### Dataset Features
- **Fuzzy Matching:** Activities stored as base forms and variants
- **Phrase Support:** Multi-word activities (e.g., "playing soccer")
- **Common Variants:** Abbreviations and misspellings handled by algorithm
- **Classification Labels:** Each activity tagged as Outdoor or Indoor

### Usage Example
```python
from services.auto_judge import ACTIVITY_CORPUS, ALL_ACTIVITIES

# All activities as flat list
all_acts = ALL_ACTIVITIES  # 100+ items

# Organized by category
outdoor = ACTIVITY_CORPUS["Outdoor"]
indoor = ACTIVITY_CORPUS["Indoor"]

# Suggestions based on partial input
suggest_activity("play socc")  # → ("playing soccer", 0.92, "Outdoor")
suggest_activity("doing homewo")  # → ("doing homework", 0.88, "Indoor")
```

### Matching Algorithm
1. **Exact phrase match** - If input closely matches activity phrase
2. **Close matches** - Using difflib with 0.4 cutoff threshold
3. **Word overlap** - Count shared words between input and activities
4. **Character similarity** - 65% word overlap + 35% string similarity
5. **Confidence threshold** - Return only if score > 0.4

### Extension Points
To add new activities, append to `ACTIVITY_CORPUS` dictionary:
```python
ACTIVITY_CORPUS["Outdoor"].append("new activity")
ACTIVITY_CORPUS["Indoor"].append("new activity")
```
