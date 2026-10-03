/**
 * Communication Gap Detector - Frontend Application Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM References
  const form = document.getElementById('analyze-form');
  const input = document.getElementById('conversation-input');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnSpinner = document.getElementById('btn-spinner');
  const btnText = document.getElementById('btn-text');
  const clearBtn = document.getElementById('clear-btn');
  const charCounter = document.getElementById('char-counter');
  const presetsContainer = document.getElementById('presets-container');

  // States
  const emptyState = document.getElementById('empty-state');
  const loadingState = document.getElementById('loading-state');
  const resultsContent = document.getElementById('results-content');
  const resultActions = document.getElementById('result-actions');

  // Metrics
  const healthScoreVal = document.getElementById('health-score-val');
  const healthStatusBadge = document.getElementById('health-status-badge');
  const totalGapsVal = document.getElementById('total-gaps-val');
  const gapsSubtext = document.getElementById('gaps-subtext');
  const totalMsgsVal = document.getElementById('total-msgs-val');
  const participantsCount = document.getElementById('participants-count');
  const participantsTags = document.getElementById('participants-tags');

  // Gap & Transcript Lists
  const gapsList = document.getElementById('gaps-list');
  const transcriptFeed = document.getElementById('transcript-feed');
  const filterChips = document.getElementById('filter-chips');
  const exportJsonBtn = document.getElementById('export-json-btn');

  // Modal
  const docBtn = document.getElementById('doc-btn');
  const docsModal = document.getElementById('docs-modal');
  const closeModalBtn = document.getElementById('close-modal-btn');

  let currentAnalysis = null;
  let activeFilter = 'all';

  // Read embedded samples
  let sampleData = [];
  try {
    const rawSamples = document.getElementById('embedded-samples');
    if (rawSamples && rawSamples.textContent) {
      sampleData = JSON.parse(rawSamples.textContent);
    }
  } catch (err) {
    console.error('Failed to parse embedded samples', err);
  }

  // Update line counter
  function updateLineCounter() {
    const text = input.value.trim();
    if (!text) {
      charCounter.textContent = '0 lines';
      return;
    }
    const lines = text.split('\n').filter(l => l.trim().length > 0);
    charCounter.textContent = `${lines.length} line${lines.length === 1 ? '' : 's'}`;
  }

  input.addEventListener('input', updateLineCounter);

  // Clear button
  clearBtn.addEventListener('click', () => {
    input.value = '';
    updateLineCounter();
    input.focus();
    document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
  });

  // Preset buttons
  presetsContainer.addEventListener('click', (e) => {
    const chip = e.target.closest('.preset-chip');
    if (!chip) return;

    document.querySelectorAll('.preset-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');

    const sampleId = chip.dataset.sampleId;
    const sample = sampleData.find(s => s.id === sampleId);
    if (sample) {
      input.value = sample.conversation;
      updateLineCounter();
      // Auto analyze when selecting a scenario
      runAnalysis();
    }
  });

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter
  input.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runAnalysis();
    }
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    runAnalysis();
  });

  // Modal actions
  if (docBtn && docsModal) {
    docBtn.addEventListener('click', () => docsModal.showModal());
    closeModalBtn.addEventListener('click', () => docsModal.close());
    docsModal.addEventListener('click', (e) => {
      if (e.target === docsModal) docsModal.close();
    });
  }

  // Perform Analysis
  async function runAnalysis() {
    const conversation = input.value.trim();
    if (!conversation) {
      alert('Please enter or select a conversation transcript first.');
      input.focus();
      return;
    }

    // Set Loading UI
    emptyState.classList.add('hidden');
    resultsContent.classList.add('hidden');
    resultActions.style.display = 'none';
    loadingState.classList.remove('hidden');

    analyzeBtn.disabled = true;
    btnSpinner.classList.remove('hidden');
    btnText.textContent = 'Analyzing...';

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ conversation })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Server returned an error.');
      }

      currentAnalysis = data;
      renderResults(data);
    } catch (err) {
      alert(`Analysis failed: ${err.message}`);
      emptyState.classList.remove('hidden');
    } finally {
      loadingState.classList.add('hidden');
      analyzeBtn.disabled = false;
      btnSpinner.classList.add('hidden');
      btnText.textContent = 'Detect Communication Gaps';
    }
  }

  // Render Analysis Results
  function renderResults(data) {
    const { gaps, summary, messages } = data;

    // Show Results Panel
    emptyState.classList.add('hidden');
    loadingState.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    resultActions.style.display = 'block';

    // Metrics
    healthScoreVal.textContent = summary.health_score;
    totalGapsVal.textContent = summary.total_gaps;
    gapsSubtext.textContent = summary.total_gaps === 1 ? '1 friction point' : `${summary.total_gaps} friction points`;
    totalMsgsVal.textContent = summary.total_messages;
    participantsCount.textContent = `${summary.total_participants} participant${summary.total_participants === 1 ? '' : 's'}`;

    // Health Badge
    healthStatusBadge.className = 'health-status-pill';
    if (summary.health_score >= 80) {
      healthStatusBadge.textContent = 'Healthy';
      healthStatusBadge.classList.add('status-healthy');
    } else if (summary.health_score >= 50) {
      healthStatusBadge.textContent = 'Moderate Friction';
      healthStatusBadge.classList.add('status-warning');
    } else {
      healthStatusBadge.textContent = 'High Friction';
      healthStatusBadge.classList.add('status-danger');
    }

    // Participants Tags
    participantsTags.innerHTML = '';
    if (summary.participants && summary.participants.length > 0) {
      summary.participants.forEach(p => {
        const tag = document.createElement('span');
        tag.className = 'participant-tag';
        tag.textContent = p;
        participantsTags.appendChild(tag);
      });
    } else {
      participantsTags.innerHTML = '<span class="text-muted">None detected</span>';
    }

    // Reset filter
    activeFilter = 'all';
    document.querySelectorAll('.filter-chip').forEach(c => {
      c.classList.toggle('active', c.dataset.filter === 'all');
    });

    renderGapCards(gaps);
    renderTranscript(messages);
  }

  // Render Gap Cards
  function renderGapCards(gaps) {
    gapsList.innerHTML = '';

    const filtered = activeFilter === 'all'
      ? gaps
      : gaps.filter(g => g.type.toLowerCase().includes(activeFilter.toLowerCase()) || g.type === activeFilter);

    if (filtered.length === 0) {
      if (gaps.length === 0) {
        gapsList.innerHTML = `
          <div class="healthy-banner">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <h4 class="healthy-title">No Communication Gaps Detected!</h4>
            <p class="healthy-desc">The conversation displayed smooth turn-taking, responsive question answering, and aligned resolution.</p>
          </div>
        `;
      } else {
        gapsList.innerHTML = `
          <div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
            No gaps matching the "${activeFilter}" filter.
          </div>
        `;
      }
      return;
    }

    filtered.forEach(gap => {
      const card = document.createElement('div');
      const typeSlug = gap.type.toLowerCase().replace(/\s+/g, '-');
      card.className = `gap-card type-${typeSlug}`;
      card.dataset.messageId = gap.message_id || '';

      const badgeClass = getBadgeClass(gap.type);
      const speakerInitial = (gap.speaker || 'U').charAt(0).toUpperCase();

      card.innerHTML = `
        <div class="gap-card-header">
          <span class="gap-badge ${badgeClass}">${escapeHtml(gap.type)}</span>
          <div class="gap-speaker">
            <span class="speaker-avatar">${speakerInitial}</span>
            <span>${escapeHtml(gap.speaker)}</span>
          </div>
        </div>
        <div class="gap-message-quote">
          "${escapeHtml(gap.message)}"
        </div>
        <div class="gap-evidence">
          <svg class="evidence-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          <span><strong>Evidence:</strong> ${escapeHtml(gap.evidence)}</span>
        </div>
      `;

      // Jump to message in transcript on card click
      card.addEventListener('click', () => {
        if (gap.message_id) {
          highlightTranscriptMessage(gap.message_id);
        }
      });

      gapsList.appendChild(card);
    });
  }

  // Render Transcript Messages
  function renderTranscript(messages) {
    transcriptFeed.innerHTML = '';

    if (!messages || messages.length === 0) {
      transcriptFeed.innerHTML = '<span class="text-muted">No messages parsed.</span>';
      return;
    }

    messages.forEach(msg => {
      const item = document.createElement('div');
      item.className = `transcript-msg ${msg.has_gap ? 'has-gap' : ''}`;
      item.id = `transcript-msg-${msg.id}`;

      let badgesHtml = '';
      if (msg.gap_types && msg.gap_types.length > 0) {
        badgesHtml = msg.gap_types.map(gt => {
          const badgeClass = getBadgeClass(gt);
          return `<span class="mini-badge ${badgeClass}">${escapeHtml(gt)}</span>`;
        }).join('');
      }

      item.innerHTML = `
        <div class="msg-header">
          <span class="msg-speaker">#${msg.id} &bull; ${escapeHtml(msg.speaker)}</span>
          <div class="msg-badges">${badgesHtml}</div>
        </div>
        <div class="msg-body">${escapeHtml(msg.message)}</div>
      `;

      transcriptFeed.appendChild(item);
    });
  }

  // Highlight message in transcript feed
  function highlightTranscriptMessage(msgId) {
    const el = document.getElementById(`transcript-msg-${msgId}`);
    if (el) {
      document.querySelectorAll('.transcript-msg').forEach(m => m.classList.remove('highlighted'));
      el.classList.add('highlighted');
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  // Filter chips handler
  filterChips.addEventListener('click', (e) => {
    const chip = e.target.closest('.filter-chip');
    if (!chip) return;

    document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');

    activeFilter = chip.dataset.filter;
    if (currentAnalysis) {
      renderGapCards(currentAnalysis.gaps);
    }
  });

  // Copy JSON Export
  exportJsonBtn.addEventListener('click', () => {
    if (!currentAnalysis) return;
    const jsonStr = JSON.stringify({
      gaps: currentAnalysis.gaps.map(g => ({
        type: g.type,
        speaker: g.speaker,
        message: g.message,
        evidence: g.evidence
      }))
    }, null, 2);

    navigator.clipboard.writeText(jsonStr).then(() => {
      const origText = exportJsonBtn.innerHTML;
      exportJsonBtn.innerHTML = '<span>&check; Copied!</span>';
      setTimeout(() => {
        exportJsonBtn.innerHTML = origText;
      }, 2000);
    }).catch(err => {
      alert('Could not copy to clipboard: ' + err);
    });
  });

  // Helpers
  function getBadgeClass(gapType) {
    const lower = (gapType || '').toLowerCase();
    if (lower.includes('question')) return 'badge-question';
    if (lower.includes('request')) return 'badge-request';
    if (lower.includes('clarification')) return 'badge-clarification';
    if (lower.includes('topic')) return 'badge-topic';
    return 'badge-question';
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initialize line counter on page load
  updateLineCounter();
});
