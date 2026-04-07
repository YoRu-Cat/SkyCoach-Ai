"""
Comprehensive Dataset Generator using English Dictionary
Generates massive, balanced, contextually-rich activity descriptions
for Indoor, Outdoor, Mixed, and Unclear location classifications.
"""

import json
import random
from pathlib import Path
from collections import defaultdict

# Core activity words with inherent location bias
INDOOR_ACTIVITIES = [
    "reading", "cooking", "working", "watching", "studying", "exercising on treadmill",
    "swimming in pool", "playing chess", "painting", "sculpting", "writing", "typing",
    "practicing piano", "practicing guitar", "meditation", "yoga indoors", "stretching",
    "dancing indoors", "singing", "performing concert", "attending lecture", "attending meeting",
    "attending seminar", "attending workshop", "shopping mall", "shopping supermarket",
    "shopping department store", "browsing library", "reading books", "solving puzzles",
    "playing board games", "playing video games", "watching movies", "watching theater",
    "attending movie premiere", "dining restaurant", "dining cafe", "drinking coffee",
    "having breakfast", "having lunch", "having dinner", "eating snacks", "baking",
    "cleaning house", "doing laundry", "vacuuming", "mopping", "ironing", "organizing",
    "repairing furniture", "renovating kitchen", "painting walls", "fixing plumbing",
    "electrical work", "carpentry", "welding", "metalworking", "pottery", "ceramics",
    "jewelry making", "glass blowing", "knitting", "sewing", "embroidery", "quilting",
    "attend art gallery", "attend museum", "attend aquarium", "attend planetarium",
    "attend zoo indoor section", "visit herb garden indoor", "attend convention",
    "attend conference", "attend exhibition", "attend trade show", "attend fair",
    "office work", "clerical work", "administrative work", "reception desk",
    "security guard station", "cashier work", "retail store", "hairdressing salon",
    "spa services", "massage therapy", "physical therapy", "consulting", "training session",
    "corporate presentation", "team meeting", "staff meeting", "annual conference",
]

OUTDOOR_ACTIVITIES = [
    "hiking", "camping", "rock climbing", "mountain biking", "cycling", "running",
    "jogging", "walking", "strolling", "trekking", "exploring trail", "trail running",
    "zip lining", "paragliding", "skydiving", "hot air ballooning", "hang gliding",
    "kayaking", "canoeing", "rafting", "sailing", "windsurfing", "kitesurfing",
    "paddleboarding", "surfing", "swimming ocean", "snorkeling", "scuba diving",
    "fishing", "ice fishing", "fly fishing", "hunting", "wildlife watching",
    "bird watching", "nature photography", "landscape photography", "stargazing",
    "astronomy observing", "picnicking", "beach time", "sunbathing", "beach volleyball",
    "beach soccer", "beach games", "surfing", "boogie boarding", "body surfing",
    "skateboarding", "roller skating", "inline skating", "ice skating rink outdoor",
    "roller hockey", "street hockey", "basketball court", "tennis court", "badminton",
    "soccer field", "american football", "rugby field", "cricket", "baseball",
    "softball", "basketball", "tennis", "badminton outdoor", "racquetball",
    "playing frisbee", "playing cornhole", "horseshoes", "lawn bowling",
    "archery range outdoor", "target shooting outdoor", "axe throwing range",
    "go-kart racing", "drag racing", "off-road racing", "rally racing",
    "attending sports event", "attending concert outdoor", "attending festival",
    "attending fair", "attending carnival", "attending parade", "street fair",
    "farmers market", "street market", "outdoor antique market", "flea market",
    "car show", "motorcycle rally", "bike rally", "truck show",
    "gardening", "landscaping", "yard work", "mowing lawn", "trimming hedges",
    "raking leaves", "planting trees", "planting flowers", "weeding",
    "composting", "greenhouse work", "nursery work", "tree farming",
    "outdoor construction", "building deck", "building fence", "building pergola",
    "laying stone path", "building raised garden", "installing outdoor lighting",
    "picnic table assembly", "tool shed building", "outdoor furniture building",
    "exploring forest", "exploring woods", "exploring mountains", "exploring valleys",
    "exploring canyons", "exploring caves", "cave exploration", "caving",
    "spelunking", "rappelling", "abseiling", "bouldering outdoor",
    "parkour outdoor", "free running outdoor", "trail walking", "nature walk",
    "urban exploration", "sightseeing", "tourist activities", "sightseeing tour",
    "outdoor painting", "outdoor sketching", "outdoor drawing", "landscape painting",
    "wildlife sketching", "plein air painting", "outdoor sculpture",
    "outdoor wedding", "outdoor reception", "outdoor ceremony", "outdoor festival",
    "outdoor party", "outdoor celebration", "backyard barbecue", "patio party",
    "bonfire", "campfire", "fire pit gathering", "outdoor meditation",
    "outdoor exercise class", "outdoor yoga", "outdoor pilates", "outdoor tai chi",
    "park exercise", "park workout", "running track", "outdoor gym",
    "dog walking", "pet exercise", "dog park visit", "equestrian activity",
    "horseback riding", "trail riding", "horse racing", "polo",
    "farming work", "crop harvesting", "hay baling", "operating farm equipment",
    "livestock management", "ranch work", "herding", "cattle drive",
]

