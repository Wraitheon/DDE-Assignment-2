#!/usr/bin/env bash
echo "Waiting for config servers to start…"
sleep 10

echo "Initiating config server replica set…"
docker exec configsvr01 \
  mongosh --quiet --host configsvr01:27017 --eval '
    rs.initiate({
      _id: "rs-config",
      configsvr: true,
      members: [
        { _id: 0, host: "configsvr01:27017" },
        { _id: 1, host: "configsvr02:27017" },
        { _id: 2, host: "configsvr03:27017" }
      ]
    });
  '

echo "Config server replica set initiated."
