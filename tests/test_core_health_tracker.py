from src.core.health_tracker import HealthTracker


def test_ping_test_and_check_connectivity(monkeypatch):
    print("TEST: test_ping_test_and_check_connectivity — patch ping_test to return latency and call check_connectivity")
    tracker = HealthTracker()

    # Patch ping_test to return a small latency (ms)
    monkeypatch.setattr(tracker, "ping_test", lambda host=None, count=1, timeout=5: 12.3)

    ok, host = tracker.check_connectivity(hosts=["8.8.8.8"])  # should use our patched ping
    assert isinstance(ok, bool)
    assert ok is True


def test_get_health_score_returns_expected_structure(monkeypatch):
    print("TEST: test_get_health_score_returns_expected_structure — patch ping_test and call get_health_score(detailed=True)")
    tracker = HealthTracker()
    # Ensure ping_test returns a deterministic value
    monkeypatch.setattr(tracker, "ping_test", lambda host=None, count=1, timeout=5: 20.0)

    result = tracker.get_health_score(detailed=True)
    assert isinstance(result, dict)
    assert "score" in result
    assert isinstance(result["score"], int)
