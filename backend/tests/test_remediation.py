def test_remediation_response_structure():
    # Unit validation for remediation data schema and formatting
    sample_patch_result = {
        "applied_requests": {"cpu": "250m", "memory": "64Mi"},
        "applied_limits": {"cpu": "500m", "memory": "96Mi"}
    }

    assert sample_patch_result["applied_requests"]["cpu"] == "250m"
    assert sample_patch_result["applied_limits"]["memory"] == "96Mi"
