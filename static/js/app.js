/**
 * LexiClear AI - Modern Frontend Application Logic
 * Full-Stack Generative AI Legal Intelligence Engine
 */

// Application State
const state = {
  activeTab: 'summary',
  currentDocument: null,
  geminiLive: false,
  activeModel: 'gemini-3.8-flash',
  summaryData: null,
  penaltiesData: null,
  complianceData: null,
  chatHistory: [],
};

// DOM Content Loaded Entrypoint
document.addEventListener('DOMContentLoaded', () => {
  initDropZone();
  fetchSystemStatus();
  fetchSamples();
  // Automatically load summary on startup
  loadSummary();
});

// ============================================================================
// SYSTEM STATUS & SAMPLES INITIALIZATION
// ============================================================================
async function fetchSystemStatus() {
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    state.geminiLive = data.gemini_live;
    state.activeModel = data.active_model;

    updateApiStatusBadge(data.gemini_live);

    if (data.current_document) {
      updateDocumentMetrics(data.current_document);
    }
  } catch (err) {
    console.error('Error checking system status:', err);
  }
}

function updateApiStatusBadge(isLive) {
  const badge = document.getElementById('apiStatusBadge');
  const dot = document.getElementById('apiStatusDot');
  const text = document.getElementById('apiStatusText');

  if (isLive) {
    dot.className = 'status-dot online';
    text.textContent = `Gemini Live (${state.activeModel})`;
    badge.title = 'Connected to Google Gemini API (Click to reconfigure)';
  } else {
    dot.className = 'status-dot simulated';
    text.textContent = 'Simulated / Demo Mode';
    badge.title = 'Running in offline simulated mode. Click to add Gemini API key.';
  }
}

function updateDocumentMetrics(doc) {
  state.currentDocument = doc;
  document.getElementById('metricFilename').textContent = doc.filename || 'contract.pdf';
  document.getElementById('metricPages').textContent = doc.pages || doc.total_pages || 1;
  document.getElementById('metricWords').textContent = (doc.words || doc.total_words || 0).toLocaleString();
  document.getElementById('metricChunks').textContent = doc.chunks || doc.chunks_count || 0;
  document.getElementById('metricTokens').textContent = (doc.estimated_tokens || 0).toLocaleString();

  document.getElementById('docStatusText').textContent = `${doc.filename} (${doc.pages || doc.total_pages || 1} pgs)`;
}

async function fetchSamples() {
  try {
    const res = await fetch('/api/samples');
    const samples = await res.json();
    const container = document.getElementById('samplePillsContainer');
    container.innerHTML = '';

    samples.forEach(sample => {
      const btn = document.createElement('button');
      btn.className = 'sample-pill-btn';
      btn.onclick = () => loadSample(sample.id);
      btn.innerHTML = `
        <span class="sample-pill-name">${sample.title}</span>
        <span class="sample-pill-desc">${sample.category} • Click to test</span>
      `;
      container.appendChild(btn);
    });
  } catch (err) {
    console.error('Error fetching sample contracts:', err);
  }
}

async function loadSample(sampleId) {
  try {
    showNotification(`Loading ${sampleId} preset...`);
    const res = await fetch(`/api/samples/load/${sampleId}`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      updateDocumentMetrics(data.metadata);
      invalidateAnalysisCache();
      refreshActiveTab();
      showNotification(`Loaded ${data.sample.title}`);
    }
  } catch (err) {
    alert('Failed to load sample contract: ' + err.message);
  }
}

function invalidateAnalysisCache() {
  state.summaryData = null;
  state.penaltiesData = null;
  state.complianceData = null;
}

function refreshActiveTab() {
  if (state.activeTab === 'summary') loadSummary(true);
  else if (state.activeTab === 'penalties') loadPenalties(true);
  else if (state.activeTab === 'compliance') loadCompliance(true);
}

