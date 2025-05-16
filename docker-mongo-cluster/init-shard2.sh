#!/usr/bin/env bash
echo "Waiting for shard2 members to come up…"
sleep 10

echo "Initiating rs-shard02…"
docker exec shard02-a \
  mongosh --quiet --host shard02-a:27017 --eval '
    rs.initiate({
      _id: "rs-shard02",
      members: [
        { _id: 0, host: "shard02-a:27017" },
        { _id: 1, host: "shard02-b:27017" },
        { _id: 2, host: "shard02-c:27017" }
      ]
    });
  '

echo "rs-shard02 initiated."
