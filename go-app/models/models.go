package models

import (
	"time"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

// User represents a user document in the users collection.
type User struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	UserIDStr string             `bson:"user_id_str"`
	Name      string             `bson:"name"`
	Email     string             `bson:"email"`
	CreatedAt time.Time          `bson:"created_at"`
}

// Topic represents a topic document in the topics collection.
type Topic struct {
	ID   primitive.ObjectID `bson:"_id,omitempty"`
	Name string             `bson:"name"`
}

// Post represents a post document in the posts collection.
type Post struct {
	ID            primitive.ObjectID `bson:"_id,omitempty"`
	UserID        primitive.ObjectID `bson:"user_id"`
	TopicID       primitive.ObjectID `bson:"topic_id"`
	Content       string             `bson:"content"`
	CreatedAt     time.Time          `bson:"created_at"`
	LikesCount    int                `bson:"likes_count"`
	CommentsCount int                `bson:"comments_count"`
}

// Comment represents a comment document in the comments collection.
type Comment struct {
	ID        primitive.ObjectID `bson:"_id,omitempty"`
	PostID    primitive.ObjectID `bson:"post_id"`
	UserID    primitive.ObjectID `bson:"user_id"`
	Text      string             `bson:"text"`
	CreatedAt time.Time          `bson:"created_at"`
}

// Like represents a like document in the likes collection.
type Like struct {
	ID      primitive.ObjectID `bson:"_id,omitempty"`
	PostID  primitive.ObjectID `bson:"post_id"`
	UserID  primitive.ObjectID `bson:"user_id"`
	LikedAt time.Time          `bson:"liked_at"`
}

// Friendship represents a uni-directional friendship (follower -> followed) in the friendships collection.
type Friendship struct {
	ID         primitive.ObjectID `bson:"_id,omitempty"`
	FollowerID primitive.ObjectID `bson:"follower_id"`
	FollowedID primitive.ObjectID `bson:"followed_id"`
	CreatedAt  time.Time          `bson:"created_at"`
}