MIXED_ACTIVITIES = [
    "going to gym with cafe", "office building with rooftop garden",
    "shopping mall with outdoor plaza", "airport terminal", "train station",
    "bus station", "ferry terminal", "parking garage", "warehouse facility",
    "distribution center", "logistics hub", "shipping facility",
    "hotel lobby", "hotel with outdoor area", "resort with both areas",
    "hospital with outdoor garden", "medical facility with parking",
    "school campus", "university campus", "college grounds",
    "office complex", "business district", "corporate park",
    "industrial park", "tech campus", "startup incubator",
    "market with indoor/outdoor", "bazaar", "shopping complex",
    "entertainment complex", "amusement park", "theme park",
    "sports complex", "recreation center", "community center",
    "cultural center", "performance venue", "concert hall with grounds",
    "theater complex", "cinema multiplex", "entertainment district",
    "restaurant with outdoor seating", "cafe with patio", "bar with rooftop",
    "pub with garden", "brewery with grounds", "winery with tour areas",
    "hotel conference", "retreat center", "retreat with nature",
    "wedding venue indoor/outdoor", "event space mixed", "banquet hall",
    "convention center", "exposition hall", "trade fair venue",
    "visiting layover destination", "layover activities", "transfer time activity",
    "commuting to work", "commuting journey", "travel between locations",
    "transfer activity", "layover work", "airport lounge work",
    "car waiting", "bus stop waiting", "train platform activity",
    "parking lot waiting", "rest stop activity", "truck stop visit",
]

UNCLEAR_ACTIVITIES = [
    "thinking", "contemplating", "planning", "analyzing", "reviewing",
    "processing information", "making decision", "sleeping", "napping",
    "resting", "recovering", "waiting", "standby", "on hold",
    "pending", "postponed activity", "cancelled activity",
    "uncertain activity", "ambiguous task", "vague objective",
    "starting something", "stopping something", "pausing",
    "resuming something", "transitioning", "changing",
    "doing miscellaneous work", "odd jobs", "general maintenance",
    "routine", "daily routine", "habit", "hobby yet to be defined",
    "something productive", "something fun", "something social",
    "activity", "doing things", "staying active", "being active",
    "occupying time", "passing time", "killing time", "wasting time",
    "leisure time", "free time activity", "downtime", "break time",
    "coffee break", "lunch break", "tea time", "meditation time",
    "personal time", "me time", "alone time", "quiet time",
    "family time", "social gathering", "social interaction",
    "event", "meeting", "appointment", "scheduled", "booked",
    "planned", "temporary", "short-term", "long-term",
    "daytime activity", "nighttime activity", "evening activity",
    "morning routine", "afternoon activity", "evening routine",
    "ongoing", "in progress", "work in progress", "project",
    "task", "errand", "chore", "responsibility",
    "obligation", "commitment", "engagement", "involvement",
    "participation", "involvement", "attending", "going",
    "visiting", "exploring", "checking out", "dropping by",
    "passing through", "stopping by", "popping in",
]

