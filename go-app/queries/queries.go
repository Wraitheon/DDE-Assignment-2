// queries/queries.go
package queries

import (
	"context"
	"time"

	"go-app/config" // replace with your module path
	"go-app/models"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/bson/primitive"
	"go.mongodb.org/mongo-driver/mongo"
)

// GetPostsByUser returns all posts authored by the given user.
func GetPostsByUser(ctx context.Context, db *mongo.Database, userID primitive.ObjectID) ([]models.Post, error) {
	coll := db.Collection(config.PostsCollection)
	cursor, err := coll.Find(ctx, bson.M{"user_id": userID})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var posts []models.Post
	if err := cursor.All(ctx, &posts); err != nil {
		return nil, err
	}
	return posts, nil
}

// GetTopKPostsByLikes returns the top k posts by the given user, sorted by like count.
func GetTopKPostsByLikes(ctx context.Context, db *mongo.Database, userID primitive.ObjectID, k int) ([]models.Post, error) {
	coll := db.Collection(config.PostsCollection)
	pipeline := mongo.Pipeline{
		{{"$match", bson.D{{"user_id", userID}}}},
		{{"$lookup", bson.D{
			{"from", config.LikesCollection},
			{"localField", "_id"},
			{"foreignField", "post_id"},
			{"as", "likes"},
		}}},
		{{"$addFields", bson.D{{"likes_count", bson.D{{"$size", "$likes"}}}}}},
		{{"$sort", bson.D{{"likes_count", -1}}}},
		{{"$limit", int64(k)}},
	}
	cursor, err := coll.Aggregate(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var posts []models.Post
	if err := cursor.All(ctx, &posts); err != nil {
		return nil, err
	}
	return posts, nil
}

// GetTopKPostsByComments returns the top k posts by the given user, sorted by comment count.
func GetTopKPostsByComments(ctx context.Context, db *mongo.Database, userID primitive.ObjectID, k int) ([]models.Post, error) {
	coll := db.Collection(config.PostsCollection)
	pipeline := mongo.Pipeline{
		{{"$match", bson.D{{"user_id", userID}}}},
		{{"$lookup", bson.D{
			{"from", config.CommentsCollection},
			{"localField", "_id"},
			{"foreignField", "post_id"},
			{"as", "comments"},
		}}},
		{{"$addFields", bson.D{{"comments_count", bson.D{{"$size", "$comments"}}}}}},
		{{"$sort", bson.D{{"comments_count", -1}}}},
		{{"$limit", int64(k)}},
	}
	cursor, err := coll.Aggregate(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var posts []models.Post
	if err := cursor.All(ctx, &posts); err != nil {
		return nil, err
	}
	return posts, nil
}

// GetCommentsByUser returns all comments made by the given user.
func GetCommentsByUser(ctx context.Context, db *mongo.Database, userID primitive.ObjectID) ([]models.Comment, error) {
	coll := db.Collection(config.CommentsCollection)
	cursor, err := coll.Find(ctx, bson.M{"user_id": userID})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var comments []models.Comment
	if err := cursor.All(ctx, &comments); err != nil {
		return nil, err
	}
	return comments, nil
}

// GetPostsByTopic returns all posts under the given topic.
func GetPostsByTopic(ctx context.Context, db *mongo.Database, topicID primitive.ObjectID) ([]models.Post, error) {
	coll := db.Collection(config.PostsCollection)
	cursor, err := coll.Find(ctx, bson.M{"topic_id": topicID})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var posts []models.Post
	if err := cursor.All(ctx, &posts); err != nil {
		return nil, err
	}
	return posts, nil
}

// TopicStat holds the result for the top-k topics query.
type TopicStat struct {
	TopicID primitive.ObjectID `bson:"topic_id"`
	Name    string             `bson:"name"`
	Count   int                `bson:"count"`
}

// GetTopKTopicsByPostCount returns the top k topics by number of posts.
func GetTopKTopicsByPostCount(ctx context.Context, db *mongo.Database, k int) ([]TopicStat, error) {
	coll := db.Collection(config.PostsCollection)
	pipeline := mongo.Pipeline{
		{{"$group", bson.D{{"_id", "$topic_id"}, {"count", bson.D{{"$sum", 1}}}}}},
		{{"$sort", bson.D{{"count", -1}}}},
		{{"$limit", int64(k)}},
		{{"$lookup", bson.D{{"from", config.TopicsCollection}, {"localField", "_id"}, {"foreignField", "_id"}, {"as", "topic"}}}},
		{{"$unwind", "$topic"}},
		{{"$project", bson.D{{"topic_id", "$_id"}, {"count", 1}, {"name", "$topic.name"}}}},
	}
	cursor, err := coll.Aggregate(ctx, pipeline)
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var stats []TopicStat
	if err := cursor.All(ctx, &stats); err != nil {
		return nil, err
	}
	return stats, nil
}

// GetFriendsPostsLast24h returns posts from all users that the given user follows in the last 24 hours.
func GetFriendsPostsLast24h(ctx context.Context, db *mongo.Database, userID primitive.ObjectID) ([]models.Post, error) {
	// 1. Find followed user IDs
	fsColl := db.Collection(config.FriendshipsCollection)
	cursor, err := fsColl.Find(ctx, bson.M{"follower_id": userID})
	if err != nil {
		return nil, err
	}
	defer cursor.Close(ctx)

	var friends []models.Friendship
	if err := cursor.All(ctx, &friends); err != nil {
		return nil, err
	}
	var friendIDs []primitive.ObjectID
	for _, f := range friends {
		friendIDs = append(friendIDs, f.FollowedID)
	}

	// 2. Query posts by those friends in last 24h
	postsColl := db.Collection(config.PostsCollection)
	since := time.Now().Add(-24 * time.Hour)
	filter := bson.M{"user_id": bson.M{"$in": friendIDs}, "created_at": bson.M{"$gte": since}}
	postCursor, err := postsColl.Find(ctx, filter)
	if err != nil {
		return nil, err
	}
	defer postCursor.Close(ctx)

	var posts []models.Post
	if err := postCursor.All(ctx, &posts); err != nil {
		return nil, err
	}
	return posts, nil
}
