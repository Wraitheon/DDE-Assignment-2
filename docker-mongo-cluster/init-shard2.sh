#!/bin/bash
echo "Waiting for shard2 servers to start..."
sleep 10 # Adjust as needed

echo "Initiating shard2 replica set..."
mongosh --host shard02-a:27017 <<EOF
rs.initiate(
  {
    _id: "rs-shard02",
    members: [
      { _id: 0, host: "shard02-a:27017" },
      { _id: 1, host: "shard02-b:27017" },
      { _id: 2, host: "shard02-c:27017" }
    ]
  }
)
EOF
echo "Shard2 replica set initiated."