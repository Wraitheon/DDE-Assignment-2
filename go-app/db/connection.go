package db

import (
	"context"
	"time"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"

	"go-app/config" // replace with your module path if different
)

// Connect establishes a MongoDB connection via the mongos router
// and returns the client and a handle to the configured database.
func Connect(ctx context.Context) (*mongo.Client, *mongo.Database, error) {
	clientOpts := options.Client().ApplyURI(config.MongoURI)
	client, err := mongo.Connect(ctx, clientOpts)
	if err != nil {
		return nil, nil, err
	}

	// Verify connection with a ping
	pingCtx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	if err := client.Ping(pingCtx, nil); err != nil {
		return nil, nil, err
	}

	db := client.Database(config.DatabaseName)
	return client, db, nil
}
