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

// ----- Behavioral Analytics Collections (IA Educativa) -----

// Sessions tracking
db.createCollection('sessions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'session_id', 'started_at', 'last_activity'],
      properties: {
        user_id: { bsonType: 'int' },
        session_id: { bsonType: 'string' },
        started_at: { bsonType: 'date' },
        last_activity: { bsonType: 'date' },
        is_active: { bsonType: 'bool' },
        events_count: { bsonType: 'int' },
        ended_at: { bsonType: 'date' },
      }
    }
  }
});

// Session metrics
db.createCollection('session_metrics', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'session_id', 'duration_seconds'],
      properties: {
        user_id: { bsonType: 'int' },
        session_id: { bsonType: 'string' },
        duration_seconds: { bsonType: 'double' },
        events_count: { bsonType: 'int' },
        date: { bsonType: 'date' },
      }
    }
  }
});

// Behavioral events (exercise started, code typed, help requested, exercise abandoned)
db.createCollection('behavioral_events', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'action', 'timestamp'],
      properties: {
        user_id: { bsonType: 'int' },
        exercise_id: { bsonType: 'int' },
        module_id: { bsonType: 'int' },
        action: { bsonType: 'string' },
        metadata: { bsonType: 'object' },
        timestamp: { bsonType: 'date' },
      }
    }
  }
});

// Frustration signals
db.createCollection('frustration_signals', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'signal_type', 'timestamp'],
      properties: {
        user_id: { bsonType: 'int' },
        exercise_id: { bsonType: 'int' },
        signal_type: { bsonType: 'string' },
        details: { bsonType: 'string' },
        timestamp: { bsonType: 'date' },
      }
    }
  }
});

// Code analysis
db.createCollection('code_analysis', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'exercise_id', 'has_error', 'timestamp'],
      properties: {
        user_id: { bsonType: 'int' },
        exercise_id: { bsonType: 'int' },
        code_length: { bsonType: 'int' },
        has_error: { bsonType: 'bool' },
        error: { bsonType: 'string' },
        error_type: { bsonType: 'string' },
        timestamp: { bsonType: 'date' },
      }
    }
  }
});

// Engagement scores
db.createCollection('engagement_scores', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'engagement_score', 'calculated_at'],
      properties: {
        user_id: { bsonType: 'int' },
        module_id: { bsonType: 'int' },
        engagement_score: { bsonType: 'double' },
        events_count: { bsonType: 'int' },
        total_time_minutes: { bsonType: 'double' },
        session_days: { bsonType: 'int' },
        frustration_count: { bsonType: 'int' },
        calculated_at: { bsonType: 'date' },
      }
    }
  }
});

// Predictions cache
db.createCollection('predictions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'predicted_at'],
      properties: {
        user_id: { bsonType: 'int' },
        dropout_risk: { bsonType: 'double' },
        frustration_level: { bsonType: 'int' },
        engagement_score: { bsonType: 'double' },
        performance_score: { bsonType: 'double' },
        predicted_at: { bsonType: 'date' },
      }
    }
  }
});

// Tutor interactions (intelligent tutor logs)
db.createCollection('tutor_interactions', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['user_id', 'message', 'response', 'intent', 'timestamp'],
      properties: {
        user_id: { bsonType: 'int' },
        session_id: { bsonType: 'string' },
        message: { bsonType: 'string' },
        response: { bsonType: 'string' },
        source: { bsonType: 'string' },
        intent: { bsonType: 'string' },
        student_level: { bsonType: 'string' },
        timestamp: { bsonType: 'date' },
      }
    }
  }
});

// Admin stats collection (for teacher analytics dashboard)
db.createCollection('admin_stats');

// Create indexes
db.sessions.createIndex({ user_id: 1, timestamp: -1 });
db.sessions.createIndex({ session_id: 1 });
db.session_metrics.createIndex({ user_id: 1, date: -1 });
db.behavioral_events.createIndex({ user_id: 1, timestamp: -1 });
db.behavioral_events.createIndex({ user_id: 1, action: 1 });
db.frustration_signals.createIndex({ user_id: 1, timestamp: -1 });
db.code_analysis.createIndex({ user_id: 1, timestamp: -1 });
db.engagement_scores.createIndex({ user_id: 1 });
db.predictions.createIndex({ user_id: 1 });
db.tutor_interactions.createIndex({ user_id: 1, timestamp: -1 });
db.admin_stats.createIndex({ timestamp: -1 });

// TTL indexes for auto-cleanup (90 days)
db.sessions.createIndex({ started_at: 1 }, { expireAfterSeconds: 7776000 });
db.behavioral_events.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 });
db.frustration_signals.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 });
db.code_analysis.createIndex({ timestamp: 1 }, { expireAfterSeconds: 7776000 });

// Create TTL index for chat sessions (auto-delete after 30 days)
db.chat_interactions.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 2592000 }
);

print('✅ Robolearn MongoDB collections initialized successfully!');
print('✅ Collections: events, exercise_attempts, progress_snapshots, chat_interactions,');
print('✅ sessions, session_metrics, behavioral_events, frustration_signals,');
print('✅ code_analysis, engagement_scores, predictions, tutor_interactions, admin_stats');
print('✅ All indexes created for optimal query performance');
