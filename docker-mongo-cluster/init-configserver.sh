#!/bin/bash
echo "Waiting for config servers to start..."
sleep 10 # Adjust as needed

echo "Initiating config server replica set..."
mongosh --host configsvr01:27017 <<EOF
rs.initiate(
  {
    _id: "rs-config",
    configsvr: true,
    members: [
      { _id: 0, host: "configsvr01:27017" },
      { _id: 1, host: "configsvr02:27017" },
      { _id: 2, host: "configsvr03:27017" }
    ]
  }
)
EOF
echo "Config server replica set initiated."