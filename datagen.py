# ==============================================
# Data Generation Script for Social Feed (using Google Gemini via google-generativeai)
# ==============================================
import google.generativeai as genai
from google.generativeai import types # For GenerationConfig
import random
import datetime
from pymongo import MongoClient
import time # For rate limiting

# ==============================================
# CONFIGURATION / PLACEHOLDERS
# ==============================================
# Set your Gemini API key.
# IMPORTANT: Replace 'YOUR_ACTUAL_GEMINI_API_KEY' with your actual key.
# It's more secure to set it as an environment variable GOOGLE_API_KEY.
GOOGLE_API_KEY = 'AIzaSyB6-I2T6YP_-peUH7AqxtL3ve2og5fNdbQ' # <-- REPLACE THIS!

# Configure the genai library with your API key
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("Google Gemini API configured successfully.")
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    print("Please ensure GOOGLE_API_KEY is set correctly and is valid.")
    exit()

# Rate limiting configuration
API_CALL_DELAY_SECONDS = 1.1  # Delay between API calls (e.g., 1.1 for ~55 RPM, adjust as needed)
                               # Free tier default is often 60 RPM for gemini-1.5-flash

# MongoDB connection (adjust URI as needed)
client_mongo = MongoClient('mongodb://localhost:27017/')  # or your Mongo URI
db = client_mongo['social_feed'] # Using a new DB name

# Collections
users_col       = db['users']
topics_col      = db['topics']
friends_col     = db['friendships']
posts_col       = db['posts']
likes_col       = db['likes']
comments_col    = db['comments']

# ==============================================
# Helper: Call Gemini to generate text
# ==============================================
def generate_text(prompt: str, model_name: str = "models/gemini-1.5-flash-latest", max_tokens: int = 64) -> str:
    """
    Uses Google Gemini (via google-generativeai) to generate text based on prompt.
    """
    try:
        model = genai.GenerativeModel(model_name)
        generation_config = types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=0.7
        )
        response = model.generate_content(
            contents=prompt,
            generation_config=generation_config
        )

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            text_parts = [part.text for part in response.candidates[0].content.parts if hasattr(part, 'text') and part.text]
            return ''.join(text_parts).strip()
        elif hasattr(response, 'text') and response.text: # Simpler access if response itself is text
             return response.text.strip()
        else:
            # print(f"Warning: Unexpected response structure from Gemini: {response}")
            # Look for error messages if any
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                return f"Content generation blocked: {response.prompt_feedback.block_reason_message or response.prompt_feedback.block_reason}"
            return "Error: Could not parse Gemini response."

    except Exception as e:
        print(f"Error during Gemini API call for prompt '{prompt[:50]}...': {e}")
        if "API key not valid" in str(e):
            print("Critical: API key is not valid. Please check your GOOGLE_API_KEY.")
        elif "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
            print("Quota exhausted. Consider increasing API_CALL_DELAY_SECONDS or checking your quota in Google AI Studio / Cloud Console.")
        return f"Error generating content due to API issue."


# ==============================================
# DATA GENERATION PARAMETERS
# ==============================================
NUM_USERS               = 1000 # Reduced for faster testing, increase as needed
NUM_POSTS               = 2000 # This will result in 2000 API calls for posts
MAX_FRIENDS_PER_USER    = 50
MAX_COMMENTS_PER_POST   = 5  # Max 5 * NUM_POSTS API calls for comments
MAX_LIKES_PER_POST      = 100

# Pre-defined list of ~20 topics
TOPICS = [
    'Machine Learning', 'Web Development', 'Gaming', 'Travel', 'Music',
    'Cooking', 'Health & Wellness', 'Finance', 'Movies', 'Art',
    'Photography', 'Fitness', 'Books', 'Space Exploration', 'DIY',
    'Education', 'Fashion', 'Sports', 'Environment', 'Science'
]
DEFAULT_MODEL_FOR_GENERATION = "models/gemini-1.5-flash-latest" # Use this for consistency

# ==============================================
# 0) Clear existing collections (optional, for a fresh start)
# ==============================================
print("Optional: Clearing existing collections in 'social_feed_v3'...")
# users_col.delete_many({})
# topics_col.delete_many({})
# friends_col.delete_many({})
# posts_col.delete_many({})
# likes_col.delete_many({})
# comments_col.delete_many({})
# print("Collections cleared (if uncommented).")

# ==============================================
# 1) USERS
# ==============================================
print(f"\nGenerating {NUM_USERS} users...")
users = []
for i in range(NUM_USERS):
    users.append({
        'user_id_str': f'user_{i}',
        'name': f'User_{i}',
        'email': f'user_{i}@example.com',
        'created_at': datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=random.randint(0, 365))
    })
