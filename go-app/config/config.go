// config/config.go
package config

// MongoURI is the connection string for MongoDB (mongos router)
const MongoURI = "mongodb://localhost:27017"

// DatabaseName is the name of the primary database
const DatabaseName = "socialfeed"

// Collection names
const (
	UsersCollection       = "users"
	PostsCollection       = "posts"
	CommentsCollection    = "comments"
	LikesCollection       = "likes"
	FriendshipsCollection = "friendships"
	TopicsCollection      = "topics"
)
