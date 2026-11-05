const form = document.querySelector("#search-form");
const input = document.querySelector("#search-input");
const results = document.querySelector("#results");
const status = document.querySelector("#status");
const title = document.querySelector("#results-title");
const documentCount = document.querySelector("#document-count");
const topicCount = document.querySelector("#topic-count");
const precisionScore = document.querySelector("#precision-score");
const corpusRange = document.querySelector("#corpus-range");
const agencyFilter = document.querySelector("#agency-filter");
const yearFilter = document.querySelector("#year-filter");
const typeFilter = document.querySelector("#type-filter");
const topicFilter = document.querySelector("#topic-filter");
const clearFilters = document.querySelector("#clear-filters");

async function refreshAbout() {
  try {
    const response = await fetch("/about");
    if (!response.ok) return;
    const data = await response.json();
    documentCount.textContent = Number(data.documents).toLocaleString();
    topicCount.textContent = Number(data.topics).toLocaleString();
    precisionScore.textContent = Number(data.semantic_precision_at_5).toFixed(3);
    corpusRange.textContent = `Federal Register · ${data.start_year}–${data.end_year}`;
  } catch (_) {
    return;
  }
}

function addOptions(select, values, labelKey = null, valueKey = null) {
  values.forEach((item) => {
    const option = document.createElement("option");
    if (labelKey) {
      option.textContent = item[labelKey];
      option.value = item[valueKey];
    } else {
      option.textContent = item.toUpperCase ? item.toUpperCase() : item;
      option.value = item;
    }
    select.appendChild(option);
  });
}

async function loadFilters() {
  try {
    const response = await fetch("/filters");
    if (!response.ok) return;
    const data = await response.json();
    addOptions(agencyFilter, data.agencies);
    addOptions(yearFilter, data.years);
    addOptions(typeFilter, data.document_types);
    addOptions(topicFilter, data.topics, "label", "cluster");
  } catch (_) {
    return;
  }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function activeFilterSummary() {
  const parts = [];
  if (agencyFilter.value) parts.push(agencyFilter.options[agencyFilter.selectedIndex].text);
  if (yearFilter.value) parts.push(yearFilter.value);
  if (typeFilter.value) parts.push(typeFilter.value);
  if (topicFilter.value) parts.push(topicFilter.options[topicFilter.selectedIndex].text);
  return parts;
}

function renderResults(query, items) {
  const filters = activeFilterSummary();
  title.textContent = `Results for “${query}”`;
  status.textContent = filters.length
    ? `${items.length} results · ${filters.join(" · ")}`
    : `${items.length} results`;

  if (!items.length) {
    results.innerHTML = `
      <div class="empty-state">
        <h3>No results found.</h3>
        <p>Try removing a filter or using broader policy language.</p>
      </div>
    `;
    return;
  }

  results.innerHTML = items.map((item) => `
    <article class="result-card">
      <div class="result-meta">
        <span>${escapeHtml(item.publication_date)}</span>
        <span>${escapeHtml(item.document_type)}</span>
        <span>${escapeHtml(item.agency_scopes)}</span>
        <span class="score">Similarity ${Number(item.score).toFixed(3)}</span>
      </div>
      <h3>
        <a href="${escapeHtml(item.detail_url)}">
          ${escapeHtml(item.title)}
        </a>
      </h3>
      ${item.snippet ? `<p class="snippet">${escapeHtml(item.snippet)}</p>` : ""}
      <div class="result-footer">
        <span class="topic">${escapeHtml(item.topic)}</span>
        <a class="source-link" href="${escapeHtml(item.source_url)}" target="_blank" rel="noopener">
          Federal Register ↗
        </a>
      </div>
    </article>
  `).join("");
}

async function runSearch(query) {
  status.textContent = "Searching…";
  results.innerHTML = `
    <div class="empty-state">
      <h3>Running semantic search…</h3>
      <p>Ranking the filtered policy corpus by semantic similarity.</p>
    </div>
  `;

  const params = new URLSearchParams({ q: query, k: "10" });
  if (agencyFilter.value) params.set("agency", agencyFilter.value);
  if (yearFilter.value) params.set("year", yearFilter.value);
  if (typeFilter.value) params.set("document_type", typeFilter.value);
  if (topicFilter.value) params.set("topic", topicFilter.value);

  try {
    const response = await fetch(`/search?${params.toString()}`);
    if (!response.ok) {
      throw new Error("Search request failed.");
    }

    const data = await response.json();
    renderResults(query, data.results);
  } catch (error) {
    status.textContent = "";
    results.innerHTML = `
      <div class="error">
        Search is temporarily unavailable. ${escapeHtml(error.message)}
      </div>
    `;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = input.value.trim();
  if (query.length >= 2) runSearch(query);
});

document.querySelectorAll("[data-query]").forEach((button) => {
  button.addEventListener("click", () => {
    const query = button.dataset.query;
    input.value = query;
    runSearch(query);
  });
});

clearFilters.addEventListener("click", () => {
  agencyFilter.value = "";
  yearFilter.value = "";
  typeFilter.value = "";
  topicFilter.value = "";
});

refreshAbout();
loadFilters();