if users:
    user_result = users_col.insert_many(users)
    user_ids = user_result.inserted_ids # These are MongoDB ObjectIds
    print(f"{len(user_ids)} users inserted.")
else:
    user_ids = []
    print("No users generated.")

# ==============================================
# 2) TOPICS
# ==============================================
print("\nGenerating topics...")
topic_docs = [{'name': t} for t in TOPICS]
if topic_docs:
    topic_result = topics_col.insert_many(topic_docs)
    topic_ids = topic_result.inserted_ids # These are MongoDB ObjectIds
    print(f"{len(topic_ids)} topics inserted.")
else:
    topic_ids = []
    print("No topics generated.")

# ==============================================
# 3) FRIENDSHIPS (uni-directional)
# ==============================================
if user_ids:
    print(f"\nGenerating friendships for {len(user_ids)} users...")
    friendships = []
    for i, uid in enumerate(user_ids):
        if len(user_ids) > 1:
            num_to_follow = random.randint(0, min(MAX_FRIENDS_PER_USER, len(user_ids) - 1))
            potential_follows = [u_other_id for u_other_id in user_ids if u_other_id != uid]
            if potential_follows and num_to_follow > 0:
                follows = random.sample(potential_follows, num_to_follow)
                for fid in follows:
                    friendships.append({
                        'follower_id': uid,
                        'followed_id': fid,
                        'created_at': datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=random.randint(0, 365))
                    })
        if (i + 1) % 200 == 0: # Print progress less frequently
            print(f"  Processed friendships for {i + 1}/{len(user_ids)} users.")

    if friendships:
        friends_col.insert_many(friendships)
        print(f"{len(friendships)} friendship records inserted.")
    else:
        print("No friendships generated.")
else:
    print("Skipping friendships as no users were generated.")


# ==============================================
# 4) POSTS
# ==============================================
print(f"\nGenerating {NUM_POSTS} posts (with API calls, this will take time)...")
posts_to_insert = []
post_map_for_engagements = []

if user_ids and topic_ids:
    for i in range(NUM_POSTS):
        author_mongo_id = random.choice(user_ids)
        topic_mongo_id = random.choice(topic_ids)

        # Fetch topic name from DB or map from TOPICS list if IDs correspond to indices
        # For simplicity, let's assume topic_ids correspond to indices in TOPICS for now.
        # A more robust way would be to fetch topic by topic_mongo_id from topics_col
        # but that's an extra DB call per post.
        # Let's get the topic name directly from the list using a random index.
        topic_name = random.choice(TOPICS)
        # Find the corresponding topic_id (this is inefficient but simple for now)
        # A better way: create a map of topic_name -> topic_id at the start
        selected_topic_doc = topics_col.find_one({'name': topic_name})
        if selected_topic_doc:
            topic_mongo_id_for_post = selected_topic_doc['_id']
        else: # Fallback if somehow topic isn't found (should not happen with current setup)
            topic_mongo_id_for_post = topic_mongo_id


        prompt = f"Generate a very short, concise social media post (1-2 sentences, less than 200 characters) on the topic '{topic_name}'. Be creative and engaging."
        print(f"({i+1}/{NUM_POSTS}) Generating post content for topic: '{topic_name}'...")

        content = generate_text(prompt, model_name=DEFAULT_MODEL_FOR_GENERATION, max_tokens=70)

        created = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=random.randint(0, 365))

        post_doc = {
            'user_id': author_mongo_id,
            'topic_id': topic_mongo_id_for_post,
            'content': content,
            'created_at': created,
            'likes_count': 0,
            'comments_count': 0
        }
        posts_to_insert.append(post_doc)
        print(f"   Post {i+1} content snippet: {content[:60]}...")

        if (i + 1) % 10 == 0 or (i + 1) == NUM_POSTS:
            print(f"   Prepared {i + 1}/{NUM_POSTS} posts for insertion.")

        print(f"   Waiting for {API_CALL_DELAY_SECONDS}s before next API call...")
        time.sleep(API_CALL_DELAY_SECONDS)

    if posts_to_insert:
        inserted_posts_result = posts_col.insert_many(posts_to_insert)
        inserted_post_ids = inserted_posts_result.inserted_ids
        print(f"\n{len(inserted_post_ids)} posts inserted into MongoDB.")

        # Populate post_map_for_engagements with inserted data
        for idx, post_id in enumerate(inserted_post_ids):
            post_map_for_engagements.append({
                'post_id': post_id, # MongoDB ObjectId
                'user_id': posts_to_insert[idx]['user_id'], # Author's MongoDB ObjectId
                'content': posts_to_insert[idx]['content'],
                'created_at': posts_to_insert[idx]['created_at']
            })
    else:
        print("No posts generated to insert.")
