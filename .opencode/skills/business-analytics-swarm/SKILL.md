# Business Analytics Swarm

AI-driven business metrics and dashboard system synthesized from `swarm_business_analytics.py`, `business_dashboard/main.py`, `LILITH_SYSTEMS_BUSINESS_REPORT_20260611.json`.

## Metrics Pipeline

```
Raw Data → Aggregation → Insight Generation → Dashboard → Report
  │            │               │                  │
  ├─ Users     ├─ DAU/WAU/MAU  ├─ Trend analysis  ├─ REST API
  ├─ Revenue   ├─ ARPU/ARPPU   ├─ Anomaly detect  ├─ JSON export
  ├─ Activity  ├─ Retention    ├─ Forecasting     └─ PDF report
  └─ Costs     └─ Churn        └─ Recommendations
```

## Swarm Agents

| Agent | Function |
|-------|----------|
| Data Collector | Pulls metrics from services (API, DB, logs) |
| Aggregator | Computes KPIs from raw data |
| Trend Analyzer | Detects patterns, seasonality, anomalies |
| Forecaster | Generates predictions (7/30/90 day) |
| Reporter | Produces formatted reports and dashboards |

## Key Metrics

| Category | Metrics |
|----------|---------|
| Growth | DAU, WAU, MAU, new users, signup rate |
| Engagement | Sessions/user, session duration, actions/session |
| Revenue | MRR, ARPU, ARPPU, LTV, conversion rate |
| Retention | D1/D7/D30 retention, churn rate, re-engagement |
| Quality | Error rate, latency P50/P95/P99, uptime |
| AI | Inference requests, latency, token usage, VRAM |

## Insight Generation

AI analyzes metric cross-correlations to produce:
- **Signals**: statistically significant changes
- **Anomalies**: deviations from expected ranges
- **Recommendations**: actionable changes ranked by impact
- **Alerts**: critical threshold breaches

## Dashboard Endpoint

`GET /dashboard` returns full dashboard JSON:
```json
{
  "summary": { "dau": 42, "mrr": 3500, "uptime": 0.9997 },
  "trends": { "growth": "+12% WoW", "engagement": "-3% WoW" },
  "insights": ["DAU spike correlated with dredge event"],
  "alerts": ["VRAM usage > 85% for 2h"]
}
```

## Configuration

- `data_sources`: list of API endpoints or db queries
- `aggregation_window`: 1h, 1d, 7d, 30d
- `insight_llm`: model for insight generation (default: nemotron-mini)
- `alert_thresholds`: per-metric threshold config
- `report_schedule`: cron expression for automated reports
