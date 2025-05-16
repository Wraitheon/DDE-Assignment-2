#!/usr/bin/env bash
echo "Waiting for mongos to be ready…"
sleep 20

echo "Adding shards and enabling sharding…"
docker exec mongos01 \
  mongosh --quiet --host localhost:27017 --eval '
    sh.addShard("rs-shard01/shard01-a:27017,shard01-b:27017,shard01-c:27017");
    sh.addShard("rs-shard02/shard02-a:27017,shard02-b:27017,shard02-c:27017");
    sh.enableSharding("socialfeed");
    // pick your shard keys here:
    sh.shardCollection("socialfeed.posts",    { authorId: 1 });
    sh.shardCollection("socialfeed.users",    { _id: 1 });
    sh.shardCollection("socialfeed.comments", { postId: 1 });
    sh.shardCollection("socialfeed.likes",    { postId: 1 });
    sh.shardCollection("socialfeed.friendships",  { followerId: 1});
    sh.shardCollection("socialfeed.topics", { name: 1 });
    // …etc for any other collections
  '

echo "Router configuration complete."
