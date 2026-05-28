import csv
import json
import random
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
ANALYSIS_DIR = ROOT / "analysis"

random.seed(27)


OPPORTUNITIES = [
    {
        "id": "OPP-001",
        "name": "Renewal risk copilot",
        "product_area": "Lease and renewal pricing",
        "persona": "Revenue manager",
        "problem": "Teams need earlier renewal risk signals when lease trade-outs, occupancy, and local comps move in different directions.",
        "hypothesis": "A guided renewal risk queue will reduce manual review time and improve renewal pricing confidence.",
        "primary_metric": "renewal recommendation adoption",
        "north_star_lift": 7.5,
        "engineering_effort": 6,
        "compliance_risk": 4,
        "dependencies": "Pricing service, renewal event feed, comp explanation cards",
    },
    {
        "id": "OPP-002",
        "name": "Explainable comp set builder",
        "product_area": "Public market intelligence",
        "persona": "Asset manager",
        "problem": "Users trust pricing recommendations faster when they can see why a comp property was included or excluded.",
        "hypothesis": "Transparent comp rationale will reduce overrides caused by low trust.",
        "primary_metric": "pricing override rate",
        "north_star_lift": 5.9,
        "engineering_effort": 5,
        "compliance_risk": 3,
        "dependencies": "Comp ingestion, geospatial filters, data freshness checks",
    },
    {
        "id": "OPP-003",
        "name": "Specials and concessions guardrails",
        "product_area": "Amenities and specials",
        "persona": "Regional operator",
        "problem": "Operators need guardrails that explain when concessions improve velocity and when they dilute revenue.",
        "hypothesis": "A guardrail workflow will improve concession decisions during soft demand periods.",
        "primary_metric": "approved concession variance",
        "north_star_lift": 6.8,
        "engineering_effort": 7,
        "compliance_risk": 5,
        "dependencies": "Specials feed, occupancy forecast, approval workflow",
    },
    {
        "id": "OPP-004",
        "name": "Amenity value tuner",
        "product_area": "Amenities and specials",
        "persona": "Portfolio analyst",
        "problem": "Amenity premiums often stay static even when local demand shifts.",
        "hypothesis": "Unit-level amenity recommendations will unlock incremental revenue without changing base rent logic.",
        "primary_metric": "amenity premium adoption",
        "north_star_lift": 4.8,
        "engineering_effort": 8,
        "compliance_risk": 6,
        "dependencies": "Unit inventory feed, amenity catalog, audit trail",
    },
    {
        "id": "OPP-005",
        "name": "Portfolio goal scenario planner",
        "product_area": "Reporting",
        "persona": "Owner",
        "problem": "Executives want to test revenue, occupancy, and concession goals before pushing strategy changes to properties.",
        "hypothesis": "Scenario planning will align portfolio goals with property-level pricing decisions.",
        "primary_metric": "scenario to action conversion",
        "north_star_lift": 6.1,
        "engineering_effort": 9,
        "compliance_risk": 4,
        "dependencies": "Goal model, reporting aggregates, permissions",
    },
    {
        "id": "OPP-006",
        "name": "Data quality launch gate",
        "product_area": "Implementation readiness",
        "persona": "Customer success",
        "problem": "Pricing users lose confidence when rent roll, renewal, or comp feeds are stale during onboarding.",
        "hypothesis": "A launch gate will prevent poor first-week experiences and speed time to value.",
        "primary_metric": "same-week launch readiness",
        "north_star_lift": 5.4,
        "engineering_effort": 4,
        "compliance_risk": 2,
        "dependencies": "Ingestion monitor, property setup checklist, CS workflow",
    },
    {
        "id": "OPP-007",
        "name": "Approval workflow and audit trail",
        "product_area": "Security and privacy",
        "persona": "Regional operator",
        "problem": "Operators need to document who approved pricing changes, exceptions, and fair housing review notes.",
        "hypothesis": "A lightweight approval flow will reduce offline approvals and increase enterprise readiness.",
        "primary_metric": "offline approval reduction",
        "north_star_lift": 4.6,
        "engineering_effort": 6,
        "compliance_risk": 7,
        "dependencies": "Roles, audit events, notification service",
    },
    {
        "id": "OPP-008",
        "name": "Conversational insight follow-up",
        "product_area": "AI insights",
        "persona": "Revenue manager",
        "problem": "Users want to ask follow-up questions when the system flags a revenue anomaly.",
        "hypothesis": "Conversational drill-down will shorten analysis time for anomaly investigation.",
        "primary_metric": "insight follow-up completion",
        "north_star_lift": 6.4,
        "engineering_effort": 8,
        "compliance_risk": 6,
        "dependencies": "Insight store, permissions, retrieval evaluation",
    },
]

