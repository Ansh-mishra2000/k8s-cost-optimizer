from services.analyzer import Analyzer
from services.cost_analyzer import CostAnalyzer


def test_calculate_cpu_waste():
    # 0.5 cores requested, 0.1 cores used -> 80% waste
    waste = Analyzer.calculate_cpu_waste(requested_cpu=0.5, actual_cpu=0.1)
    assert waste == 80.0

    # 0 cores requested -> 0 waste
    assert Analyzer.calculate_cpu_waste(0, 0.1) == 0


def test_recommend_cpu():
    # 0.2 cores actual * 1.2 safety buffer -> 0.24 cores
    recommended = Analyzer.recommend_cpu(requested_cpu=0.5, actual_cpu=0.2)
    assert recommended == 0.24


def test_recommend_memory_enforces_minimum():
    # 10 MiB actual * 1.2 = 12 MiB (< 64 MiB policy floor) -> should return 64 MiB
    recommended, explanation = Analyzer.recommend_memory(requested_memory=128, actual_memory=10)
    assert recommended == 64
    assert explanation["minimum_memory_policy_mib"] == 64


def test_cost_analyzer_monthly_savings():
    current_cost = 25.50
    optimized_cost = 10.20
    savings = CostAnalyzer.calculate_monthly_savings(current_cost, optimized_cost)
    assert savings == 15.30
