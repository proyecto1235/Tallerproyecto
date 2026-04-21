// MongoDB Initialization Script for CodeKids Metrics
// Run with: mongosh codekids_metrics scripts/003-mongodb-init.js

// Create collections with validation schemas
db.createCollection("user_sessions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "timestamp"],
      properties: {
        user_id: { bsonType: "int", description: "User ID from PostgreSQL" },
        session_start: { bsonType: "date" },
        session_end: { bsonType: "date" },
        duration_seconds: { bsonType: "int" },
        pages_visited: { bsonType: "array" },
        device_info: { bsonType: "object" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("exercise_metrics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "exercise_id", "timestamp"],
      properties: {
        user_id: { bsonType: "int" },
        exercise_id: { bsonType: "int" },
        attempts: { bsonType: "int" },
        time_to_solve_seconds: { bsonType: "int" },
        hints_used: { bsonType: "int" },
        errors_encountered: { bsonType: "array" },
        code_snapshots: { bsonType: "array" },
        final_score: { bsonType: "int" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("learning_analytics", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "timestamp"],
      properties: {
        user_id: { bsonType: "int" },
        module_id: { bsonType: "int" },
        lesson_id: { bsonType: "int" },
        time_spent_seconds: { bsonType: "int" },
        interaction_events: { bsonType: "array" },
        comprehension_score: { bsonType: "double" },
        difficulty_rating: { bsonType: "int" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("platform_events", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["event_type", "timestamp"],
      properties: {
        event_type: { bsonType: "string" },
        user_id: { bsonType: "int" },
        event_data: { bsonType: "object" },
        ip_address: { bsonType: "string" },
        user_agent: { bsonType: "string" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});

db.createCollection("ai_interactions", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["user_id", "interaction_type", "timestamp"],
      properties: {
        user_id: { bsonType: "int" },
        interaction_type: { bsonType: "string" },
        prompt: { bsonType: "string" },
        response: { bsonType: "string" },
        tokens_used: { bsonType: "int" },
        response_time_ms: { bsonType: "int" },
        feedback_rating: { bsonType: "int" },
        timestamp: { bsonType: "date" }
      }
    }
  }
});

// Create indexes for better query performance
db.user_sessions.createIndex({ user_id: 1 });
db.user_sessions.createIndex({ timestamp: -1 });
db.user_sessions.createIndex({ session_start: -1 });

db.exercise_metrics.createIndex({ user_id: 1 });
db.exercise_metrics.createIndex({ exercise_id: 1 });
db.exercise_metrics.createIndex({ timestamp: -1 });
db.exercise_metrics.createIndex({ user_id: 1, exercise_id: 1 });

db.learning_analytics.createIndex({ user_id: 1 });
db.learning_analytics.createIndex({ module_id: 1 });
db.learning_analytics.createIndex({ timestamp: -1 });

db.platform_events.createIndex({ event_type: 1 });
db.platform_events.createIndex({ user_id: 1 });
db.platform_events.createIndex({ timestamp: -1 });

db.ai_interactions.createIndex({ user_id: 1 });
db.ai_interactions.createIndex({ interaction_type: 1 });
db.ai_interactions.createIndex({ timestamp: -1 });

print("✅ MongoDB collections and indexes created successfully!");
print("Collections created:");
print("  - user_sessions");
print("  - exercise_metrics");
print("  - learning_analytics");
print("  - platform_events");
print("  - ai_interactions");