THEMES = [
    ("renewal confidence", "OPP-001", "Lease and renewal pricing"),
    ("comp transparency", "OPP-002", "Public market intelligence"),
    ("concession guardrails", "OPP-003", "Amenities and specials"),
    ("amenity pricing", "OPP-004", "Amenities and specials"),
    ("portfolio scenario planning", "OPP-005", "Reporting"),
    ("onboarding data quality", "OPP-006", "Implementation readiness"),
    ("approval auditability", "OPP-007", "Security and privacy"),
    ("AI follow-up questions", "OPP-008", "AI insights"),
]

PERSONAS = [
    ("Revenue manager", 0.29),
    ("Asset manager", 0.22),
    ("Regional operator", 0.18),
    ("Portfolio analyst", 0.16),
    ("Customer success", 0.10),
    ("Owner", 0.05),
]

SOURCES = ["customer interview", "CS note", "sales call", "beta feedback", "support thread"]
PORTFOLIO_SIZES = [1800, 3200, 6400, 9800, 14500, 21000, 36000]


def weighted_choice(items):
    names = [name for name, _ in items]
    weights = [weight for _, weight in items]
    return random.choices(names, weights=weights, k=1)[0]


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_feedback():
    start = date(2026, 1, 6)
    rows = []
    for idx in range(1, 121):
        theme, opp_id, area = random.choice(THEMES)
        persona = weighted_choice(PERSONAS)
        pain_base = {
            "renewal confidence": 8,
            "comp transparency": 8,
            "concession guardrails": 7,
            "amenity pricing": 6,
            "portfolio scenario planning": 7,
            "onboarding data quality": 7,
            "approval auditability": 6,
            "AI follow-up questions": 7,
        }[theme]
        pain = min(10, max(3, round(random.gauss(pain_base, 1.2))))
        urgency = "high" if pain >= 8 else "medium" if pain >= 6 else "low"
        rows.append(
            {
                "feedback_id": f"FB-{idx:03d}",
                "date": (start + timedelta(days=random.randint(0, 112))).isoformat(),
                "persona": persona,
                "portfolio_units": random.choice(PORTFOLIO_SIZES),
                "source": random.choice(SOURCES),
                "theme": theme,
                "product_area": area,
                "linked_opportunity": opp_id,
                "pain_score": pain,
                "urgency": urgency,
                "quote_summary": summarize_quote(persona, theme),
            }
        )
    return rows


def summarize_quote(persona, theme):
    templates = {
        "renewal confidence": f"{persona} needs earlier renewal risk context before recommending price moves.",
        "comp transparency": f"{persona} wants clearer reasons behind comp selection and exclusions.",
        "concession guardrails": f"{persona} wants a safer way to compare concessions against leasing velocity.",
        "amenity pricing": f"{persona} sees amenity premiums drifting from current demand patterns.",
        "portfolio scenario planning": f"{persona} needs to test portfolio goals before changing property strategy.",
        "onboarding data quality": f"{persona} needs stale feed issues surfaced before first pricing review.",
        "approval auditability": f"{persona} wants approvals and exceptions captured inside the workflow.",
        "AI follow-up questions": f"{persona} wants to ask why an anomaly appeared without exporting data.",
    }
    return templates[theme]


