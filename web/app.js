const form = document.querySelector("#search-form");
const input = document.querySelector("#search-input");
const results = document.querySelector("#results");
const status = document.querySelector("#status");
const title = document.querySelector("#results-title");
const documentCount = document.querySelector("#document-count");

async function refreshHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) return;
    const data = await response.json();
    documentCount.textContent = data.documents.toLocaleString();
  } catch (_) {
    return;
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderResults(query, items) {
  title.textContent = `Results for “${query}”`;
  status.textContent = `${items.length} results`;

  if (!items.length) {
    results.innerHTML = `
      <div class="empty-state">
        <h3>No results found.</h3>
        <p>Try a broader policy concept or different wording.</p>
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
        <a href="${escapeHtml(item.source_url)}" target="_blank" rel="noopener">
          ${escapeHtml(item.title)}
        </a>
      </h3>
      <span class="topic">${escapeHtml(item.topic)}</span>
    </article>
  `).join("");
}

async function runSearch(query) {
  status.textContent = "Searching…";
  results.innerHTML = `
    <div class="empty-state">
      <h3>Running semantic search…</h3>
      <p>The first query may take longer while the local embedding model loads.</p>
    </div>
  `;

  try {
    const response = await fetch(`/search?q=${encodeURIComponent(query)}&k=10`);
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

refreshHealth();
