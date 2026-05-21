"""
Test script for the AI Educational System (IA Educativa).
Validates predictive model and intelligent tutor without external dependencies.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_student_predictor():
    from application.services.student_predictor import StudentPredictor

    predictor = StudentPredictor()

    profile = {
        "user_id": 1,
        "session_days_30d": 25,
        "total_sessions_30d": 40,
        "total_time_minutes_30d": 1200,
        "total_events_30d": 300,
        "total_exercise_attempts_30d": 80,
        "passed_exercises_30d": 70,
        "error_rate": 0.15,
        "frustration_signals_30d": 2,
        "engagement_score": 0.85,
        "avg_session_minutes": 30,
    }

    import asyncio
    metrics = asyncio.run(predictor.predict_metrics(profile))

    assert "dropout_risk" in metrics
    assert "frustration_level" in metrics
    assert "engagement_score" in metrics
    assert "performance_score" in metrics
    assert metrics["engagement_score"] > 0.5, f"Expected high engagement, got {metrics['engagement_score']}"
    assert metrics["dropout_risk"] < 0.5, f"Expected low dropout risk, got {metrics['dropout_risk']}"
    assert metrics["performance_score"] > 0.5, f"Expected good performance, got {metrics['performance_score']}"

    print(f"  [+] High-performing student: engagement={metrics['engagement_score']:.3f}, "
          f"dropout_risk={metrics['dropout_risk']:.3f}, "
          f"performance={metrics['performance_score']:.3f}")

    low_profile = {
        "user_id": 2,
        "session_days_30d": 2,
        "total_sessions_30d": 3,
        "total_time_minutes_30d": 30,
        "total_events_30d": 5,
        "total_exercise_attempts_30d": 2,
        "passed_exercises_30d": 0,
        "error_rate": 0.8,
        "frustration_signals_30d": 15,
        "engagement_score": 0.15,
        "avg_session_minutes": 10,
    }

    low_metrics = asyncio.run(predictor.predict_metrics(low_profile))
    assert low_metrics["dropout_risk"] > 0.2, f"Expected higher dropout risk, got {low_metrics['dropout_risk']}"
    assert low_metrics["frustration_level"] >= 1, f"Expected some frustration, got {low_metrics['frustration_level']}"
    assert low_metrics["engagement_score"] < 0.5, f"Expected low engagement, got {low_metrics['engagement_score']}"
    assert low_metrics["performance_score"] < 0.5, f"Expected low performance, got {low_metrics['performance_score']}"

    print(f"  [+] At-risk student: engagement={low_metrics['engagement_score']:.3f}, "
          f"dropout_risk={low_metrics['dropout_risk']:.3f}, "
          f"frustration={low_metrics['frustration_label']}")

    profiles = [profile, low_profile]
    classification = asyncio.run(predictor.classify_students(profiles))
    assert len(classification["at_risk"]) >= 1
    assert len(classification["excellent"]) >= 1

    print(f"  [+] Classification: {len(classification['at_risk'])} at-risk, "
          f"{len(classification['excellent'])} excellent")

    insights = asyncio.run(predictor.get_insights(low_profile))
    assert len(insights) > 0
    print(f"  [+] Insights generated: {len(insights)} insights")

    print("  [+] StudentPredictor: ALL TESTS PASSED")


def test_intelligent_tutor():
    from application.services.intelligent_tutor import IntelligentTutor
    from application.services.student_predictor import StudentPredictor

    predictor = StudentPredictor()
    tutor = IntelligentTutor(predictor=predictor)

    import asyncio

    student_profile = {
        "user_id": 1,
        "session_days_30d": 2,
        "total_sessions_30d": 3,
        "total_time_minutes_30d": 30,
        "total_events_30d": 5,
        "total_exercise_attempts_30d": 2,
        "passed_exercises_30d": 0,
        "error_rate": 0.8,
        "frustration_signals_30d": 15,
        "engagement_score": 0.15,
        "avg_session_minutes": 10,
        "frustration_level": 2,
        "performance_score": 0.2,
    }

    result = asyncio.run(tutor.generate_response(
        "Hola, necesito ayuda",
        student_profile=student_profile,
    ))
    assert result["source"] == "tutor"
    assert result["intent"] == "greeting"
    assert "no preocupes" in result["response"].lower() or "ayudarte" in result["response"].lower()
    print(f"  [+] Greeting response (frustrated student): '{result['response'][:60]}...'")

    result = asyncio.run(tutor.generate_response(
        "Explícame que son las variables",
        student_profile=student_profile,
    ))
    assert result["intent"] == "explain_concept"
    assert result["concept"] == "variable"
    assert "variable" in result["response"].lower()
    print(f"  [+] Concept explanation: intent={result['intent']}, concept={result['concept']}")

    result = asyncio.run(tutor.generate_response(
        "Dame una pista",
        student_profile=student_profile,
    ))
    assert result["intent"] == "request_hint"
    print(f"  [+] Hint request: '{result['response'][:60]}...'")

    result = asyncio.run(tutor.generate_response(
        "Muestrame un ejemplo de funcion",
        student_profile=student_profile,
    ))
    assert result["intent"] == "request_example"
    print(f"  [+] Example request: intent={result['intent']}")

    result = asyncio.run(tutor.generate_response(
        "Me da error NameError",
        student_profile=student_profile,
    ))
    assert result["intent"] == "help_error"
    print(f"  [+] Error help: '{result['response'][:60]}...'")

    result = asyncio.run(tutor.generate_response(
        "Que me recomiendas estudiar",
        student_profile=student_profile,
    ))
    assert result["intent"] == "recommend"
    print(f"  [+] Recommendation: intent={result['intent']}")

    result = asyncio.run(tutor.generate_response(
        "Gracias",
        student_profile=student_profile,
    ))
    assert result["intent"] == "acknowledge"
    print(f"  [+] Acknowledgment: '{result['response'][:40]}...'")

    level = asyncio.run(tutor.get_student_level(student_profile))
    assert level == "beginner"
    print(f"  [+] Student level detection: {level}")

    advanced_profile = dict(student_profile)
    advanced_profile.update({
        "passed_exercises_30d": 30,
        "performance_score": 0.85,
        "frustration_level": 0,
    })
    adv_level = asyncio.run(tutor.get_student_level(advanced_profile))
    assert adv_level == "advanced"
    print(f"  [+] Advanced level detection: {adv_level}")

    hint = asyncio.run(tutor.generate_hint(1, None, advanced_profile))
    assert len(hint) > 0
    print(f"  [+] Hint for advanced: '{hint[:50]}...'")

    print("  [+] IntelligentTutor: ALL TESTS PASSED")


def test_dialogflow_fallback():
    from application.services.intelligent_tutor import IntelligentTutor

    tutor = IntelligentTutor()

    import asyncio

    result = asyncio.run(tutor.generate_response(
        "Cual es el sentido de la vida?",
        student_profile=None,
        dialogflow_result="Eso es una pregunta filosofica interesante.",
    ))
    assert result["source"] == "dialogflow", f"Expected dialogflow, got {result['source']}"
    print(f"  [+] Dialogflow passthrough: source={result['source']}")

    result = asyncio.run(tutor.generate_response(
        "Alebrije cuantico",
        student_profile=None,
        dialogflow_result=None,
    ))
    assert result["source"] == "tutor"
    assert result["intent"] == "fallback" or result["intent"] == "general_chat"
    print(f"  [+] Fallback (no dialogflow): source={result['source']}, intent={result['intent']}")

    print("  [+] DialogflowFallback: ALL TESTS PASSED")


if __name__ == "__main__":
    print("\n*** Testing AI Educational System (IA Educativa) ***\n")
    print("=" * 50)

    tests = [
        ("StudentPredictor (ML Model)", test_student_predictor),
        ("IntelligentTutor (Conversational AI)", test_intelligent_tutor),
        ("DialogflowFallback", test_dialogflow_fallback),
    ]

    all_passed = True
    for name, test_fn in tests:
        print(f"\n[Testing {name}]...")
        try:
            test_fn()
            print(f"  [+] {name}: PASSED")
        except Exception as e:
            print(f"  [X] {name}: FAILED - {e}")
            import traceback
            traceback.print_exc()
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("\n*** ALL TESTS PASSED - AI Educational System is working correctly! ***")
    else:
        print("\n*** SOME TESTS FAILED - Check errors above. ***")