def generate_usage():
    rows = []
    start = date(2026, 1, 1)
    for day_idx in range(120):
        current = start + timedelta(days=day_idx)
        for opportunity in OPPORTUNITIES:
            adoption_base = 0.36 + opportunity["north_star_lift"] / 28
            override_base = 0.31 - opportunity["north_star_lift"] / 60
            rows.append(
                {
                    "date": current.isoformat(),
                    "opportunity_id": opportunity["id"],
                    "product_area": opportunity["product_area"],
                    "active_accounts": random.randint(18, 68),
                    "pricing_recommendations": random.randint(90, 520),
                    "adoption_rate": round(min(0.82, max(0.18, random.gauss(adoption_base, 0.07))), 3),
                    "override_rate": round(min(0.46, max(0.06, random.gauss(override_base, 0.055))), 3),
                    "explainability_open_rate": round(min(0.88, max(0.22, random.gauss(0.56, 0.12))), 3),
                    "approval_latency_hours": round(min(72, max(4, random.gauss(24, 9))), 1),
                    "manual_export_count": random.randint(4, 38),
                    "data_freshness_score": round(min(0.99, max(0.70, random.gauss(0.91, 0.055))), 3),
                }
            )
    return rows


def score_opportunities(feedback_rows, usage_rows):
    feedback_by_opp = defaultdict(list)
    for row in feedback_rows:
        feedback_by_opp[row["linked_opportunity"]].append(row)

    usage_by_opp = defaultdict(list)
    for row in usage_rows:
        usage_by_opp[row["opportunity_id"]].append(row)

    scored = []
    for opportunity in OPPORTUNITIES:
        opp_id = opportunity["id"]
        feedback = feedback_by_opp[opp_id]
        usage = usage_by_opp[opp_id]
        avg_pain = sum(int(row["pain_score"]) for row in feedback) / len(feedback)
        high_urgency = sum(1 for row in feedback if row["urgency"] == "high")
        avg_adoption = sum(float(row["adoption_rate"]) for row in usage) / len(usage)
        avg_override = sum(float(row["override_rate"]) for row in usage) / len(usage)
        avg_freshness = sum(float(row["data_freshness_score"]) for row in usage) / len(usage)
        customer_pull = min(100, avg_pain * 8 + high_urgency * 2.2)
        revenue_impact = min(100, opportunity["north_star_lift"] * 9.5 + (1 - avg_override) * 22)
        strategy_fit = {
            "Lease and renewal pricing": 94,
            "Public market intelligence": 88,
            "Amenities and specials": 82,
            "Reporting": 78,
            "Implementation readiness": 84,
            "Security and privacy": 76,
            "AI insights": 86,
        }[opportunity["product_area"]]
        confidence = min(100, len(feedback) * 3.1 + avg_adoption * 44 + avg_freshness * 18)
        effort_penalty = opportunity["engineering_effort"] * 6
        risk_penalty = opportunity["compliance_risk"] * 4
        priority = (
            customer_pull * 0.28
            + revenue_impact * 0.24
            + strategy_fit * 0.20
            + confidence * 0.18
            - effort_penalty * 0.06
            - risk_penalty * 0.04
        )
        stage = "Beta candidate" if priority >= 72 else "Discovery" if priority >= 66 else "Backlog"
        scored.append(
            {
                **opportunity,
                "feedback_count": len(feedback),
                "high_urgency_count": high_urgency,
                "avg_pain_score": round(avg_pain, 1),
                "avg_adoption_rate": round(avg_adoption, 3),
                "avg_override_rate": round(avg_override, 3),
                "data_freshness_score": round(avg_freshness, 3),
                "customer_pull": round(customer_pull, 1),
                "revenue_impact": round(revenue_impact, 1),
                "strategy_fit": strategy_fit,
                "confidence": round(confidence, 1),
                "priority_score": round(priority, 1),
                "stage": stage,
            }
        )
    return sorted(scored, key=lambda row: row["priority_score"], reverse=True)


def build_launch_plan(scored):
    top = scored[0]
    return [
        {
            "phase": "Discovery close",
            "owner": "Product",
            "gate": "Confirm top three renewal workflows with five customer calls",
            "metric": "problem validation rate >= 70%",
            "status": "ready",
        },
        {
            "phase": "Design partner beta",
            "owner": "Product and Design",
            "gate": "Prototype queue, explanation cards, and exception notes with design partners",
            "metric": "task success >= 80%",
            "status": "planned",
        },
        {
            "phase": "Engineering build",
            "owner": "Engineering",
            "gate": f"Ship {top['name'].lower()} behind account-level feature flag",
            "metric": "p95 queue load < 1.5 seconds",
            "status": "planned",
        },
        {
            "phase": "Compliance review",
            "owner": "Product and Legal",
            "gate": "Review data fields, explanations, and audit events for fair housing sensitivity",
            "metric": "zero unresolved launch blockers",
            "status": "planned",
        },
        {
            "phase": "GA readiness",
            "owner": "Product, CS, Sales",
            "gate": "Enable playbook, release notes, training, and adoption dashboard",
            "metric": "beta adoption >= 60% and support rate <= 2 tickets per account",
            "status": "planned",
        },
    ]