else:
    print("Skipping post generation as no users or topics were found.")


# ==============================================
# 5) COMMENTS
# ==============================================
print(f"\nGenerating comments (with API calls, this will also take time)...")
comments_to_insert = []
total_comments_generated_api = 0

if post_map_for_engagements and user_ids:
    for i, post_entry in enumerate(post_map_for_engagements):
        num_comments_for_this_post = random.randint(0, MAX_COMMENTS_PER_POST)
        original_post_author_id = post_entry['user_id']

        print(f"({i+1}/{len(post_map_for_engagements)}) Attempting to generate {num_comments_for_this_post} comments for post ID {post_entry['post_id']}...")

        potential_commenters = [uid for uid in user_ids if uid != original_post_author_id]
        if not potential_commenters:
            continue

        actual_comments_for_post = 0
        # Ensure we don't try to pick more commenters than available
        commenters_for_this_post = random.sample(potential_commenters, min(num_comments_for_this_post, len(potential_commenters)))

        for j, commenter_id in enumerate(commenters_for_this_post):
            prompt = f"Generate a brief, relevant comment (1-2 sentences, less than 100 characters) responding to this social media post: '{post_entry['content'][:250]}...'"
            print(f"   ({j+1}/{len(commenters_for_this_post)}) Generating comment for post ID {post_entry['post_id']} by user...")

            text = generate_text(prompt, model_name=DEFAULT_MODEL_FOR_GENERATION, max_tokens=50)
            total_comments_generated_api += 1

            ts = post_entry['created_at'] + datetime.timedelta(seconds=random.randint(60, 20 * 24 * 60 * 60)) # Comments within 20 days
            comments_to_insert.append({
                'post_id': post_entry['post_id'],
                'user_id': commenter_id,
                'text': text,
                'created_at': ts
            })
            actual_comments_for_post +=1
            print(f"      Comment {j+1} text snippet: {text[:50]}...")

            print(f"      Waiting for {API_CALL_DELAY_SECONDS}s before next API call...")
            time.sleep(API_CALL_DELAY_SECONDS)

        # Update comments_count in the posts collection for this specific post
        if actual_comments_for_post > 0:
            posts_col.update_one(
                {'_id': post_entry['post_id']},
                {'$set': {'comments_count': actual_comments_for_post}}
            )

    if comments_to_insert:
        comments_col.insert_many(comments_to_insert)
        print(f"\n{len(comments_to_insert)} comments inserted into MongoDB.")
    else:
        print("No comments generated to insert.")
else:
    print("Skipping comment generation as no posts or users were found.")

# ==============================================
# 6) LIKES
# ==============================================
print(f"\nGenerating likes...")
likes_to_insert = []

if post_map_for_engagements and user_ids:
    for i, post_entry in enumerate(post_map_for_engagements):
        original_post_author_id = post_entry['user_id']
        potential_likers = [uid for uid in user_ids if uid != original_post_author_id]

        if not potential_likers:
            continue

        num_likes_for_this_post = random.randint(0, min(MAX_LIKES_PER_POST, len(potential_likers)))

        if num_likes_for_this_post > 0:
            liker_ids = random.sample(potential_likers, num_likes_for_this_post)
            for liker_id in liker_ids:
                ts = post_entry['created_at'] + datetime.timedelta(seconds=random.randint(60, 20 * 24 * 60 * 60)) # Likes within 20 days
                likes_to_insert.append({
                    'post_id': post_entry['post_id'],
                    'user_id': liker_id,
                    'liked_at': ts
                })

        if (i + 1) % 200 == 0 or (i + 1) == len(post_map_for_engagements): # Print progress less frequently
            print(f"   Processed likes for {i + 1}/{len(post_map_for_engagements)} posts. Generated {num_likes_for_this_post} likes for current post.")

        # Update likes_count in the posts collection
        posts_col.update_one(
            {'_id': post_entry['post_id']},
            {'$set': {'likes_count': num_likes_for_this_post}}
        )

    if likes_to_insert:
        likes_col.insert_many(likes_to_insert)
        print(f"\n{len(likes_to_insert)} likes inserted into MongoDB.")
    else:
        print("No likes generated to insert.")
else:
    print("Skipping like generation as no posts or users were found.")


print("\n==============================================")
print("Data generation complete!")
print(f"Total API calls made for content generation: {NUM_POSTS + total_comments_generated_api} (Posts + Comments)")
print(f"Check MongoDB for the '{db.name}' database and its collections.")
print("==============================================")
