// ============================================
// RoboLearn Massive Seed — MongoDB (1000+ registros)
// Ejecutar después de 004-mongodb-init.js
// ============================================

db = db.getSiblingDB('robolearn_metrics');

print('Seeding massive behavioral data...');

// ============================================
// 5000 Behavioral Events
// ============================================
const actions = ['exercise_started', 'code_typed', 'exercise_submitted', 'hint_requested', 'exercise_abandoned', 'module_viewed', 'lesson_completed'];
const batchSize = 500;
let totalEvents = 0;

for (let batch = 0; batch < 10; batch++) {
    const docs = [];
    for (let i = 0; i < batchSize; i++) {
        docs.push({
            user_id: Math.floor(Math.random() * 1000) + 101,
            exercise_id: Math.floor(Math.random() * 25) + 1,
            module_id: Math.floor(Math.random() * 10) + 1,
            action: actions[Math.floor(Math.random() * actions.length)],
            metadata: { attempt: Math.floor(Math.random() * 5) + 1 },
            timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
        });
    }
    try {
        db.behavioral_events.insertMany(docs, { ordered: false });
        totalEvents += docs.length;
    } catch(e) {
        // Ignore duplicate errors
    }
}
print(`  [OK] ${totalEvents} behavioral events inserted`);

// ============================================
// 2000 Frustration Signals
// ============================================
const signalTypes = ['rapid_retry', 'long_idle', 'multiple_hints', 'code_deletion', 'tab_switch'];
let totalFrustration = 0;

for (let batch = 0; batch < 4; batch++) {
    const docs = [];
    for (let i = 0; i < 500; i++) {
        docs.push({
            user_id: Math.floor(Math.random() * 1000) + 101,
            exercise_id: Math.floor(Math.random() * 25) + 1,
            signal_type: signalTypes[Math.floor(Math.random() * signalTypes.length)],
            details: 'Frustration signal detected during exercise',
            timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
        });
    }
    try {
        db.frustration_signals.insertMany(docs, { ordered: false });
        totalFrustration += docs.length;
    } catch(e) {}
}
print(`  [OK] ${totalFrustration} frustration signals inserted`);

// ============================================
// 2000 Code Analysis Records
// ============================================
const errorTypes = ['SyntaxError', 'NameError', 'TypeError', 'IndexError', 'ValueError', 'IndentationError'];
let totalCode = 0;

for (let batch = 0; batch < 4; batch++) {
    const docs = [];
    for (let i = 0; i < 500; i++) {
        const hasError = Math.random() < 0.4;
        docs.push({
            user_id: Math.floor(Math.random() * 1000) + 101,
            exercise_id: Math.floor(Math.random() * 25) + 1,
            code_length: Math.floor(Math.random() * 200) + 10,
            has_error: hasError,
            error: hasError ? errorTypes[Math.floor(Math.random() * errorTypes.length)] : null,
            error_type: hasError ? errorTypes[Math.floor(Math.random() * errorTypes.length)] : null,
            timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000)
        });
    }
    try {
        db.code_analysis.insertMany(docs, { ordered: false });
        totalCode += docs.length;
    } catch(e) {}
}
print(`  [OK] ${totalCode} code analysis records inserted`);

// ============================================
// 1000 Engagement Scores
// ============================================
const engagementDocs = [];
for (let i = 0; i < 1000; i++) {
    const userId = Math.floor(Math.random() * 1000) + 101;
    engagementDocs.push({
        user_id: userId,
        module_id: Math.floor(Math.random() * 10) + 1,
        engagement_score: Math.round((0.1 + Math.random() * 0.9) * 100) / 100,
        events_count: Math.floor(Math.random() * 200),
        total_time_minutes: Math.round((Math.random() * 500) * 100) / 100,
        session_days: Math.floor(Math.random() * 30),
        frustration_count: Math.floor(Math.random() * 20),
        calculated_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    });
}
try {
    db.engagement_scores.insertMany(engagementDocs, { ordered: false });
} catch(e) {}
print(`  [OK] ${engagementDocs.length} engagement scores inserted`);

// ============================================
// 1000 Predictions Cache
// ============================================
const predictionDocs = [];
for (let i = 0; i < 1000; i++) {
    predictionDocs.push({
        user_id: Math.floor(Math.random() * 1000) + 101,
        dropout_risk: Math.round((Math.random()) * 100) / 100,
        frustration_level: Math.floor(Math.random() * 3),
        engagement_score: Math.round((0.1 + Math.random() * 0.9) * 100) / 100,
        performance_score: Math.round((0.1 + Math.random() * 0.9) * 100) / 100,
        predicted_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000)
    });
}
try {
    db.predictions.insertMany(predictionDocs, { ordered: false });
} catch(e) {}
print(`  [OK] ${predictionDocs.length} predictions cached`);

print('✅ Massive MongoDB seed complete!');
print('  ~5000 behavioral_events');
print('  ~2000 frustration_signals');
print('  ~2000 code_analysis');
print('  ~1000 engagement_scores');
print('  ~1000 predictions');
