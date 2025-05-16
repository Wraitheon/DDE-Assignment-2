#!/bin/bash
echo "Waiting for shard1 servers to start..."
sleep 10 # Adjust as needed

echo "Initiating shard1 replica set..."
mongosh --host shard01-a:27017 <<EOF
rs.initiate(
  {
    _id: "rs-shard01",
    members: [
      { _id: 0, host: "shard01-a:27017" },
      { _id: 1, host: "shard01-b:27017" },
      { _id: 2, host: "shard01-c:27017" }
    ]
  }
)
EOF
echo "Shard1 replica set initiated."