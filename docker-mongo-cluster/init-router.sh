#!/bin/bash
echo "Waiting for mongos and replica sets to be ready..."
sleep 20 # Adjust as needed, ensure replica sets are primary

echo "Adding shards to the cluster..."
mongosh --host mongos01:27017 <<EOF
sh.addShard("rs-shard01/shard01-a:27017,shard01-b:27017,shard01-c:27017")
sh.addShard("rs-shard02/shard02-a:27017,shard02-b:27017,shard02-c:27017")

printjson(sh.status())

// Enable sharding for the database
sh.enableSharding("social_feed_sharded")
print("Sharding enabled for database 'social_feed_sharded'")

// Shard collections - CHOOSE KEYS WISELY!
// Example shard keys. Re-evaluate based on your queries.
// Hashed shard keys are good for even distribution if queries don't rely on range.
// Ranged shard keys are good if queries often target ranges of that key.

// users: sharding by user_id (assuming _id is user's unique identifier)
db.adminCommand({ shardCollection: "social_feed_sharded.users", key: { _id: "hashed" } })
print("Sharding enabled for 'users' collection on _id (hashed)")

// topics: Small collection, maybe don't shard or shard by name if lookups are common
// For now, let's not shard it as it's small. If needed:
// db.adminCommand({ shardCollection: "social_feed_sharded.topics", key: { name: 1 } })

// friendships: sharding by follower_id (for finding who a user follows)
db.adminCommand({ shardCollection: "social_feed_sharded.friendships", key: { follower_id: 1 } })
print("Sharding enabled for 'friendships' collection on follower_id")

// posts: Shard by user_id (to group user's posts) and created_at (for time-based queries)
// This is a compound shard key. Good for queries like "all posts by user X created recently"
db.adminCommand({ shardCollection: "social_feed_sharded.posts", key: { user_id: 1, created_at: -1 } })
print("Sharding enabled for 'posts' collection on {user_id: 1, created_at: -1}")

// likes: Shard by post_id, as likes are always tied to a post.
db.adminCommand({ shardCollection: "social_feed_sharded.likes", key: { post_id: "hashed" } })
print("Sharding enabled for 'likes' collection on post_id (hashed)")

// comments: Shard by post_id, as comments are always tied to a post.
db.adminCommand({ shardCollection: "social_feed_sharded.comments", key: { post_id: "hashed" } })
print("Sharding enabled for 'comments' collection on post_id (hashed)")

printjson(sh.status())
EOF

echo "Sharding configuration complete."