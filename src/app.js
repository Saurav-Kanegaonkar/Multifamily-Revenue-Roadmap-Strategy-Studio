const state = {
  payload: null,
  selectedOpportunityId: null,
};

const currency = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

function qs(selector) {
  return document.querySelector(selector);
}

function qsa(selector) {
  return [...document.querySelectorAll(selector)];
}

function percent(value) {
  return `${Math.round(value * 100)}%`;
}

function setView(viewName) {
  qsa(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  qsa(".view").forEach((view) => {
    view.classList.toggle("active", view.id === `${viewName}View`);
  });
}

function renderMetrics(metrics) {
  qs("#metricGrid").innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card">
          <span>${metric.label}</span>
          <strong>${currency.format(metric.value)}</strong>
          <p>${metric.context}</p>
        </article>
      `
    )
    .join("");
}

function renderBars(selector, items) {
  const max = Math.max(...items.map((item) => item.count));
  qs(selector).innerHTML = items
    .map(
      (item) => `
        <div class="bar-row">
          <div class="bar-label">
            <span>${item.name}</span>
            <strong>${item.count}</strong>
          </div>
          <div class="bar-track">
            <span style="width:${Math.max(8, (item.count / max) * 100)}%"></span>
          </div>
        </div>
      `
    )
    .join("");
}

function renderFeedback(items) {
  qs("#feedbackList").innerHTML = items
    .map(
      (item) => `
        <article class="feedback-item">
          <div>
            <strong>${item.theme}</strong>
            <span>${item.persona} | ${item.source} | ${item.date}</span>
          </div>
          <p>${item.quote_summary}</p>
          <b>${item.urgency}</b>
        </article>
      `
    )
    .join("");
}

function renderPriorityQueue(items) {
  qs("#priorityQueue").innerHTML = items
    .map(
      (item, index) => `
        <button class="priority-row ${item.id === state.selectedOpportunityId ? "selected" : ""}" type="button" data-id="${item.id}">
          <span class="rank">${index + 1}</span>
          <span class="priority-main">
            <strong>${item.name}</strong>
            <em>${item.product_area} | ${item.persona}</em>
          </span>
          <span class="priority-score">${item.priority_score}</span>
        </button>
      `
    )
    .join("");

  qsa(".priority-row").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedOpportunityId = button.dataset.id;
      renderPriorityQueue(state.payload.roadmap);
      renderPrd();
      setView("prd");
    });
  });
}

function selectedOpportunity() {
  return (
    state.payload.roadmap.find((item) => item.id === state.selectedOpportunityId) ||
    state.payload.roadmap[0]
  );
}

function renderSelectedBrief(opportunity) {
  qs("#selectedBrief").innerHTML = `
    <p class="eyebrow">Selected bet</p>
    <h3>${opportunity.name}</h3>
    <p>${opportunity.problem}</p>
    <dl class="brief-grid">
      <div><dt>Priority</dt><dd>${opportunity.priority_score}</dd></div>
      <div><dt>Stage</dt><dd>${opportunity.stage}</dd></div>
      <div><dt>Metric</dt><dd>${opportunity.primary_metric}</dd></div>
      <div><dt>Evidence</dt><dd>${opportunity.feedback_count} records</dd></div>
    </dl>
    <div class="hypothesis">
      <span>Hypothesis</span>
      <p>${opportunity.hypothesis}</p>
    </div>
  `;
}

function renderList(selector, items) {
  qs(selector).innerHTML = items.map((item) => `<li>${item}</li>`).join("");
}

function renderLaunchPlan(items) {
  qs("#launchList").innerHTML = items
    .map(
      (item) => `
        <article class="launch-item">
          <span>${item.phase}</span>
          <strong>${item.owner}</strong>
          <p>${item.gate}</p>
          <em>${item.metric}</em>
        </article>
      `
    )
    .join("");
}

function renderPrd() {
  const prd = state.payload.prd;
  renderSelectedBrief(selectedOpportunity());
  renderList("#requirementsList", prd.requirements);
  renderList("#riskList", prd.risks);
  renderList("#nonGoalList", prd.non_goals);
  renderLaunchPlan(prd.launch_plan);
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  state.selectedOpportunityId = state.payload.summary.top_opportunity.id;

  renderMetrics(state.payload.summary.metrics);
  renderBars("#themeBars", state.payload.evidence.theme_counts);
  renderBars("#personaBars", state.payload.evidence.persona_counts);
  renderFeedback(state.payload.evidence.recent_feedback);
  renderPriorityQueue(state.payload.roadmap);
  renderPrd();

  qsa(".tab-button").forEach((button) => {
    button.addEventListener("click", () => setView(button.dataset.view));
  });
}

init().catch((error) => {
  qs(".app-shell").innerHTML = `<section class="panel"><h1>Unable to load artifact data</h1><p>${error.message}</p></section>`;
});
