"""
AgentLoops Example: SRE / Incident Response Agent
Industry: DevOps / Site Reliability Engineering
Use Case: AI incident responder that learns alert-to-root-cause mappings and reduces MTTR.
Expected ROI: Reduce mean time to resolution (MTTR) from 45 minutes to 5 minutes by
learning which alert patterns map to which runbooks. At $5K+/min for major outages,
each minute saved is real money.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_devops_")
    loops = AgentLoops("incident-responder", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: SRE / Incident Response Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track incident response actions.
    # Each run = one alert the agent triaged and responded to.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking incident responses ---\n")

    incidents = [
        {
            "input": "ALERT: high_cpu on api-gateway (92% for 5 min). "
                     "Service: api-gateway. Region: us-east-1. Time: 2:14 AM. "
                     "Concurrent alerts: none. Recent deploys: none in 24h.",
            "output": "Checked connection pool — found 850/1000 connections in use. "
                      "Ran `SELECT * FROM pg_stat_activity` — 200 idle connections from "
                      "stale pods. Killed idle connections, CPU dropped to 35%. "
                      "Root cause: pod scaling left zombie DB connections.",
            "outcome": "resolved",
            "metadata": {"alert_type": "high_cpu", "service": "api-gateway",
                         "root_cause": "connection_pool_exhaustion",
                         "mttr_minutes": 8, "severity": "P2",
                         "runbook_used": "db-connection-pool-check"},
        },
        {
            "input": "ALERT: high_memory on recommendation-service (95% for 3 min). "
                     "Service: recommendation-service. Region: us-east-1. "
                     "Concurrent alerts: high_latency on same service. "
                     "Recent deploys: model update deployed 2h ago.",
            "output": "Checked recent deploy — new ML model is 3x larger than previous. "
                      "Memory limit was set for old model size. Increased pod memory "
                      "from 4GB to 12GB. Restarted pods. Memory stabilized at 70%.",
            "outcome": "resolved",
            "metadata": {"alert_type": "high_memory", "service": "recommendation-service",
                         "root_cause": "model_size_increase",
                         "mttr_minutes": 12, "severity": "P2",
                         "runbook_used": "memory-limit-adjustment"},
        },
        {
            "input": "ALERT: error_rate_spike on payment-service (15% error rate, "
                     "baseline 0.1%). Service: payment-service. Region: us-east-1. "
                     "Concurrent alerts: high_latency on stripe-webhook. "
                     "Recent deploys: none.",
            "output": "Checked Stripe status page — no issues reported. Checked our "
                      "Stripe API key rotation — keys expired 30 min ago. "
                      "Rotated API keys. Error rate back to baseline.",
            "outcome": "resolved",
            "metadata": {"alert_type": "error_rate_spike", "service": "payment-service",
                         "root_cause": "expired_api_keys",
                         "mttr_minutes": 15, "severity": "P1",
                         "runbook_used": "api-key-rotation"},
        },
        {
            "input": "ALERT: disk_space_low on logging-service (92% disk usage). "
                     "Service: logging-service. Region: us-west-2. "
                     "Concurrent alerts: none. Recent deploys: none.",
            "output": "Investigated — log rotation cron job failed 3 days ago. "
                      "Manually rotated logs, freed 40GB. Fixed cron schedule. "
                      "Set up monitoring on cron job itself.",
            "outcome": "resolved",
            "metadata": {"alert_type": "disk_space_low", "service": "logging-service",
                         "root_cause": "failed_log_rotation",
                         "mttr_minutes": 6, "severity": "P3",
                         "runbook_used": "disk-cleanup"},
        },
        {
            "input": "ALERT: high_cpu on api-gateway (88% for 3 min). "
                     "Service: api-gateway. Region: us-east-1. Time: 9:02 AM. "
                     "Concurrent alerts: none. Recent deploys: none.",
            "output": "Checked connection pool — all normal at 200/1000. "
                      "Checked request volume — Black Friday traffic spike, 4x normal. "
                      "Scaled api-gateway from 5 to 15 pods. CPU normalized.",
            "outcome": "resolved",
            "metadata": {"alert_type": "high_cpu", "service": "api-gateway",
                         "root_cause": "traffic_spike",
                         "mttr_minutes": 4, "severity": "P2",
                         "runbook_used": "horizontal-scaling"},
        },
        {
            "input": "ALERT: high_latency on search-service (p99: 12s, baseline 200ms). "
                     "Service: search-service. Region: us-east-1. "
                     "Concurrent alerts: high_cpu on elasticsearch cluster. "
                     "Recent deploys: index schema change 1h ago.",
            "output": "Checked Elasticsearch — new index schema triggered reindexing "
                      "of 50M documents. Reindexing consuming all IO. "
                      "Throttled reindex rate to 500 docs/s. Latency recovered to 400ms "
                      "during reindex. Full recovery after reindex completed in 2h.",
            "outcome": "resolved",
            "metadata": {"alert_type": "high_latency", "service": "search-service",
                         "root_cause": "reindex_storm",
                         "mttr_minutes": 18, "severity": "P1",
                         "runbook_used": "elasticsearch-reindex-throttle"},
        },
        {
            "input": "ALERT: pod_crash_loop on auth-service (3 restarts in 5 min). "
                     "Service: auth-service. Region: us-east-1. "
                     "Concurrent alerts: none. Recent deploys: dependency update 30m ago.",
            "output": "Checked pod logs — OOM killed. New dependency has memory leak. "
                      "Rolled back to previous image. Pods stable. Filed bug with "
                      "dependency maintainer.",
            "outcome": "resolved",
            "metadata": {"alert_type": "pod_crash_loop", "service": "auth-service",
                         "root_cause": "dependency_memory_leak",
                         "mttr_minutes": 7, "severity": "P1",
                         "runbook_used": "rollback-deployment"},
        },
        {
            "input": "ALERT: high_cpu on monitoring-service (75% for 2 min). "
                     "Service: monitoring-service. Region: us-west-2. "
                     "Concurrent alerts: none. Recent deploys: none.",
            "output": "Investigated — CPU spike is from scheduled daily metric "
                      "aggregation job. This runs every day at this time. "
                      "Not actionable — marked as expected behavior.",
            "outcome": "false_alarm",
            "metadata": {"alert_type": "high_cpu", "service": "monitoring-service",
                         "root_cause": "scheduled_job",
                         "mttr_minutes": 3, "severity": "P3",
                         "runbook_used": None},
        },
    ]

    total_mttr = 0
    for i in incidents:
        run = loops.track(**i)
        m = i["metadata"]
        total_mttr += m["mttr_minutes"]
        icon = {"resolved": "FIX", "false_alarm": "N/A", "escalated": "ESC"}
        print(f"  [{icon.get(i['outcome'], '???'):3s}] {m['service']:25s} "
              f"| {m['alert_type']:20s} | {m['mttr_minutes']:2d} min "
              f"| {m.get('root_cause', 'n/a')}")

    avg_mttr = total_mttr / len(incidents)
    print(f"\n  Average MTTR: {avg_mttr:.0f} minutes")

    # -------------------------------------------------------------------
    # Phase 2: Rules mapping alert patterns to root causes.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF alert is high_cpu AND service is api-gateway AND time is overnight "
            "(12am-6am) THEN check connection pool first — because 2am high CPU was "
            "caused by zombie DB connections, not traffic",
            ["2:14 AM api-gateway incident: connection pool exhaustion, 8 min MTTR"],
            0.85,
        ),
        (
            "IF alert is high_cpu AND service is api-gateway AND time is business "
            "hours (8am-8pm) THEN check request volume and scale horizontally — "
            "because 9am spike was traffic, not infrastructure",
            ["9:02 AM api-gateway incident: traffic spike resolved by scaling, 4 min MTTR"],
            0.80,
        ),
        (
            "IF alert is high_memory AND there was a deploy in the last 4 hours "
            "THEN check if deploy changed resource requirements — because model "
            "update caused 3x memory increase",
            ["recommendation-service: new model was 3x larger than old model"],
            0.88,
        ),
        (
            "IF alert is error_rate_spike AND service handles third-party APIs "
            "THEN check API key expiration before checking vendor status — because "
            "expired keys are faster to diagnose than waiting for vendor status pages",
            ["payment-service: Stripe keys expired, 15 min MTTR"],
            0.82,
        ),
        (
            "IF alert is high_cpu AND service is monitoring-service AND alert is "
            "between 2-4am THEN likely scheduled aggregation job — classify as "
            "false alarm without investigation",
            ["monitoring-service: daily aggregation job flagged as false alarm"],
            0.90,
        ),
        (
            "IF alert is pod_crash_loop AND there was a dependency update in the "
            "last 2 hours THEN roll back first, investigate second — because "
            "rollback is faster than debugging a memory leak in a new dependency",
            ["auth-service: dependency memory leak, rollback resolved in 7 min"],
            0.92,
        ),
    ]

    for text, evidence, confidence in rules:
        loops.rules.add_rule(text=text, evidence=evidence, confidence=confidence)
        print(f"  Rule ({confidence:.0%}): {text[:75]}...")

    # -------------------------------------------------------------------
    # Phase 3: Conventions.
    # -------------------------------------------------------------------
    print("\n--- Phase 3: Adding conventions ---\n")

    conventions = [
        ("Always check recent deploys first — 50% of incidents correlate with "
         "a deploy in the last 4 hours. If a deploy happened, it's the likely cause.",
         "derived from deploy-correlated incidents"),
        ("Time of day matters for root cause analysis. Overnight high CPU is usually "
         "infrastructure (connection leaks, stuck jobs). Daytime is usually traffic.",
         "derived from api-gateway time-of-day pattern"),
        ("For crash loops, roll back first, then investigate. Minimizing MTTR is more "
         "important than understanding root cause in the moment.",
         "derived from auth-service rollback success"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are an incident response agent for a cloud-native infrastructure. "
            "When alerts fire, diagnose the root cause and resolve as fast as possible. "
            "Minimize MTTR. Escalate only when necessary.")
    enhanced = loops.enhance_prompt(base)
    for line in enhanced.split("\n"):
        if line.strip():
            print(f"  {line}")

    # -------------------------------------------------------------------
    # Phase 5: Summary.
    # -------------------------------------------------------------------
    print("\n--- Phase 5: Memory pruning ---\n")
    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Pruned: {len(pruned['rules_pruned'])} rules, "
          f"{len(pruned['conventions_pruned'])} conventions")

    print(f"\n--- Summary ---\n")
    resolved = sum(1 for i in incidents if i["outcome"] == "resolved")
    false_alarms = sum(1 for i in incidents if i["outcome"] == "false_alarm")
    print(f"  Incidents tracked: {len(incidents)}")
    print(f"  Resolved: {resolved} | False alarms: {false_alarms}")
    print(f"  Average MTTR: {avg_mttr:.0f} min (target: <5 min)")
    print(f"  Fastest resolution: {min(i['metadata']['mttr_minutes'] for i in incidents)} min")
    print(f"  Slowest resolution: {max(i['metadata']['mttr_minutes'] for i in incidents)} min")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
