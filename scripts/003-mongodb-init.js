// Robolearn MongoDB Initialization Script
// This script runs when MongoDB container starts

db = db.getSiblingDB('robolearn_metrics');

// Create collections with schema validation

// Events collection
db.createCollection('events', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['event_type', 'user_id', 'timestamp'],
      properties: {
        _id: { bsonType: 'objectId' },
        event_type: {
          enum: ['user_login', 'user_logout', 'exercise_attempt', 'module_enrollment', 'module_completion', 'recommendations_requested'],
          description: 'Type of event'
        },
        user_id: { bsonType: 'int' },
        timestamp: { bsonType: 'date' },
        data: { bsonType: 'object' }
      }
    }
  }
});

// Exercise attempts collection
db.createCollection('exercise_attempts', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['event_type', 'user_id', 'exercise_id', 'timestamp'],
      properties: {
        _id: { bsonType: 'objectId' },
        event_type: { enum: ['exercise_attempt'] },
        user_id: { bsonType: 'int' },
        exercise_id: { bsonType: 'int' },
        module_id: { bsonType: 'int' },
        passed: { bsonType: 'bool' },
        score: { bsonType: 'double' },
        timestamp: { bsonType: 'date' }
      }
    }
  }
});

// Progress snapshots collection
db.createCollection('progress_snapshots', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'timestamp'],
      properties: {
        _id: { bsonType: 'objectId' },
        user_id: { bsonType: 'int' },
        module_id: { bsonType: 'int' },
        percentage: { bsonType: 'double' },
        completed_exercises: { bsonType: 'int' },
        total_exercises: { bsonType: 'int' },
        points_earned: { bsonType: 'int' },
        timestamp: { bsonType: 'date' }
      }
    }
  }
});

// Chat interactions collection
db.createCollection('chat_interactions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'session_id', 'message', 'response', 'timestamp'],
      properties: {
        _id: { bsonType: 'objectId' },
        user_id: { bsonType: 'int' },
        session_id: { bsonType: 'string' },
        message: { bsonType: 'string' },
        response: { bsonType: 'string' },
        intent: { bsonType: 'string' },
        timestamp: { bsonType: 'date' }
      }
    }
  }
});

// Create indexes for better performance
db.events.createIndex({ user_id: 1, timestamp: -1 });
db.events.createIndex({ event_type: 1 });
db.exercise_attempts.createIndex({ user_id: 1, timestamp: -1 });
db.exercise_attempts.createIndex({ exercise_id: 1 });
db.progress_snapshots.createIndex({ user_id: 1, timestamp: -1 });
db.progress_snapshots.createIndex({ module_id: 1 });
db.chat_interactions.createIndex({ user_id: 1, timestamp: -1 });
db.chat_interactions.createIndex({ session_id: 1 });

// Create TTL index for chat sessions (auto-delete after 30 days)
db.chat_interactions.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 2592000 }
);

print('✅ Robolearn MongoDB collections created successfully!');
print('✅ Collections: events, exercise_attempts, progress_snapshots, chat_interactions');
print('✅ Indexes created for optimal query performance');
