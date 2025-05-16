# SocialFeed Sharded MongoDB Cluster Setup

This document summarizes the steps we’ve completed so far to satisfy the assignment requirements:

1. Stand up a sharded MongoDB cluster via Docker
2. Initialize each component (config servers, shards, router)
3. Import JSON data into the sharded cluster
4. Verify the sharding configuration

---

## Prerequisites

- **Docker & Docker Compose** installed and running
- **MongoDB Shell (`mongosh`)** installed on your host and available in Git Bash’s `$PATH`
- **MongoDB Compass** (optional, for GUI-based import and inspection)
- **JSON data files** for collections: `users.json`, `posts.json`, `comments.json`, `likes.json`, `friendships.json`, `topics.json`
- (Optional) **Go** toolchain if you plan to run the Go-based query CLI

---

## 1. Start the Dockerized Cluster

1. In your project directory (where `docker-compose.yml` lives):

   ```bash
   docker-compose up -d
   ```

2. Wait \~30 seconds for all containers (`configsvr01/02/03`, `shard01-a/b/c`, `shard02-a/b/c`, `mongos01`) to start.

---

## 2. Initialize Replica Sets & Sharding

We use our `init-*.sh` scripts, which under the hood run `mongosh` via `docker exec`:

```bash
# 1. Config server
bash init-configserver.sh

# 2. Shard 1
bash init-shard1.sh

# 3. Shard 2
bash init-shard2.sh

# 4. Mongos router
bash init-router.sh
```

Each script will:

- Wait for its target containers to be ready
- Run `rs.initiate(...)` inside the appropriate container (for config or shard RS)
- Register shards and apply `sh.shardCollection(...)` for each collection in the router script

---

## 3. Import JSON Data into the Sharded Cluster

Your data must live inside the Docker cluster’s `mongos` process (port 27017 by default):

### Option A: Use MongoDB Compass

1. In Compass, connect to **mongodb://localhost:27017** (the `mongos` router).
2. For each JSON file:

   - Select (or create) database `socialfeed` and the matching collection name.
   - Click **Add Data → Import File**.
   - Choose **JSON**, point at `*.json`, check **"File contains a JSON array"** if applicable, then **Import**.

### Option B: Use `mongoimport` on the Host

```bash
mongoimport --host localhost:27017 --db socialfeed --collection users      --file /path/to/users.json      --jsonArray
mongoimport --host localhost:27017 --db socialfeed --collection posts      --file /path/to/posts.json      --jsonArray
mongoimport --host localhost:27017 --db socialfeed --collection comments   --file /path/to/comments.json   --jsonArray
mongoimport --host localhost:27017 --db socialfeed --collection likes      --file /path/to/likes.json      --jsonArray
mongoimport --host localhost:27017 --db socialfeed --collection friendships--file /path/to/friendships.json--jsonArray
mongoimport --host localhost:27017 --db socialfeed --collection topics     --file /path/to/topics.json     --jsonArray
```

---

## 4. Verify Sharding Configuration

1. **Connect** to the router:

   ```bash
   mongosh --host localhost:27017
   ```

2. **Check status:**

   ```js
   sh.status(true); // verbose—lists shards, databases, collections, and chunk ranges
   ```

3. **Inspect chunk distribution** (example for `posts`):

   ```js
   use config
   db.chunks.aggregate([
     { $match: { ns: "socialfeed.posts" } },
     { $group: { _id: "$shard", count: { $sum: 1 } } }
   ]).pretty()
   ```

4. **Confirm** that every collection (`users`, `posts`, `comments`, `likes`, `friendships`, `topics`) appears under `socialfeed` as `sharded: true` with a correct shard key and at least one chunk.

---

## 5. Running Queries (Next Steps)

With your sharded cluster live and data loaded, you can:

- Use **Compass**’s Aggregation Pipeline Builder or **mongosh** queries to retrieve data.
- (If implemented) run your Go-based CLI:

  ```bash
  go run cmd/query.go --action <query-name> --userId <id> [--k <n>]
  ```

  Supported actions: `posts-by-user`, `top-likes`, `top-comments`, `comments-by-user`, `posts-by-topic`, `top-topics`, `friends-posts-recent`

---

**Cluster is now fully set up.** You can proceed to implement and test the seven assignment queries against this production-like, sharded MongoDB environment.

**Commands to test queries coded**

# 1) All posts by a user

go run main.go --action posts-by-user \
 --userId 681e6248c41e3572a61be056

# 2) Top-5 most liked posts for a user

go run main.go --action top-likes \
 --userId 681e6248c41e3572a61be056 --k 5

# 3) Top-5 most commented posts for a user

go run main.go --action top-comments \
 --userId 681e6248c41e3572a61be056 --k 5

# 4) All comments by a user

go run main.go --action comments-by-user \
 --userId 681e6248c41e3572a61be056

# 5) All posts in a topic

go run main.go --action posts-by-topic \
 --topicId 6821abcd1234ef567890ghij

# 6) Top-3 topics by number of posts

go run main.go --action top-topics --k 3

# 7) Posts by friends in the last 24 hours

go run main.go --action friends-posts-recent \
 --userId 681e6248c41e3572a61be056
