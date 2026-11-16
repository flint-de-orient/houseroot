/* HouseRoot admin panel — talks to server.js (/api/admin/*). */
(function () {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const esc = window.HR.esc;
  const state = { content: null, view: 'projects', editing: null };

  /* ---------- api ---------- */
  async function api(method, url, body) {
    const res = await fetch(url, { method, headers: { 'Content-Type': 'application/json', 'X-Requested-With': 'HouseRootAdmin' }, body: body ? JSON.stringify(body) : undefined, credentials: 'same-origin' });
    let data = {};
    try { data = await res.json(); } catch { /* empty */ }
    if (res.status === 401 && !url.endsWith('/login')) { showLogin(); throw new Error('Signed out'); }
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
    return data;
  }
  let toastT;
  function toast(msg, err) {
    const t = $('#toast'); t.textContent = msg; t.hidden = false; t.classList.toggle('is-err', !!err);
    clearTimeout(toastT); toastT = setTimeout(() => t.hidden = true, err ? 4000 : 2200);
  }

  /* ---------- auth ---------- */
  function showLogin() {
    $('#login-form').reset(); $('#pw').value = ''; $('#login-err').hidden = true;
    $$('.pw-eye').forEach(btn => setEye(btn, false));
    $('#login').hidden = false; $('#app').hidden = true; setTimeout(() => $('#pw').focus(), 0);
  }
  function setEye(btn, show) {
    const input = btn.parentElement.querySelector('input');
    input.type = show ? 'text' : 'password';
    btn.setAttribute('aria-pressed', String(show)); btn.setAttribute('aria-label', show ? 'Hide password' : 'Show password'); btn.title = show ? 'Hide password' : 'Show password';
  }
  $$('.pw-eye').forEach(btn => btn.addEventListener('click', () => setEye(btn, btn.getAttribute('aria-pressed') !== 'true')));
  // Hard character limits: trim typed or pasted text and show a counter on password boxes
  $$('[maxlength]').forEach(el => {
    const max = Number(el.getAttribute('maxlength'));
    const counter = el.type === 'password' ? Object.assign(document.createElement('span'), { className: 'pw-count' }) : null;
    if (counter) el.closest('.field').appendChild(counter);
    const sync = () => {
      if (el.value.length > max) el.value = el.value.slice(0, max);
      if (counter) { counter.textContent = el.value.length + ' / ' + max; counter.classList.toggle('is-max', el.value.length >= max); }
    };
    el.addEventListener('input', sync); el.addEventListener('paste', () => setTimeout(sync, 0)); el.addEventListener('change', sync);
    if (el.form) el.form.addEventListener('reset', () => setTimeout(sync, 0));
    sync();
  });
  async function showApp() { $('#login').hidden = true; $('#app').hidden = false; await refresh(); go(state.view); }
  $('#login-form').addEventListener('submit', async e => {
    e.preventDefault(); const err = $('#login-err'); err.hidden = true;
    const btn = $('button[type="submit"]', e.target); btn.disabled = true;
    try { await api('POST', '/api/login', { password: $('#pw').value }); $('#pw').value = ''; await showApp(); }
    catch (ex) { err.textContent = ex.message; err.hidden = false; $('#pw').value = ''; $('#pw').dispatchEvent(new Event('input')); $('#pw').focus(); }
    finally { btn.disabled = false; }
  });
  $('#logout').addEventListener('click', async () => { try { await api('POST', '/api/logout'); } catch { /* already signed out */ } state.content = null; state.editing = null; $('#password-form').reset(); showLogin(); });

  async function refresh() { state.content = await api('GET', '/api/admin/content'); }

  /* ---------- navigation ---------- */
  function go(view) {
    state.view = view;
    $$('[data-view]').forEach(s => s.hidden = s.dataset.view !== view);
    $$('[data-nav]').forEach(b => b.classList.toggle('is-on', b.dataset.nav === view || (view === 'project-edit' && b.dataset.nav === 'projects') || (view === 'post-edit' && b.dataset.nav === 'posts')));
    if (view === 'projects') renderProjects();
    if (view === 'posts') renderPosts();
    if (view === 'settings') fillSettings();
    window.scrollTo(0, 0);
  }
  $$('[data-nav]').forEach(b => b.addEventListener('click', () => go(b.dataset.nav)));
  $$('[data-back]').forEach(b => b.addEventListener('click', () => go(b.dataset.back)));
  $$('[data-new]').forEach(b => b.addEventListener('click', () => b.dataset.new === 'project' ? editProject(null) : editPost(null)));

  /* ---------- helpers ---------- */
  const lines = v => (v || []).join('\n');
  const splitLines = v => String(v || '').split('\n').map(s => s.trim()).filter(Boolean);
  function fill(form, obj) {
    $$('[name]', form).forEach(el => {
      const key = el.name; const v = key.includes('.') ? key.split('.').reduce((o, k) => (o || {})[k], obj) : obj[key];
      if (el.type === 'checkbox') el.checked = !!v;
      else if (Array.isArray(v)) el.value = lines(v);
      else el.value = v == null ? '' : v;
    });
  }
  function collect(form) {
    const out = {};
    $$('[name]', form).forEach(el => {
      const v = el.type === 'checkbox' ? el.checked : el.value;
      if (el.name.includes('.')) { const [a, b] = el.name.split('.'); (out[a] = out[a] || {})[b] = v; } else out[el.name] = v;
    });
    return out;
  }
  const I = {
    edit: '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    view: '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>',
    del: '<svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/></svg>'
  };
  const statusLabel = { 'new-launch': 'New launch', 'under-construction': 'Under construction', 'ready': 'Ready to move' };

  /* ---------- projects ---------- */
  function renderProjects() {
    const q = ($('#project-search').value || '').toLowerCase();
    const list = state.content.projects.filter(p => !q || `${p.name} ${p.locality} ${p.developer}`.toLowerCase().includes(q));
    const tb = $('#projects-table tbody');
    tb.innerHTML = list.length ? list.map(p => `<tr data-id="${esc(p.id)}">
      <td class="name" data-edit>${esc(p.name)}<small>${esc(p.developer || '')}</small></td>
      <td>${esc([p.locality, p.city].filter(Boolean).join(', '))}</td>
      <td>${esc(statusLabel[p.status] || p.status)}</td>
      <td>${esc(p.price)}</td>
      <td>${esc(p.mode)}</td>
      <td><span class="badge ${p.published ? 'badge--on' : 'badge--off'}">${p.published ? 'Published' : 'Draft'}</span>${p.featured ? '<span class="badge badge--feat">Featured</span>' : ''}</td>
      <td class="actions"><button type="button" class="ic" data-edit title="Edit" aria-label="Edit">${I.edit}</button><a class="ic" href="../project.html?id=${encodeURIComponent(p.slug)}" target="_blank" rel="noopener" title="View on site" aria-label="View on site">${I.view}</a><button type="button" class="ic danger" data-del title="Delete" aria-label="Delete">${I.del}</button></td>
    </tr>`).join('') : '<tr><td colspan="7" class="empty">No projects yet. Click "New project" to add one.</td></tr>';
  }
  $('#project-search').addEventListener('input', renderProjects);
  $('#projects-table').addEventListener('click', e => {
    const tr = e.target.closest('tr[data-id]'); if (!tr) return;
    const p = state.content.projects.find(x => x.id === tr.dataset.id);
    if (e.target.closest('[data-edit]')) editProject(p);
    if (e.target.closest('[data-del]')) removeItem('projects', p);
  });

  function unitRow(u = {}) {
    return `<tr><td><input class="input" data-u="type" value="${esc(u.type)}" placeholder="2 BHK"></td><td><input class="input" data-u="carpet" value="${esc(u.carpet)}" placeholder="780 sq ft"></td><td><input class="input" data-u="builtup" value="${esc(u.builtup)}" placeholder="1,050 sq ft"></td><td><input class="input" data-u="facing" value="${esc(u.facing)}" placeholder="East"></td><td><input class="input" data-u="price" value="${esc(u.price)}" placeholder="₹62 L"></td><td><button type="button" class="rm" aria-label="Remove">×</button></td></tr>`;
  }
  $('#add-unit').addEventListener('click', () => $('#units-body').insertAdjacentHTML('beforeend', unitRow()));
  $('#units-body').addEventListener('click', e => { if (e.target.closest('.rm')) e.target.closest('tr').remove(); });
  function renderThumbs(container, urls) {
    container.innerHTML = urls.length ? urls.map(u => `<img src="../${esc(u).replace(/^\//, '')}" alt="">`).join('') : '<span class="empty">No photos yet.</span>';
  }
  const pf = $('#project-form');
  $('[name="images"]', pf).addEventListener('input', () => renderThumbs($('#thumbs'), splitLines($('[name="images"]', pf).value)));

  function editProject(p) {
    state.editing = p;
    pf.reset();
    $('[data-title]', pf).textContent = p ? p.name : 'New project';
    $('[data-delete]', pf).hidden = !p;
    const prev = $('[data-preview]', pf); prev.hidden = !p; if (p) prev.href = `../project.html?id=${encodeURIComponent(p.slug)}`;
    const obj = p || { city: 'Kolkata', tag: 'New launch', status: 'new-launch', mode: 'buy', published: true, featured: false, verdict: {} };
    fill(pf, obj);
    $('[name="nearby"]', pf).value = (obj.nearby || []).map(n => `${n.label} | ${n.value}`).join('\n');
    $('#units-body').innerHTML = (obj.units && obj.units.length ? obj.units : [{}]).map(unitRow).join('');
    renderThumbs($('#thumbs'), obj.images || []);
    go('project-edit');
  }
  pf.addEventListener('submit', async e => {
    e.preventDefault();
    const d = collect(pf);
    d.units = $$('#units-body tr').map(tr => { const o = {}; $$('[data-u]', tr).forEach(i => o[i.dataset.u] = i.value.trim()); return o; }).filter(u => u.type);
    d.nearby = splitLines(d.nearby).map(l => { const [label, value = ''] = l.split('|'); return { label: label.trim(), value: value.trim() }; });
    ['chips', 'amenities', 'images'].forEach(k => d[k] = splitLines(d[k]));
    d.verdict.liked = splitLines(d.verdict.liked); d.verdict.watch = splitLines(d.verdict.watch);
    try {
      const saved = state.editing ? await api('PUT', `/api/admin/projects/${state.editing.id}`, d) : await api('POST', '/api/admin/projects', d);
      await refresh(); toast('Project saved'); editProject(state.content.projects.find(x => x.id === saved.id));
    } catch (ex) { toast(ex.message, true); }
  });
  $('[data-delete]', pf).addEventListener('click', () => removeItem('projects', state.editing, () => go('projects')));

  /* ---------- posts ---------- */
  function renderPosts() {
    const list = state.content.posts.slice().sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    $('#posts-table tbody').innerHTML = list.length ? list.map(p => `<tr data-id="${esc(p.id)}">
      <td class="name" data-edit>${esc(p.title)}<small>/post.html?slug=${esc(p.slug)}</small></td><td>${esc(p.date)}</td><td>${esc(p.author)}</td>
      <td><span class="badge ${p.published ? 'badge--on' : 'badge--off'}">${p.published ? 'Published' : 'Draft'}</span></td>
      <td class="actions"><button type="button" class="ic" data-edit title="Edit" aria-label="Edit">${I.edit}</button><a class="ic" href="../post.html?slug=${encodeURIComponent(p.slug)}" target="_blank" rel="noopener" title="View on site" aria-label="View on site">${I.view}</a><button type="button" class="ic danger" data-del title="Delete" aria-label="Delete">${I.del}</button></td>
    </tr>`).join('') : '<tr><td colspan="5" class="empty">No posts yet. Click "New post" to write one.</td></tr>';
  }
  $('#posts-table').addEventListener('click', e => {
    const tr = e.target.closest('tr[data-id]'); if (!tr) return;
    const p = state.content.posts.find(x => x.id === tr.dataset.id);
    if (e.target.closest('[data-edit]')) editPost(p);
    if (e.target.closest('[data-del]')) removeItem('posts', p);
  });
  const bf = $('#post-form');
  const preview = () => { $('#md-preview').innerHTML = window.HR.md($('[name="body"]', bf).value) || '<p class="hint">Preview appears here as you type.</p>'; };
  $('[name="body"]', bf).addEventListener('input', preview);
  $('[name="cover"]', bf).addEventListener('input', () => renderThumbs($('#cover-thumb'), splitLines($('[name="cover"]', bf).value)));
  function editPost(p) {
    state.editing = p;
    bf.reset();
    $('[data-title]', bf).textContent = p ? p.title : 'New post';
    $('[data-delete]', bf).hidden = !p;
    const prev = $('[data-preview]', bf); prev.hidden = !p; if (p) prev.href = `../post.html?slug=${encodeURIComponent(p.slug)}`;
    fill(bf, p || { date: new Date().toISOString().slice(0, 10), author: 'HouseRoot team', published: true });
    renderThumbs($('#cover-thumb'), p && p.cover ? [p.cover] : []);
    preview(); go('post-edit');
  }
  bf.addEventListener('submit', async e => {
    e.preventDefault(); const d = collect(bf);
    try {
      const saved = state.editing ? await api('PUT', `/api/admin/posts/${state.editing.id}`, d) : await api('POST', '/api/admin/posts', d);
      await refresh(); toast('Post saved'); editPost(state.content.posts.find(x => x.id === saved.id));
    } catch (ex) { toast(ex.message, true); }
  });
  $('[data-delete]', bf).addEventListener('click', () => removeItem('posts', state.editing, () => go('posts')));

  async function removeItem(kind, item, after) {
    if (!item || !confirm(`Delete "${item.name || item.title}"? This cannot be undone.`)) return;
    try { await api('DELETE', `/api/admin/${kind}/${item.id}`); await refresh(); toast('Deleted'); (after || (() => go(kind)))(); }
    catch (ex) { toast(ex.message, true); }
  }

  /* ---------- uploads ---------- */
  const toB64 = f => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(f); });
  $$('[data-upload]').forEach(input => input.addEventListener('change', async () => {
    const target = input.dataset.upload; const status = target === 'images' ? $('#upload-status') : $('#post-upload-status');
    for (const f of Array.from(input.files)) {
      if (f.size > 6 * 1024 * 1024) { toast(`${f.name} is over 6 MB`, true); continue; }
      status.textContent = `Uploading ${f.name}…`;
      try {
        const { url } = await api('POST', '/api/admin/upload', { name: f.name, data: await toB64(f) });
        if (target === 'images') { const ta = $('[name="images"]', pf); ta.value = (ta.value.trim() ? ta.value.trim() + '\n' : '') + url; ta.dispatchEvent(new Event('input')); }
        else if (target === 'cover') { const i = $('[name="cover"]', bf); i.value = url; i.dispatchEvent(new Event('input')); }
        else { const ta = $('[name="body"]', bf); ta.value += `\n\n![${f.name.replace(/\.[^.]+$/, '')}](${url})\n`; ta.dispatchEvent(new Event('input')); }
      } catch (ex) { toast(ex.message, true); }
    }
    status.textContent = ''; input.value = '';
  }));

  /* ---------- settings ---------- */
  function fillSettings() { fill($('#settings-form'), state.content.settings || {}); }
  $('#settings-form').addEventListener('submit', async e => {
    e.preventDefault();
    try { await api('PUT', '/api/admin/settings', collect($('#settings-form'))); await refresh(); toast('Settings saved'); } catch (ex) { toast(ex.message, true); }
  });
  $('#password-form').addEventListener('submit', async e => {
    e.preventDefault();
    try {
      const r = await api('POST', '/api/admin/password', collect($('#password-form')));
      $('#password-form').reset(); $$('.pw-eye', $('#password-form')).forEach(btn => setEye(btn, false));
      if (r.reauth) { state.content = null; showLogin(); const err = $('#login-err'); err.textContent = 'Password updated. Please sign in again with the new password.'; err.style.color = '#1E7A3C'; err.hidden = false; setTimeout(() => err.style.color = '', 6000); }
      else toast('Password updated');
    } catch (ex) { toast(ex.message, true); }
  });

  /* ---------- boot ---------- */
  api('GET', '/api/admin/me').then(showApp).catch(showLogin);
})();
