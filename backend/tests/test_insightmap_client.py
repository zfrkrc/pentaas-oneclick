import json

import engine


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.hashes = {}

    def get(self, key):
        return self.values.get(key)

    def hgetall(self, key):
        return self.hashes.get(key, {})

    def setex(self, key, ttl, value):
        self.values[key] = value

    def rpush(self, key, value):
        return None

    def expire(self, key, ttl):
        return None


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {"risk_level": "High", "risk_score": 8.2}


def test_collect_service_findings_normalizes_payload(monkeypatch):
    redis = FakeRedis()
    redis.values["scan:scan-1:result:nuclei"] = json.dumps({
        "findings": [{
            "title": "Remote code execution",
            "severity": "critical",
            "description": "Command injection",
        }],
    })
    monkeypatch.setattr(engine, "redis_client", redis)

    findings = engine._collect_service_findings("scan-1", ["nuclei"])

    assert findings == [{
        "id": "nuclei-0",
        "title": "Remote code execution",
        "severity": "critical",
        "description": "Command injection",
        "service": "nuclei",
    }]


def test_send_to_insightmap_posts_and_persists_analysis(monkeypatch):
    redis = FakeRedis()
    redis.hashes["scan:scan-1:meta"] = {
        "started_at": "2026-07-28T10:00:00",
        "completed_at": "2026-07-28T10:05:00",
    }
    captured = {}

    def fake_post(url, headers, json, timeout):
        captured.update({
            "url": url,
            "headers": headers,
            "json": json,
            "timeout": timeout,
        })
        return FakeResponse()

    monkeypatch.setattr(engine, "redis_client", redis)
    monkeypatch.setattr(engine, "INSIGHTMAP_URL", "http://insightmap")
    monkeypatch.setattr(engine, "INSIGHTMAP_API_KEY", "service-secret")
    monkeypatch.setattr(engine.httpx, "post", fake_post)

    result = engine.send_to_insightmap(
        "scan-1", "example.com", "black", ["nuclei"]
    )

    assert captured["url"] == "http://insightmap/api/security/pentest/analyze"
    assert captured["headers"] == {"X-API-Key": "service-secret"}
    assert captured["json"]["scan_id"] == "scan-1"
    assert result["risk_level"] == "High"
    stored = json.loads(redis.values["scan:scan-1:insightmap"])
    assert stored["risk_score"] == 8.2