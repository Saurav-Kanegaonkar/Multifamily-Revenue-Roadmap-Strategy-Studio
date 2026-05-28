-- Portfolio SQL examples for roadmap prioritization review.
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
