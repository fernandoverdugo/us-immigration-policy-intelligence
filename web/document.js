const root = document.querySelector("#document-detail");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function displayDate(value) {
  if (!value) return "—";
  const date = new Date(value + "T00:00:00");
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function listValue(values) {
  return values && values.length ? values.map(escapeHtml).join(", ") : "—";
}

function sourceLinks(item) {
  const links = [];
  if (document.html_url) {
    links.push(`<a href="${escapeHtml(document.html_url)}" target="_blank" rel="noopener">Federal Register page ↗</a>`);
  }
  if (document.pdf_url) {
    links.push(`<a href="${escapeHtml(document.pdf_url)}" target="_blank" rel="noopener">Official PDF ↗</a>`);
  }
  if (document.raw_text_url) {
    links.push(`<a href="${escapeHtml(document.raw_text_url)}" target="_blank" rel="noopener">Raw text ↗</a>`);
  }
  return links.join("");
}

function relatedMarkup(items) {
  if (!items || !items.length) {
    return "<p>No related documents are indexed.</p>";
  }

  return `
    <ul class="related-list">
      ${items.map((item) => `
        <li>
          <a href="${escapeHtml(item.detail_url)}">${escapeHtml(item.title)}</a>
          <span class="related-score">TF-IDF similarity ${Number(item.cosine_similarity).toFixed(3)}</span>
        </li>
      `).join("")}
    </ul>
  `;
}

function renderDocument(item) {
  window.item.title = `${item.title} · U.S. Immigration Policy Intelligence`;

  root.innerHTML = `
    <section class="detail-hero">
      <div class="eyebrow">${escapeHtml(item.topic)}</div>
      <h1>${escapeHtml(item.title)}</h1>
      <div class="detail-meta">
        <span>${escapeHtml(displayDate(item.publication_date))}</span>
        <span>${escapeHtml(item.document_type || "")}</span>
        <span>${escapeHtml(item.agency_scopes.join(" · ").toUpperCase())}</span>
        <span>${escapeHtml(item.document_number)}</span>
      </div>
      <span class="topic">${escapeHtml(item.topic)}</span>
    </section>

    <section class="detail-grid">
      <div>
        <article class="detail-card">
          <h2>Abstract</h2>
          <p>${escapeHtml(item.abstract || "No abstract is available in the indexed Federal Register metadata.")}</p>
        </article>

        ${item.action ? `
          <article class="detail-card" style="margin-top: 18px;">
            <h2>Agency action</h2>
            <p>${escapeHtml(item.action)}</p>
          </article>
        ` : ""}

        <article class="detail-card" style="margin-top: 18px;">
          <h2>Related documents</h2>
          ${relatedMarkup(item.related_documents)}
        </article>
      </div>

      <aside class="detail-card">
        <h3>Document metadata</h3>
        <dl class="metadata-list">
          <div class="metadata-row">
            <dt>Federal Register citation</dt>
            <dd>${escapeHtml(item.citation || "—")}</dd>
          </div>
          <div class="metadata-row">
            <dt>Effective date</dt>
            <dd>${escapeHtml(displayDate(item.effective_on))}</dd>
          </div>
          <div class="metadata-row">
            <dt>Comments close</dt>
            <dd>${escapeHtml(displayDate(item.comments_close_on))}</dd>
          </div>
          <div class="metadata-row">
            <dt>CFR references</dt>
            <dd>${listValue(item.cfr_references)}</dd>
          </div>
          <div class="metadata-row">
            <dt>RIN</dt>
            <dd>${listValue(item.regulation_identifiers)}</dd>
          </div>
        </dl>

        <div class="link-stack">
          ${sourceLinks(document)}
        </div>
      </aside>
    </section>
  `;
}

async function loadDocument() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  const documentNumber = parts.at(-1);

  try {
    const response = await fetch(`/documents/${encodeURIComponent(documentNumber)}`);
    if (!response.ok) {
      throw new Error(response.status === 404 ? "Document not found." : "Document request failed.");
    }
    renderDocument(await response.json());
  } catch (error) {
    root.innerHTML = `
      <div class="error">
        ${escapeHtml(error.message)}
      </div>
    `;
  }
}

loadDocument();