// ============================================================================
// UPLOAD & FILE DROPZONE HANDLERS
// ============================================================================
function initDropZone() {
  const dropZone = document.getElementById('dropZone');
  const fileInput = document.getElementById('pdfFileInput');

  dropZone.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
    });
  });

  dropZone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileUpload(e.target.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert('Please upload a valid PDF document.');
    return;
  }

  const formData = new FormData();
  formData.append('file', file);

  const progressBar = document.getElementById('uploadProgress');
  const fill = document.getElementById('progressBarFill');
  progressBar.classList.remove('hidden');
  fill.style.width = '40%';

  try {
    const res = await fetch('/api/upload', {
      method: 'POST',
      body: formData,
    });
    fill.style.width = '80%';

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Upload failed');
    }

    const data = await res.json();
    fill.style.width = '100%';
    setTimeout(() => progressBar.classList.add('hidden'), 500);

    updateDocumentMetrics(data.metadata);
    invalidateAnalysisCache();
    refreshActiveTab();
    showNotification(`Successfully parsed ${file.name} using PyMuPDF!`);
  } catch (err) {
    progressBar.classList.add('hidden');
    alert(`Upload error: ${err.message}`);
  }
}

function togglePasteArea() {
  const container = document.getElementById('pasteContainer');
  container.classList.toggle('hidden');
}

async function submitPastedText() {
  const text = document.getElementById('pastedText').value.trim();
  const filename = document.getElementById('pasteFilename').value.trim() || 'custom-contract.txt';

  if (text.length < 30) {
    alert('Please paste a substantial contract text snippet (at least 30 characters).');
    return;
  }

  try {
    const res = await fetch('/api/ingest-text', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, filename }),
    });

    const data = await res.json();
    if (data.success) {
      togglePasteArea();
      updateDocumentMetrics(data.metadata);
      invalidateAnalysisCache();
      refreshActiveTab();
      showNotification('Contract text ingested successfully.');
    }
  } catch (err) {
    alert('Failed to ingest text: ' + err.message);
  }
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================
function switchTab(tabId) {
  state.activeTab = tabId;

  // Toggle Tab Buttons
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabId);
  });

  // Toggle Tab Panels
  document.querySelectorAll('.tab-panel').forEach(panel => {
    panel.classList.toggle('active', panel.id === `tab-${tabId}`);
  });

  // Lazy-load data for tab if not yet loaded
  if (tabId === 'summary' && !state.summaryData) loadSummary();
  if (tabId === 'penalties' && !state.penaltiesData) loadPenalties();
  if (tabId === 'compliance' && !state.complianceData) loadCompliance();
}

// ============================================================================
// 1. PLAIN-ENGLISH SUMMARY
// ============================================================================
async function loadSummary(force = false) {
  if (state.summaryData && !force) {
    renderSummary(state.summaryData);
    return;
  }

  const loader = document.getElementById('summaryLoading');
  const content = document.getElementById('summaryContent');
  loader.classList.remove('hidden');
  content.classList.add('hidden');

  try {
    const res = await fetch('/api/analyze/summary', { method: 'POST' });
    const data = await res.json();
    state.summaryData = data;
    renderSummary(data);
  } catch (err) {
    console.error('Error loading summary:', err);
  } finally {
    loader.classList.add('hidden');
    content.classList.remove('hidden');
  }
}

function renderSummary(data) {
  document.getElementById('sumDocTitle').textContent = data.document_title || 'Legal Document Analysis';
  document.getElementById('sumDocType').textContent = data.document_type || 'Contract';
  document.getElementById('sumTldr').textContent = data.tl_dr || 'No summary available.';

  // Render Parties
  const partiesContainer = document.getElementById('sumParties');
  partiesContainer.innerHTML = '';
  if (data.parties_involved && Array.isArray(data.parties_involved)) {
    data.parties_involved.forEach(p => {
      const badge = document.createElement('div');
      badge.className = 'party-badge';
      badge.innerHTML = `<strong>${escapeHtml(p.name)}</strong><span class="party-role">(${escapeHtml(p.role)})</span>`;
      partiesContainer.appendChild(badge);
    });
  }

  // Core Rights
  const rightsList = document.getElementById('sumRightsGranted');
  rightsList.innerHTML = '';
  (data.core_rights || ['Standard operational access']).forEach(r => {
    const li = document.createElement('li');
    li.textContent = r;
    rightsList.appendChild(li);
  });

  // Rights Conceded
  const concededList = document.getElementById('sumRightsConceded');
  concededList.innerHTML = '';
  (data.rights_conceded || ['No harsh rights conceded']).forEach(c => {
    const li = document.createElement('li');
    li.textContent = c;
    concededList.appendChild(li);
  });

  // Term & Exit
  document.getElementById('sumTermExit').textContent = data.term_and_termination || 'Standard term provisions.';

  // Verdict
  document.getElementById('sumVerdict').textContent = data.plain_english_verdict || 'Review all terms carefully before execution.';
}