def write_analysis_docs(scored, feedback_rows, usage_rows, launch_plan):
    top = scored[0]
    theme_counts = Counter(row["theme"] for row in feedback_rows)
    persona_counts = Counter(row["persona"] for row in feedback_rows)
    avg_override = sum(float(row["override_rate"]) for row in usage_rows) / len(usage_rows)
    avg_latency = sum(float(row["approval_latency_hours"]) for row in usage_rows) / len(usage_rows)

    executive = f"""# Executive Findings

## What I analyzed

I synthesized {len(feedback_rows)} customer evidence records and {len(usage_rows)} product telemetry rows for a multifamily revenue intelligence product roadmap. The analysis connects customer interviews, customer success notes, product usage, pricing workflow signals, engineering effort, and compliance risk.

## Findings

- The highest-priority product bet is **{top["name"]}** with a priority score of **{top["priority_score"]}**.
- The strongest evidence theme is **{theme_counts.most_common(1)[0][0]}**, with **{theme_counts.most_common(1)[0][1]}** records.
- The most represented persona is **{persona_counts.most_common(1)[0][0]}**, which is consistent with a product used by pricing and operating teams.
- The synthetic telemetry shows an average pricing override rate of **{avg_override:.1%}** and average approval latency of **{avg_latency:.1f} hours**.

## Recommendation

Prioritize the top roadmap bet as a design partner beta, while using the launch gate to protect data quality, explanation quality, and fair housing review before general availability.
"""
    plan = """# Analysis Plan

1. Collect customer evidence at feedback-record grain across interviews, CS notes, support threads, sales calls, and beta feedback.
2. Map each evidence record to a product opportunity and product area.
3. Aggregate usage telemetry by opportunity, including adoption, override behavior, explainability engagement, approval latency, export behavior, and data freshness.
4. Score opportunities with a transparent weighted model.
5. Convert the winning opportunity into a PRD-ready launch plan with gates, owners, success metrics, and risks.
"""
    sql = """-- Portfolio SQL examples for roadmap prioritization review.
-- These examples assume the CSVs have been loaded into warehouse tables.

select
  linked_opportunity,
  count(*) as feedback_count,
  avg(pain_score) as avg_pain_score,
  sum(case when urgency = 'high' then 1 else 0 end) as high_urgency_count
from customer_feedback
group by 1
order by high_urgency_count desc, avg_pain_score desc;

select
  opportunity_id,
  avg(adoption_rate) as avg_adoption_rate,
  avg(override_rate) as avg_override_rate,
  avg(approval_latency_hours) as avg_approval_latency_hours,
  avg(data_freshness_score) as avg_data_freshness_score
from product_usage
group by 1;

select
  name,
  product_area,
  priority_score,
  stage,
  primary_metric
from roadmap_priority
order by priority_score desc;
"""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    (ANALYSIS_DIR / "executive_findings.md").write_text(executive)
    (ANALYSIS_DIR / "analysis_plan.md").write_text(plan)
    (ANALYSIS_DIR / "sql_checks.sql").write_text(sql)