# Location-indicating context words
INDOOR_CONTEXT = [
    "inside", "in the building", "indoors", "under roof", "in the house",
    "at home", "in room", "in office", "in workplace", "at work",
    "in store", "in shop", "in mall", "in market", "in arcade",
    "in basement", "in attic", "in garage", "in warehouse",
    "in stadium roof", "in covered area", "under shelter",
]

OUTDOOR_CONTEXT = [
    "outside", "outdoors", "open air", "in nature", "in park",
    "in garden", "in yard", "on mountain", "on beach", "on trail",
    "in forest", "in woods", "on field", "on court", "on road",
    "on highway", "in countryside", "in desert", "in valley",
    "on hilltop", "on slope", "in canyon", "on cliff", "on summit",
    "in wilderness", "in backcountry", "on expedition"
]

MIXED_CONTEXT = [
    "in shopping complex", "in entertainment center", "in hotel",
    "in airport", "in train station", "in bus station",
    "in campus", "in resort", "in park with buildings",
    "in community center", "in sports complex", "in market with both areas",
    "moving between inside and outside", "transitioning areas",
]

def generate_activity_descriptions(count_per_label=2500):
    """Generate contextually rich activity descriptions"""
    descriptions = defaultdict(list)
    
    # Generate Indoor activities
    for _ in range(count_per_label):
        activity = random.choice(INDOOR_ACTIVITIES)
        context = random.choice(INDOOR_CONTEXT + [""])
        
        templates = [
            f"I'm {activity}",
            f"Currently {activity}",
            f"I enjoy {activity}",
            f"Doing some {activity}",
            f"Let's go {activity}",
            f"I decided to go {activity}",
            f"Going to {activity} {context}",
            f"Heading to {activity} {context}",
            f"{activity.capitalize()} is fun",
            f"Planning to {activity}",
            f"I want to {activity}",
            f"Can we {activity}?",
            f"Let's {activity} together",
            f"Just finished {activity}",
            f"Starting to {activity}",
        ]
        
        description = random.choice(templates).strip()
        if context and description.endswith(context):
            description = description
        descriptions["Indoor"].append(description)
    
    # Generate Outdoor activities
    for _ in range(count_per_label):
        activity = random.choice(OUTDOOR_ACTIVITIES)
        context = random.choice(OUTDOOR_CONTEXT + [""])
        
        templates = [
            f"I'm {activity}",
            f"Currently {activity}",
            f"I love {activity}",
            f"Let's go {activity}",
            f"Going to {activity} {context}",
            f"Heading out for {activity}",
            f"Taking a trip for {activity}",
            f"Adventure of {activity}",
            f"{activity.capitalize()} is exciting",
            f"Enjoying {activity}",
            f"Planning an outing for {activity}",
            f"Want to {activity}?",
            f"Let's {activity} outside",
            f"Just got back from {activity}",
            f"Preparing for {activity}",
        ]
        
        description = random.choice(templates).strip()
        descriptions["Outdoor"].append(description)
    
    # Generate Mixed location activities
    for _ in range(count_per_label):
        activity = random.choice(MIXED_ACTIVITIES)
        
        templates = [
            f"I'm {activity}",
            f"Currently at {activity}",
            f"Visiting {activity}",
            f"Going to {activity}",
            f"Time for {activity}",
            f"Let's visit {activity}",
            f"Planning trip to {activity}",
            f"Exploring {activity}",
            f"Day at {activity}",
            f"Spending time at {activity}",
            f"Adventure at {activity}",
            f"Taking family to {activity}",
            f"Heading to {activity}",
            f"Just arrived at {activity}",
            f"Enjoying {activity}",
        ]
        
        description = random.choice(templates).strip()
        descriptions["Mixed"].append(description)
    
    # Generate Unclear/Ambiguous activities
    for _ in range(count_per_label):
        activity = random.choice(UNCLEAR_ACTIVITIES)
        
        templates = [
            f"I'm {activity}",
            f"Currently {activity}",
            f"Just {activity}",
            f"Thinking about {activity}",
            f"Planning to {activity}",
            f"Need to {activity}",
            f"Going to {activity}",
            f"Some {activity}",
            f"Doing {activity}",
            f"That's {activity}",
            f"It's time to {activity}",
            f"Let me {activity}",
            f"Maybe {activity}",
            f"Should I {activity}?",
            f"Want to {activity}?",
        ]
        
        description = random.choice(templates).strip()
        descriptions["Unclear"].append(description)
    
    return descriptions


