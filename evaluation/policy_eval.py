# evaluation/policy_eval.py

import time
from typing import Dict, List, Any

def simulate_departures(decision: Dict[str, Any]) -> int:
    """
    Naive departure model:
    - Departures scale with green duration; cap to avoid runaway.
    - Emergency phase yields boosted throughput (simulates priority lane clearing).
    """
    green = int(decision.get("green", 0))
    phase = decision.get("phase", "NORMAL")
    base_rate = 1  # vehicles per simulated second (demo scale)
    boost = 2 if phase == "EMERGENCY" else 1
    return min(green * base_rate * boost, 30)


def compute_queue_metrics(observations: Dict[str, List[int]],
                          decisions: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    For each junction:
    - arrivals: sum of observed lane counts
    - departures: simulated from decision
    - queue_after: max(arrivals - departures, 0)
    """
    metrics = {}
    for inter_id, counts in observations.items():
        # observations may be raw list or dict {"counts": [...], "emergency": bool}
        if isinstance(counts, dict):
            arrivals = sum(counts.get("counts", []))
            emergency = bool(counts.get("emergency", False))
        else:
            arrivals = sum(counts)
            emergency = False

        decision = decisions.get(inter_id, {})
        departures = simulate_departures(decision)
        queue_after = max(arrivals - departures, 0)

        metrics[inter_id] = {
            "arrivals": float(arrivals),
            "departures": float(departures),
            "queue_after": float(queue_after),
            "emergency": float(1 if emergency or decision.get("phase") == "EMERGENCY" else 0),
        }
    return metrics


def fairness_index(metrics: Dict[str, Dict[str, float]]) -> float:
    """
    Jain's fairness index over departures across junctions:
    J(x) = (sum(x))^2 / (N * sum(x^2)); ranges 0..1 (higher is fairer).
    """
    deps = [m["departures"] for m in metrics.values()]
    if not deps:
        return 1.0
    s1 = sum(deps)
    s2 = sum(d * d for d in deps)
    n = len(deps)
    if s2 == 0:
        return 1.0
    return (s1 * s1) / (n * s2)


def queue_reduction_score(metrics: Dict[str, Dict[str, float]]) -> float:
    """
    Average fractional reduction: 1 - queue_after/arrivals (per junction), averaged.
    If arrivals == 0, treat reduction as 1 (no queue).
    """
    scores = []
    for m in metrics.values():
        a = m["arrivals"]
        q = m["queue_after"]
        if a <= 0:
            scores.append(1.0)
        else:
            scores.append(max(0.0, 1.0 - q / a))
    return sum(scores) / max(1, len(scores))


def emergency_effect(metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Measures how emergency overrides influenced throughput:
    - emergency_departures: sum of departures where emergency==1
    - normal_departures: sum of departures where emergency==0
    - boost_ratio: emergency_departures / (normal_departures / max(1, normal_count))
      normalized by average normal departures per junction.
    """
    emergency_deps = [m["departures"] for m in metrics.values() if m["emergency"] == 1]
    normal_deps = [m["departures"] for m in metrics.values() if m["emergency"] == 0]
    emergency_departures = sum(emergency_deps)
    normal_departures = sum(normal_deps)
    normal_avg = normal_departures / max(1, len(normal_deps))
    boost_ratio = (emergency_departures / max(1e-6, normal_avg)) if normal_avg > 0 else 1.0
    return {
        "emergency_departures": float(emergency_departures),
        "normal_departures": float(normal_departures),
        "normal_avg_departures": float(normal_avg),
        "boost_ratio": float(boost_ratio),
    }


def latency_metrics(timestamps: Dict[str, float]) -> Dict[str, float]:
    """
    Given timestamps:
    - t_obs_start: before vision fan-out
    - t_obs_end: after observations collected
    - t_policy_end: after decisions computed
    - t_apply_end: after control loop apply completes
    Returns per-stage latencies.
    """
    t_obs_start = timestamps.get("t_obs_start", time.time())
    t_obs_end = timestamps.get("t_obs_end", t_obs_start)
    t_policy_end = timestamps.get("t_policy_end", t_obs_end)
    t_apply_end = timestamps.get("t_apply_end", t_policy_end)

    return {
        "latency_observation": max(0.0, t_obs_end - t_obs_start),
        "latency_policy": max(0.0, t_policy_end - t_obs_end),
        "latency_apply": max(0.0, t_apply_end - t_policy_end),
        "latency_cycle_total": max(0.0, t_apply_end - t_obs_start),
    }


def evaluate(observations: Dict[str, Any],
             decisions: Dict[str, Dict[str, Any]],
             timestamps: Dict[str, float]) -> Dict[str, Any]:
    """
    Top-level evaluation:
    - per_junction metrics
    - system metrics: fairness, queue reduction, emergency effect, latencies
    """
    per_junction = compute_queue_metrics(observations, decisions)
    fair = fairness_index(per_junction)
    reduction = queue_reduction_score(per_junction)
    emer = emergency_effect(per_junction)
    lats = latency_metrics(timestamps)

    return {
        "per_junction": per_junction,
        "system": {
            "fairness_jain": round(fair, 4),
            "queue_reduction_avg": round(reduction, 4),
            "emergency_effect": emer,
            "latency": {k: round(v, 4) for k, v in lats.items()},
        },
    }