def build_payload(scored, feedback_rows, usage_rows, launch_plan):
    theme_counts = Counter(row["theme"] for row in feedback_rows)
    persona_counts = Counter(row["persona"] for row in feedback_rows)
    source_counts = Counter(row["source"] for row in feedback_rows)
    top = scored[0]
    requirements = [
        "Show every renewal risk item with the account goal, property context, lease exposure, and recommended action.",
        "Explain why the item is in the queue using recent occupancy movement, pricing override behavior, comp changes, and renewal timing.",
        "Allow product, CS, and operators to capture exception notes and approval status without leaving the workflow.",
        "Instrument queue views, explanation opens, recommendation accepts, overrides, and exception reasons.",
        "Gate launch by feed freshness, explanation coverage, fair housing review, and support readiness.",
    ]
    non_goals = [
        "Replace human pricing approval.",
        "Expose customer-private market data across accounts.",
        "Optimize every amenity or concession workflow in the first release.",
    ]
    risks = [
        "Users may distrust recommendations if comp rationale is incomplete.",
        "Sparse renewal data can create noisy prioritization for smaller properties.",
        "Compliance review must be complete before scaling beyond design partners.",
        "CS enablement needs to explain why the beta is narrow by design.",
    ]
    metrics = [
        {"label": "Feedback records", "value": len(feedback_rows), "context": "synthetic customer evidence"},
        {"label": "Telemetry rows", "value": len(usage_rows), "context": "120 days x 8 opportunities"},
        {"label": "Top score", "value": top["priority_score"], "context": top["name"]},
        {"label": "Beta gates", "value": len(launch_plan), "context": "concept to GA"},
    ]
    return {
        "generated_on": date.today().isoformat(),
        "summary": {
            "title": "Multifamily Revenue Roadmap Strategy Studio",
            "subtitle": "A PM artifact for turning customer evidence and product telemetry into a PRD-ready roadmap bet.",
            "domain": "multifamily revenue intelligence",
            "top_opportunity": top,
            "metrics": metrics,
        },
        "evidence": {
            "theme_counts": [{"name": key, "count": value} for key, value in theme_counts.most_common()],
            "persona_counts": [{"name": key, "count": value} for key, value in persona_counts.most_common()],
            "source_counts": [{"name": key, "count": value} for key, value in source_counts.most_common()],
            "recent_feedback": sorted(feedback_rows, key=lambda row: row["date"], reverse=True)[:12],
        },
        "roadmap": scored,
        "prd": {
            "selected": top,
            "requirements": requirements,
            "non_goals": non_goals,
            "risks": risks,
            "launch_plan": launch_plan,
        },
    }


def main():
    feedback_rows = generate_feedback()
    usage_rows = generate_usage()
    scored = score_opportunities(feedback_rows, usage_rows)
    launch_plan = build_launch_plan(scored)

    write_csv(
        DATA_DIR / "customer_feedback.csv",
        feedback_rows,
        [
            "feedback_id",
            "date",
            "persona",
            "portfolio_units",
            "source",
            "theme",
            "product_area",
            "linked_opportunity",
            "pain_score",
            "urgency",
            "quote_summary",
        ],
    )
    write_csv(
        DATA_DIR / "product_usage.csv",
        usage_rows,
        [
            "date",
            "opportunity_id",
            "product_area",
            "active_accounts",
            "pricing_recommendations",
            "adoption_rate",
            "override_rate",
            "explainability_open_rate",
            "approval_latency_hours",
            "manual_export_count",
            "data_freshness_score",
        ],
    )
    write_csv(
        OUTPUT_DIR / "roadmap_priority.csv",
        scored,
        [
            "id",
            "name",
            "product_area",
            "persona",
            "problem",
            "hypothesis",
            "primary_metric",
            "north_star_lift",
            "engineering_effort",
            "compliance_risk",
            "dependencies",
            "feedback_count",
            "high_urgency_count",
            "avg_pain_score",
            "avg_adoption_rate",
            "avg_override_rate",
            "data_freshness_score",
            "customer_pull",
            "revenue_impact",
            "strategy_fit",
            "confidence",
            "priority_score",
            "stage",
        ],
    )
    write_csv(
        OUTPUT_DIR / "launch_plan.csv",
        launch_plan,
        ["phase", "owner", "gate", "metric", "status"],
    )

    payload = build_payload(scored, feedback_rows, usage_rows, launch_plan)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "app_payload.json").write_text(json.dumps(payload, indent=2))
    write_analysis_docs(scored, feedback_rows, usage_rows, launch_plan)
    print(f"Top opportunity: {scored[0]['name']} ({scored[0]['priority_score']})")
    print(f"Feedback records: {len(feedback_rows)}")
    print(f"Telemetry rows: {len(usage_rows)}")


if __name__ == "__main__":
    main()