def create_balanced_splits(all_descriptions, train_ratio=0.7, val_ratio=0.15, test_ratio=0.1, hardset_ratio=0.05):
    """Create balanced train/val/test/hardset splits"""
    splits = {"train": [], "val": [], "test": [], "hardset": []}
    
    for label, descriptions in all_descriptions.items():
        # Shuffle descriptions
        random.shuffle(descriptions)
        
        train_count = int(len(descriptions) * train_ratio)
        val_count = int(len(descriptions) * val_ratio)
        test_count = int(len(descriptions) * test_ratio)
        hardset_count = len(descriptions) - train_count - val_count - test_count
        
        # Distribute
        for i, desc in enumerate(descriptions):
            record = {"phrase": desc, "label": label}
            
            if i < train_count:
                splits["train"].append(record)
            elif i < train_count + val_count:
                splits["val"].append(record)
            elif i < train_count + val_count + test_count:
                splits["test"].append(record)
            else:
                splits["hardset"].append(record)
    
    # Shuffle each split
    for split_name in splits:
        random.shuffle(splits[split_name])
    
    return splits


def save_splits_to_jsonl(splits, output_dir):
    """Save splits to JSONL files"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for split_name, records in splits.items():
        filepath = output_path / f"{split_name}.jsonl"
        with open(filepath, 'w') as f:
            for record in records:
                f.write(json.dumps(record) + '\n')
        print(f"✓ Created {split_name}.jsonl with {len(records)} records")
    
    return output_path


def print_dataset_summary(splits):
    """Print dataset statistics"""
    print("\n" + "="*60)
    print("DATASET GENERATION COMPLETE")
    print("="*60)
    
    total_records = sum(len(records) for records in splits.values())
    print(f"\nTotal records: {total_records:,}")
    
    for split_name, records in splits.items():
        label_counts = defaultdict(int)
        for record in records:
            label_counts[record["label"]] += 1
        
        print(f"\n{split_name.upper()} SPLIT: {len(records):,} records")
        for label, count in sorted(label_counts.items()):
            percentage = (count / len(records)) * 100
            print(f"  {label:12} {count:5,} records ({percentage:5.1f}%)")


if __name__ == "__main__":
    print("Generating comprehensive activity dataset...")
    print("Using English dictionary-based activity descriptions")
    print("Generating 2,500 balanced examples per label...")
    
    # Generate descriptions
    all_descriptions = generate_activity_descriptions(count_per_label=2500)
    
    print(f"\nTotal descriptions generated: {sum(len(v) for v in all_descriptions.values()):,}")
    
    # Create balanced splits
    splits = create_balanced_splits(all_descriptions)
    
    # Save to JSONL
    output_dir = Path(__file__).parent
    save_splits_to_jsonl(splits, output_dir)
    
    # Print summary
    print_dataset_summary(splits)
    
    print(f"\n✓ All files saved to: {output_dir}")
    print("\nDataset is ready for training!")
    write_jsonl(base / "hardset.jsonl", hard_rows)

    print("Generated datasets:")
    print("- train.jsonl:", 6000 * 4)
    print("- val.jsonl:", 1000 * 4)
    print("- test.jsonl:", 1000 * 4)
    print("- hardset.jsonl:", 500 * 4)


if __name__ == "__main__":
    main()
