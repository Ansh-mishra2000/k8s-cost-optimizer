from services.ai_service import AIService


def test_ai_engine_overprovisioned_analysis():
    ai = AIService()
    metrics = {
        "deployment": "payment-service",
        "requested_cpu": 0.5,
        "actual_cpu": 0.05,
        "recommended_cpu": 0.1,
        "peak_cpu_24h": 0.07,
        "requested_memory_mib": 128,
        "actual_memory_mib": 32,
        "recommended_memory_mib": 64,
        "monthly_total_cost_usd": 20.0,
        "monthly_total_savings_usd": 15.0,
        "instance_type": "t3.small"
    }

    result = ai.generate_explanation(metrics)

    assert result["status"] == "Severely Overprovisioned"
    assert result["risk_level"] == "Very Low"
    assert "15.0" in result["financial_impact"]
    assert "resources:" in result["recommended_yaml_snippet"]


def test_ai_engine_underprovisioned_analysis():
    ai = AIService()
    metrics = {
        "deployment": "stress-app",
        "requested_cpu": 0.1,
        "actual_cpu": 0.25,
        "recommended_cpu": 0.30,
        "peak_cpu_24h": 0.25,
        "requested_memory_mib": 64,
        "actual_memory_mib": 50,
        "recommended_memory_mib": 64,
        "monthly_total_cost_usd": 5.0,
        "monthly_total_savings_usd": -6.0,
        "instance_type": "t3.small"
    }

    result = ai.generate_explanation(metrics)

    assert result["status"] == "Underprovisioned (Throttling Risk)"
    assert "stability" in result["financial_impact"].lower()