// ============================================================================
// 2. PENALTIES & OBLIGATIONS
// ============================================================================
async function loadPenalties(force = false) {
  if (state.penaltiesData && !force) {
    renderPenalties(state.penaltiesData);
    return;
  }

  const loader = document.getElementById('penaltiesLoading');
  const content = document.getElementById('penaltiesContent');
  loader.classList.remove('hidden');
  content.classList.add('hidden');

  try {
    const res = await fetch('/api/analyze/risks', { method: 'POST' });
    const data = await res.json();
    state.penaltiesData = data;
    renderPenalties(data);
  } catch (err) {
    console.error('Error loading penalties:', err);
  } finally {
    loader.classList.add('hidden');
    content.classList.remove('hidden');
  }
}

function renderPenalties(data) {
  // Strict Financial Penalties Table
  const tbody = document.getElementById('penaltiesTableBody');
  tbody.innerHTML = '';

  const penalties = data.strict_penalties || [];
  if (penalties.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted)">No aggressive liquidated damages detected.</td></tr>`;
  } else {
    penalties.forEach(p => {
      const tr = document.createElement('tr');
      const sevClass = (p.severity || 'medium').toLowerCase();
      tr.innerHTML = `
        <td><strong>${escapeHtml(p.clause_name)}</strong></td>
        <td style="color:var(--risk-critical); font-family:var(--font-mono); font-weight:600;">${escapeHtml(p.financial_impact)}</td>
        <td>${escapeHtml(p.trigger_condition)}</td>
        <td><span class="severity-pill ${sevClass}">${escapeHtml(p.severity || 'Medium')}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Strict Operational Deadlines
  const obContainer = document.getElementById('obligationsContainer');
  obContainer.innerHTML = '';
  (data.strict_obligations || []).forEach(o => {
    const card = document.createElement('div');
    card.className = 'obligation-card';
    card.innerHTML = `
      <div class="obligation-title">${escapeHtml(o.obligation)}</div>
      <div class="obligation-deadline">⏳ Deadline: ${escapeHtml(o.deadline_or_timeframe)}</div>
      <div class="obligation-consequence">⚠️ Consequence of miss: ${escapeHtml(o.consequence_of_miss)}</div>
    `;
    obContainer.appendChild(card);
  });

  // Unilateral Terms
  const uniContainer = document.getElementById('unilateralContainer');
  uniContainer.innerHTML = '';
  (data.unilateral_terms || []).forEach(u => {
    const item = document.createElement('div');
    item.className = 'term-item';
    item.innerHTML = `
      <div class="term-title">${escapeHtml(u.term)}</div>
      <div class="term-desc">${escapeHtml(u.explanation)}</div>
    `;
    uniContainer.appendChild(item);
  });

  // Hidden Traps
  const trapsContainer = document.getElementById('trapsContainer');
  trapsContainer.innerHTML = '';
  (data.hidden_traps || []).forEach(t => {
    const li = document.createElement('li');
    li.textContent = t;
    trapsContainer.appendChild(li);
  });
}

// ============================================================================
// 3. COMPLIANCE & RISK AUDIT
// ============================================================================
async function loadCompliance(force = false) {
  if (state.complianceData && !force) {
    renderCompliance(state.complianceData);
    return;
  }

  const loader = document.getElementById('complianceLoading');
  const content = document.getElementById('complianceContent');
  loader.classList.remove('hidden');
  content.classList.add('hidden');

  try {
    const res = await fetch('/api/analyze/compliance', { method: 'POST' });
    const data = await res.json();
    state.complianceData = data;
    renderCompliance(data);
  } catch (err) {
    console.error('Error loading compliance:', err);
  } finally {
    loader.classList.add('hidden');
    content.classList.remove('hidden');
  }
}

function renderCompliance(data) {
  const score = data.overall_risk_score || 50;
  const level = (data.risk_level || 'Medium').toLowerCase();

  // Gauge Circle Update
  const gaugeNumber = document.getElementById('riskGaugeNumber');
  const gaugeCircle = document.querySelector('.gauge-circle');
  const riskBadge = document.getElementById('riskLevelBadge');

  gaugeNumber.textContent = score;
  gaugeCircle.className = `gauge-circle ${level}`;
  riskBadge.textContent = `${level.toUpperCase()} RISK`;
  riskBadge.className = `risk-badge ${level}`;

  // Rationale & Priorities
  document.getElementById('riskRationaleText').textContent = data.executive_risk_rationale || 'Risk profile evaluated.';
  const priorityList = document.getElementById('negotiationList');
  priorityList.innerHTML = '';
  (data.negotiation_priorities || []).forEach(p => {
    const li = document.createElement('li');
    li.textContent = p;
    priorityList.appendChild(li);
  });

  // Compliance Checklist
  const checkContainer = document.getElementById('complianceChecklist');
  checkContainer.innerHTML = '';
  (data.compliance_checklist || []).forEach(c => {
    const item = document.createElement('div');
    item.className = 'check-item';
    const statusClass = (c.status || 'warning').toLowerCase();
    item.innerHTML = `
      <div class="check-item-header">
        <span class="check-name">${escapeHtml(c.item)}</span>
        <span class="check-status ${statusClass}">${escapeHtml(c.status || 'Warning')}</span>
      </div>
      <div class="check-notes">${escapeHtml(c.notes || '')}</div>
    `;
    checkContainer.appendChild(item);
  });

  // Clause Audits & Redlines
  const auditsContainer = document.getElementById('clauseAuditsList');
  auditsContainer.innerHTML = '';
  (data.clause_audits || []).forEach(a => {
    const card = document.createElement('div');
    card.className = 'clause-audit-card';
    const sevClass = (a.risk_level || 'medium').toLowerCase();

    card.innerHTML = `
      <div class="clause-card-top">
        <span class="clause-title">${escapeHtml(a.clause_title)}</span>
        <span class="severity-pill ${sevClass}">${escapeHtml(a.risk_level)} Risk</span>
      </div>
      <div class="quote-box">"${escapeHtml(a.original_intent_or_quote || '')}"</div>
      <p class="analysis-p"><strong>Risk Exposure:</strong> ${escapeHtml(a.risk_analysis)}</p>
      <div class="redline-box">
        <div class="redline-header">
          <span class="redline-label">✍️ Recommended Redline / Counter-Clause</span>
          <button class="copy-btn" onclick="copyText(this, '${escapeForAttribute(a.suggested_redline)}')">Copy Redline</button>
        </div>
        <div class="redline-text">${escapeHtml(a.suggested_redline)}</div>
      </div>
    `;
    auditsContainer.appendChild(card);
  });
}

// ============================================================================
// 4. CONTEXT-AWARE RAG Q&A CHAT
// ============================================================================
function askQuestion(q) {
  document.getElementById('chatInput').value = q;
  handleChatSubmit(new Event('submit'));
}

async function handleChatSubmit(e) {
  e.preventDefault();
  const input = document.getElementById('chatInput');
  const question = input.value.trim();
  if (!question) return;

  // Add User Message
  appendChatMessage('user', question);
  input.value = '';

  // Add Bot Loading Message
  const loadingId = appendChatMessage('bot', 'Analyzing retrieved contract chunks and citing sources...', true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k: 4 }),
    });

    const data = await res.json();
    removeChatMessage(loadingId);

    // Format Bot Response with Quotes and Citations
    let contentHtml = `<p>${escapeHtml(data.answer)}</p>`;

    // Add Direct Quotes if available
    if (data.direct_quotes && data.direct_quotes.length > 0) {
      data.direct_quotes.forEach(quote => {
        contentHtml += `<div class="quote-highlight">"${escapeHtml(quote)}"</div>`;
      });
    }

    // Add Actionable Takeaway
    if (data.actionable_takeaway) {
      contentHtml += `<p style="margin-top:8px;font-size:0.82rem;color:var(--accent-teal)"><strong>💡 Actionable Takeaway:</strong> ${escapeHtml(data.actionable_takeaway)}</p>`;
    }

    // Add Citations Panel
    if (data.citations && data.citations.length > 0) {
      contentHtml += `
        <div class="citations-panel">
          <div class="citations-title">📌 Verified Contract Sources & Page Citations:</div>
      `;
      data.citations.forEach(c => {
        contentHtml += `
          <div class="citation-pill">
            <strong>${escapeHtml(c.pages)}</strong> ${c.section ? `• [${escapeHtml(c.section)}]` : ''} 
            <span style="opacity:0.75">(Relevance: ${c.score})</span>
            <div style="font-size:0.72rem;margin-top:3px;font-style:italic;opacity:0.85;">"${escapeHtml(c.snippet)}"</div>
          </div>
        `;
      });
      contentHtml += `</div>`;
    }

    appendChatMessage('bot', contentHtml, false, true);
  } catch (err) {
    removeChatMessage(loadingId);
    appendChatMessage('bot', `⚠️ Sorry, an error occurred while searching the document: ${err.message}`);
  }
}

function appendChatMessage(sender, content, isLoading = false, isHtml = false) {
  const box = document.getElementById('chatMessagesBox');
  const msgDiv = document.createElement('div');
  const msgId = 'msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 5);
  msgDiv.id = msgId;
  msgDiv.className = `chat-message ${sender}-message`;

  const avatar = sender === 'user' ? '👤' : '⚖️';
  msgDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      ${isHtml ? content : (isLoading ? `<em>${content}</em>` : `<p>${escapeHtml(content)}</p>`)}
    </div>
  `;

  box.appendChild(msgDiv);
  box.scrollTop = box.scrollHeight;
  return msgId;
}

function removeChatMessage(msgId) {
  const msg = document.getElementById(msgId);
  if (msg) msg.remove();
}

function clearChat() {
  const box = document.getElementById('chatMessagesBox');
  box.innerHTML = `
    <div class="chat-message bot-message">
      <div class="message-avatar">⚖️</div>
      <div class="message-content">
        <p>Chat cleared. Ask me any question regarding your loaded agreement!</p>
      </div>
    </div>
  `;
}

// ============================================================================
// MODALS & HELPERS
// ============================================================================
async function openDocModal() {
  const modal = document.getElementById('docModal');
  const title = document.getElementById('docModalTitle');
  const content = document.getElementById('docViewerContent');

  modal.classList.remove('hidden');
  content.textContent = 'Loading full document text...';

  try {
    const res = await fetch('/api/document/raw');
    const data = await res.json();
    title.textContent = `Inspecting: ${data.filename}`;
    content.textContent = data.raw_text;
  } catch (err) {
    content.textContent = 'Failed to load document text.';
  }
}

function closeDocModal() {
  document.getElementById('docModal').classList.add('hidden');
}

function openKeyModal() {
  document.getElementById('keyModal').classList.remove('hidden');
  document.getElementById('apiKeyInput').value = '';
  document.getElementById('keyStatusMsg').className = 'form-feedback hidden';
}

function closeKeyModal() {
  document.getElementById('keyModal').classList.add('hidden');
}

async function saveApiKey() {
  const key = document.getElementById('apiKeyInput').value.trim();
  const feedback = document.getElementById('keyStatusMsg');

  if (!key) {
    feedback.className = 'form-feedback error';
    feedback.textContent = 'Please enter an API key.';
    feedback.classList.remove('hidden');
    return;
  }

  try {
    const res = await fetch('/api/settings/key', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: key }),
    });

    const data = await res.json();
    if (data.success) {
      feedback.className = 'form-feedback success';
      feedback.textContent = 'Gemini API key updated and validated!';
      feedback.classList.remove('hidden');
      state.geminiLive = data.gemini_live;
      updateApiStatusBadge(data.gemini_live);

      setTimeout(() => {
        closeKeyModal();
        invalidateAnalysisCache();
        refreshActiveTab();
      }, 1000);
    } else {
      feedback.className = 'form-feedback error';
      feedback.textContent = 'Failed to validate API key.';
      feedback.classList.remove('hidden');
    }
  } catch (err) {
    feedback.className = 'form-feedback error';
    feedback.textContent = err.message;
    feedback.classList.remove('hidden');
  }
}

function copyText(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const orig = btn.textContent;
    btn.textContent = '✓ Copied!';
    btn.style.borderColor = 'var(--risk-safe)';
    btn.style.color = 'var(--risk-safe)';
    setTimeout(() => {
      btn.textContent = orig;
      btn.style.borderColor = '';
      btn.style.color = '';
    }, 2000);
  });
}

function showNotification(msg) {
  const badge = document.getElementById('docStatusText');
  const orig = badge.textContent;
  badge.textContent = msg;
  setTimeout(() => {
    badge.textContent = orig;
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeForAttribute(str) {
  if (!str) return '';
  return String(str)
    .replace(/'/g, "\\'")
    .replace(/"/g, '&quot;')
    .replace(/\n/g, ' ');
}
