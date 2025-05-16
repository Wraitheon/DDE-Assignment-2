// main.go
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"time"

	"go-app/db" // replace with your actual module path
	"go-app/queries"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

func main() {
	var action string
	var userIdStr string
	var topicIdStr string
	var k int

	flag.StringVar(&action, "action", "", "Action to perform: posts-by-user, top-likes, top-comments, comments-by-user, posts-by-topic, top-topics, friends-posts-recent")
	flag.StringVar(&userIdStr, "userId", "", "User ID in hex format (required for relevant actions)")
	flag.StringVar(&topicIdStr, "topicId", "", "Topic ID in hex format (required for posts-by-topic)")
	flag.IntVar(&k, "k", 0, "Parameter k for top-k queries")
	flag.Parse()

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, dbConn, err := db.Connect(ctx)
	if err != nil {
		log.Fatalf("Failed to connect to DB: %v", err)
	}
	defer func() {
		if err := client.Disconnect(ctx); err != nil {
			log.Printf("Error disconnecting from DB: %v", err)
		}
	}()

	var result interface{}

	switch action {
	case "posts-by-user":
		if userIdStr == "" {
			log.Fatal("--userId is required for posts-by-user")
		}
		userID, err := primitive.ObjectIDFromHex(userIdStr)
		if err != nil {
			log.Fatalf("Invalid userId: %v", err)
		}
		result, err = queries.GetPostsByUser(ctx, dbConn, userID)

	case "top-likes":
		if userIdStr == "" || k <= 0 {
			log.Fatal("--userId and --k (>0) are required for top-likes")
		}
		userID, err := primitive.ObjectIDFromHex(userIdStr)
		if err != nil {
			log.Fatalf("Invalid userId: %v", err)
		}
		result, err = queries.GetTopKPostsByLikes(ctx, dbConn, userID, k)

	case "top-comments":
		if userIdStr == "" || k <= 0 {
			log.Fatal("--userId and --k (>0) are required for top-comments")
		}
		userID, err := primitive.ObjectIDFromHex(userIdStr)
		if err != nil {
			log.Fatalf("Invalid userId: %v", err)
		}
		result, err = queries.GetTopKPostsByComments(ctx, dbConn, userID, k)

	case "comments-by-user":
		if userIdStr == "" {
			log.Fatal("--userId is required for comments-by-user")
		}
		userID, err := primitive.ObjectIDFromHex(userIdStr)
		if err != nil {
			log.Fatalf("Invalid userId: %v", err)
		}
		result, err = queries.GetCommentsByUser(ctx, dbConn, userID)

	case "posts-by-topic":
		if topicIdStr == "" {
			log.Fatal("--topicId is required for posts-by-topic")
		}
		topicID, err := primitive.ObjectIDFromHex(topicIdStr)
		if err != nil {
			log.Fatalf("Invalid topicId: %v", err)
		}
		result, err = queries.GetPostsByTopic(ctx, dbConn, topicID)

	case "top-topics":
		if k <= 0 {
			log.Fatal("--k (>0) is required for top-topics")
		}
		result, err = queries.GetTopKTopicsByPostCount(ctx, dbConn, k)

	case "friends-posts-recent":
		if userIdStr == "" {
			log.Fatal("--userId is required for friends-posts-recent")
		}
		userID, err := primitive.ObjectIDFromHex(userIdStr)
		if err != nil {
			log.Fatalf("Invalid userId: %v", err)
		}
		result, err = queries.GetFriendsPostsLast24h(ctx, dbConn, userID)

	default:
		log.Fatalf("Unknown action: %s", action)
	}

	if err != nil {
		log.Fatalf("Query error: %v", err)
	}

	out, err := json.MarshalIndent(result, "", "  ")
	if err != nil {
		log.Fatalf("Failed to marshal result: %v", err)
	}
	fmt.Println(string(out))
}
