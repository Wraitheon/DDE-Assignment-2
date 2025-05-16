#!/usr/bin/env bash
echo "Waiting for shard1 members to come up…"
sleep 10

echo "Initiating rs-shard01…"
docker exec shard01-a \
  mongosh --quiet --host shard01-a:27017 --eval '
    rs.initiate({
      _id: "rs-shard01",
      members: [
        { _id: 0, host: "shard01-a:27017" },
        { _id: 1, host: "shard01-b:27017" },
        { _id: 2, host: "shard01-c:27017" }
      ]
    });
  '

echo "rs-shard01 initiated."
