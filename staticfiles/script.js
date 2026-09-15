(function(){
  const API_URL = '/api/entries/';
  let entries = [];
  let activeType = 'all';
  let activeStatus = 'all';
  let searchTerm = '';
  let editingId = null;

  const listEl = document.getElementById('entryList');
  const statsEl = document.getElementById('statsStrip');
  const modalOverlay = document.getElementById('modalOverlay');
  const topnav = document.querySelector('.topnav');
  const form = document.getElementById('entryForm');
  const typePicker = document.getElementById('typePicker');
  const episodeRow = document.getElementById('episodeRow');
  let selectedType = 'movie';

  function getCsrfToken(){
    const cookie = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  function buildHeaders(includeBody = false){
    const headers = {Accept: 'application/json'};
    if(includeBody){ headers['Content-Type'] = 'application/json'; }
    const token = getCsrfToken();
    if(token){ headers['X-CSRFToken'] = token; }
    return headers;
  }

  async function loadEntries(){
    try{
      const res = await fetch(API_URL, {
        headers: buildHeaders(),
        credentials: 'same-origin',
        cache: 'no-store',
      });
      const data = await res.json();
      entries = Array.isArray(data) ? data : [];
    }catch(err){
      entries = [];
      console.error('Load failed', err);
    }
    render();
  }

  async function saveEntry(payload){
    const url = editingId ? `${API_URL}${editingId}/` : API_URL;
    const method = editingId ? 'PUT' : 'POST';
    try{
      const res = await fetch(url, {
        method,
        headers: buildHeaders(true),
        credentials: 'same-origin',
        cache: 'no-store',
        body: JSON.stringify(payload),
      });
      if(!res.ok){
        let message = 'Could not save entry';
        try{
          const data = await res.json();
          if(data && data.error){ message = data.error; }
        }catch(_){
          const text = await res.text();
          if(text){ message = text; }
        }
        throw new Error(message);
      }
      await loadEntries();
      closeModal();
    }catch(err){
      console.error('Save failed', err);
      alert(`The title could not be saved. ${err.message}`);
    }
  }

  async function deleteEntry(id){
    try{
      const res = await fetch(`${API_URL}${id}/`, {
        method: 'DELETE',
        headers: buildHeaders(),
        credentials: 'same-origin',
        cache: 'no-store',
      });
      if(!res.ok){
        throw new Error('Delete failed');
      }
      await loadEntries();
    }catch(err){
      console.error('Delete failed', err);
      alert('The title could not be removed.');
    }
  }

  function typeLabel(t){
    return t === 'movie' ? 'MOV' : t === 'tv' ? 'TV' : 'ANI';
  }

  function statusLabel(s){
    return {watching:'Watching', completed:'Completed', planned:'Plan to watch', dropped:'Dropped'}[s] || s;
  }

  function ticketNumber(id){
    const digits = String(id).replace(/\D/g, '') || String(id);
    return 'NO ' + digits.slice(-5).padStart(5, '0');
  }

  function computeStats(){
    const total = entries.length;
    const completed = entries.filter(e => e.status === 'completed').length;
    const watching = entries.filter(e => e.status === 'watching').length;
    const rated = entries.filter(e => e.rating !== null && e.rating !== undefined && e.rating !== '');
    const avg = rated.length ? (rated.reduce((s,e)=>s+parseFloat(e.rating),0) / rated.length).toFixed(1) : '—';
    return {total, completed, watching, avg};
  }

  function setActiveTypeButtons(type){
    document.querySelectorAll('.nav-filter-btn').forEach(b => {
      if(b.dataset.type){
        b.classList.toggle('active', b.dataset.type === type);
      }
    });
  }

  function setActiveStatusButtons(status){
    document.querySelectorAll('.nav-status-btn').forEach(b => {
      b.classList.toggle('active', b.dataset.status === status);
    });
    const statusSelect = document.getElementById('statusFilter');
    if(statusSelect){
      statusSelect.value = status;
    }
  }

  function renderStats(){
    const s = computeStats();
    statsEl.innerHTML = `
      <div class="stat-chip"><div class="num">${s.total}</div><div class="lbl">Logged</div></div>
      <div class="stat-chip"><div class="num">${s.completed}</div><div class="lbl">Completed</div></div>
      <div class="stat-chip"><div class="num">${s.watching}</div><div class="lbl">Watching</div></div>
      <div class="stat-chip"><div class="num">${s.avg}</div><div class="lbl">Avg rating</div></div>
    `;
  }

  function filteredEntries(){
    return entries
      .filter(e => activeType === 'all' || e.type === activeType)
      .filter(e => activeStatus === 'all' || e.status === activeStatus)
      .filter(e => !searchTerm || e.title.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a,b) => (b.dateWatched || '').localeCompare(a.dateWatched || '') || b.createdAt - a.createdAt);
  }

  function render(){
    renderStats();
    setActiveTypeButtons(activeType);
    setActiveStatusButtons(activeStatus);
    const list = filteredEntries();
    if(list.length === 0){
      listEl.innerHTML = `<div class="empty-state"><strong>Nothing here yet</strong>Tap + to log the first title.</div>`;
      return;
    }
    listEl.innerHTML = list.map(e => {
      const ratingDisplay = (e.rating !== null && e.rating !== undefined && e.rating !== '') ? e.rating : '—';
      const epInfo = (e.type !== 'movie' && (e.epCurrent || e.epTotal)) ? `<span>Ep ${e.epCurrent || 0}${e.epTotal ? '/' + e.epTotal : ''}</span>` : '';
      const yearInfo = e.year ? `<span>${escapeHtml(e.year)}</span>` : '';
      const dateInfo = e.dateWatched ? `<span>${formatDate(e.dateWatched)}</span>` : '';
      const notes = e.notes ? `<div class="card-notes">${escapeHtml(e.notes)}</div>` : '';
      return `
        <div class="card type-${e.type}" data-id="${e.id}">
          <div class="stub">
            <div class="ticket-no">${ticketNumber(e.id)}</div>
            <div class="kind">${typeLabel(e.type)}</div>
            <div class="rating">${ratingDisplay}</div>
            <div class="barcode" aria-hidden="true"></div>
          </div>
          <div class="card-body">
            <div class="card-top">
              <div class="card-title">${escapeHtml(e.title)}</div>
              <div class="status-badge status-${e.status}">${statusLabel(e.status)}</div>
            </div>
            <div class="card-meta">${yearInfo}${epInfo}${dateInfo}</div>
            ${notes}
            <div class="card-actions">
              <button type="button" class="edit-btn">Edit</button>
              <button type="button" class="danger delete-btn">Delete</button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  function escapeHtml(str){
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  function formatDate(iso){
    const d = new Date(iso + 'T00:00:00');
    if(isNaN(d)) return iso;
    return d.toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'});
  }

  const typeTabs = document.getElementById('typeTabs');
  if(typeTabs){
    typeTabs.addEventListener('click', e => {
      const btn = e.target.closest('.tab');
      if(!btn) return;
      activeType = btn.dataset.type;
      setActiveTypeButtons(activeType);
      render();
    });
  }

  if(topnav){
    topnav.addEventListener('click', e => {
      const typeBtn = e.target.closest('.nav-filter-btn');
      if(typeBtn){
        activeType = typeBtn.dataset.type;
        setActiveTypeButtons(activeType);
        render();
        return;
      }
      const statusBtn = e.target.closest('.nav-status-btn');
      if(statusBtn){
        activeStatus = statusBtn.dataset.status;
        setActiveStatusButtons(activeStatus);
        render();
      }
    });

    /* scroll effect: add subtle shadow when page scrolls */
    let scrollT = null;
    window.addEventListener('scroll', () => {
      if(scrollT) return;
      scrollT = setTimeout(() => {
        topnav.classList.toggle('scrolled', window.scrollY > 20);
        scrollT = null;
      }, 8);
    });
    topnav.classList.toggle('scrolled', window.scrollY > 20);
  }

  document.getElementById('statusFilter').addEventListener('change', e => {
    activeStatus = e.target.value;
    setActiveStatusButtons(activeStatus);
    render();
  });

  document.getElementById('searchInput').addEventListener('input', e => {
    searchTerm = e.target.value;
    render();
  });

  function openModal(entry){
    editingId = entry ? entry.id : null;
    document.getElementById('modalTitle').textContent = entry ? 'Edit title' : 'Add a title';
    selectedType = entry ? entry.type : 'movie';
    updateTypePicker();
    document.getElementById('fTitle').value = entry ? entry.title : '';
    document.getElementById('fYear').value = entry ? (entry.year || '') : '';
    document.getElementById('fStatus').value = entry ? entry.status : 'completed';
    document.getElementById('fEpCurrent').value = entry ? (entry.epCurrent || '') : '';
    document.getElementById('fEpTotal').value = entry ? (entry.epTotal || '') : '';
    document.getElementById('fRating').value = entry ? (entry.rating ?? '') : '';
    document.getElementById('fDate').value = entry ? (entry.dateWatched || '') : new Date().toISOString().slice(0,10);
    document.getElementById('fNotes').value = entry ? (entry.notes || '') : '';
    toggleEpisodeRow();
    modalOverlay.classList.add('open');
  }

  function closeModal(){
    modalOverlay.classList.remove('open');
    form.reset();
    editingId = null;
  }

  function updateTypePicker(){
    document.querySelectorAll('#typePicker button').forEach(b => {
      b.classList.toggle('sel', b.dataset.v === selectedType);
    });
    toggleEpisodeRow();
  }

  function toggleEpisodeRow(){
    episodeRow.style.display = (selectedType === 'movie') ? 'none' : 'flex';
  }

  typePicker.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if(!btn) return;
    selectedType = btn.dataset.v;
    updateTypePicker();
  });

  document.getElementById('addBtn').addEventListener('click', () => openModal(null));
  document.getElementById('cancelBtn').addEventListener('click', closeModal);
  modalOverlay.addEventListener('click', e => { if(e.target === modalOverlay) closeModal(); });

  listEl.addEventListener('click', e => {
    const card = e.target.closest('.card');
    if(!card) return;
    const id = card.dataset.id;
    const entry = entries.find(x => String(x.id) === String(id));
    if(!entry) return;

    if(e.target.closest('.edit-btn')){
      openModal(entry);
    } else if(e.target.closest('.delete-btn')){
      if(confirm(`Remove "${entry.title}" from your log?`)){
        deleteEntry(id);
      }
    }
  });

  form.addEventListener('submit', e => {
    e.preventDefault();
    const title = document.getElementById('fTitle').value.trim();
    if(!title) return;
    const ratingVal = document.getElementById('fRating').value;
    const data = {
      type: selectedType,
      title,
      year: document.getElementById('fYear').value.trim(),
      status: document.getElementById('fStatus').value,
      epCurrent: document.getElementById('fEpCurrent').value ? parseInt(document.getElementById('fEpCurrent').value) : null,
      epTotal: document.getElementById('fEpTotal').value ? parseInt(document.getElementById('fEpTotal').value) : null,
      rating: ratingVal !== '' ? parseFloat(ratingVal) : null,
      dateWatched: document.getElementById('fDate').value,
      notes: document.getElementById('fNotes').value.trim(),
    };
    saveEntry(data);
  });

  loadEntries();
  
  /* =====================================================================
     CHAT — AI Recommendations
     ===================================================================== */
  const chatOverlay = document.getElementById('chatOverlay');
  const chatBtn = document.getElementById('chatBtn');
  const chatCloseBtn = document.getElementById('chatCloseBtn');
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  const chatMessages = document.getElementById('chatMessages');
  const chatSuggestions = document.getElementById('chatSuggestions');
  
  let chatHistory = [];
  
  const SUGGESTIONS = [
    "Something like Interstellar",
    "Best sci-fi movies of the 2010s",
    "Hidden gem thriller series",
    "Feel-good anime recommendations",
    "Movies similar to Parasite",
    "Top rated TV dramas",
    "90s action movies",
    "Mind-bending mystery shows"
  ];
  
  function initChat(){
    renderSuggestions();
    
    chatBtn.addEventListener('click', openChat);
    chatCloseBtn.addEventListener('click', closeChat);
    chatOverlay.addEventListener('click', e => { if(e.target === chatOverlay) closeChat(); });
    chatForm.addEventListener('submit', handleChatSubmit);
    chatInput.addEventListener('keydown', e => {
      if(e.key === 'Enter' && !e.shiftKey){
        e.preventDefault();
        handleChatSubmit(e);
      }
    });
    
    // Add welcome message
    addMessage('assistant', 'Hey! I\'m your watch-log AI. Ask me for movie or TV recommendations based on your taste. Try: "Something like Interstellar" or "Best hidden gem thrillers"');
  }
  
  function openChat(){
    chatOverlay.classList.add('open');
    chatInput.focus();
    chatInput.value = '';
  }
  
  function closeChat(){
    chatOverlay.classList.remove('open');
  }
  
  function renderSuggestions(){
    chatSuggestions.innerHTML = SUGGESTIONS.map(s => 
      `<button type="button" class="suggestion-chip" data-suggestion="${escapeHtml(s)}">${escapeHtml(s)}</button>`
    ).join('');
    
    chatSuggestions.querySelectorAll('.suggestion-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        chatInput.value = btn.dataset.suggestion;
        chatInput.focus();
      });
    });
  }
  
  async function handleChatSubmit(e){
    e.preventDefault();
    const message = chatInput.value.trim();
    if(!message) return;
    
    // Add user message
    addMessage('user', message);
    chatHistory.push({ role: 'user', content: message });
    
    // Clear input and show loading
    chatInput.value = '';
    chatInput.disabled = true;
    chatSendBtn.disabled = true;
    const loadingId = addLoadingMessage();
    
    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: buildHeaders(true),
        credentials: 'same-origin',
        body: JSON.stringify({ message }),
      });
      
      // Remove loading message
      removeLoadingMessage(loadingId);
      
      if(!res.ok){
        throw new Error('Failed to get recommendations');
      }
      
      const data = await res.json();
      
      // Add assistant response
      addAssistantResponse(data);
      
    } catch (err) {
      console.error('Chat error:', err);
      removeLoadingMessage(loadingId);
      addMessage('assistant', 'Sorry, I couldn\'t get recommendations right now. Please try again later.');
    } finally {
      chatInput.disabled = false;
      chatSendBtn.disabled = false;
      chatInput.focus();
    }
  }
  
  function addMessage(role, content){
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    div.innerHTML = `<div class="chat-bubble">${escapeHtml(content)}</div>`;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div;
  }
  
  function addLoadingMessage(){
    const div = document.createElement('div');
    div.className = 'chat-message assistant loading';
    div.id = 'chat-loading-' + Date.now();
    div.innerHTML = `
      <div class="chat-bubble">
        <span class="typing-indicator"><span></span><span></span><span></span></span>
        <span>Thinking…</span>
      </div>
    `;
    chatMessages.appendChild(div);
    scrollToBottom();
    return div.id;
  }
  
  function removeLoadingMessage(id){
    const el = document.getElementById(id);
    if(el) el.remove();
  }
  
  function addAssistantResponse(data){
    const { recommendations, message, error, fallback } = data;
    
    // Add the conversational message
    const msgDiv = addMessage('assistant', message || 'Here are some recommendations for you!');
    
    // Add recommendation cards if any
    if(recommendations && recommendations.length > 0){
      const recDiv = document.createElement('div');
      recDiv.className = 'chat-message assistant';
      recDiv.innerHTML = `
        <div class="chat-bubble">
          <div class="rec-grid">
            ${recommendations.map(r => renderRecCard(r)).join('')}
          </div>
        </div>
      `;
      chatMessages.appendChild(recDiv);
      
      // Add click handlers for rec cards
      recDiv.querySelectorAll('.rec-card').forEach(card => {
        card.addEventListener('click', () => {
          const title = card.dataset.title;
          const year = card.dataset.year;
          const type = card.dataset.type;
          if(title){
            prefillAddForm(title, year, type);
            closeChat();
            openModal(null);
          }
        });
      });
    }
    
    scrollToBottom();
  }
  
  function renderRecCard(r){
    const poster = r.poster 
      ? `<img src="${escapeHtml(r.poster)}" alt="${escapeHtml(r.title)}" loading="lazy">`
      : `<div class="rec-placeholder">${r.type === 'movie' ? 'MOV' : r.type === 'tv' ? 'TV' : 'ANI'}</div>`;
    
    return `
      <div class="rec-card" 
           data-title="${escapeHtml(r.title)}" 
           data-year="${escapeHtml(r.year || '')}" 
           data-type="${escapeHtml(r.type)}"
           tabindex="0"
           role="button"
           aria-label="${escapeHtml(r.title)} (${r.year || 'N/A'})">
        <div class="rec-poster">${poster}</div>
        <div class="rec-info">
          <div class="rec-title">${escapeHtml(r.title)}</div>
          <div class="rec-meta">
            <span class="rec-type ${escapeHtml(r.type)}">${r.type === 'movie' ? 'MOV' : r.type === 'tv' ? 'TV' : 'ANI'}</span>
            ${r.year ? `<span class="rec-year">${escapeHtml(r.year)}</span>` : ''}
            ${r.rating ? `<span class="rec-rating">★ ${r.rating.toFixed(1)}</span>` : ''}
          </div>
          ${r.reason ? `<div class="rec-reason">${escapeHtml(r.reason)}</div>` : ''}
        </div>
      </div>
    `;
  }
  
  function prefillAddForm(title, year, type){
    selectedType = type || 'movie';
    updateTypePicker();
    document.getElementById('fTitle').value = title || '';
    document.getElementById('fYear').value = year || '';
    document.getElementById('fStatus').value = 'planned';
    document.getElementById('fRating').value = '';
    document.getElementById('fDate').value = '';
    document.getElementById('fNotes').value = '';
    document.getElementById('fEpCurrent').value = '';
    document.getElementById('fEpTotal').value = '';
    toggleEpisodeRow();
  }
  
  function scrollToBottom(){
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Initialize chat after DOM is ready
  initChat();
})();