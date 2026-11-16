/* HouseRoot — renders projects, blog posts and contact settings from data/content.json.
   Works with the Node server (server.js) or any static host that serves the JSON file. */
(function () {
  'use strict';
  const HR = window.HR = window.HR || {};
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  HR.esc = esc;

  /* ---------- tiny markdown ---------- */
  function inline(t) {
    return t
      .replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (m, a, u) => `<img src="${u}" alt="${a}" loading="lazy">`)
      .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, a, u) => `<a href="${u}" ${/^https?:/.test(u) ? 'target="_blank" rel="noopener"' : ''}>${a}</a>`)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, '$1<em>$2</em>');
  }
  HR.md = function (src) {
    const lines = esc(src || '').replace(/\r/g, '').split('\n');
    const out = []; let para = [], list = null;
    const flushP = () => { if (para.length) { out.push(`<p>${inline(para.join(' '))}</p>`); para = []; } };
    const flushL = () => { if (list) { out.push(`<${list.tag}>${list.items.map(i => `<li>${inline(i)}</li>`).join('')}</${list.tag}>`); list = null; } };
    for (const raw of lines) {
      const l = raw.trim();
      let m;
      if (!l) { flushP(); flushL(); continue; }
      if ((m = l.match(/^(#{1,3})\s+(.*)$/))) { flushP(); flushL(); const n = m[1].length + 1; out.push(`<h${n}>${inline(m[2])}</h${n}>`); continue; }
      if (/^(-{3,}|\*{3,})$/.test(l)) { flushP(); flushL(); out.push('<hr>'); continue; }
      if ((m = l.match(/^>\s?(.*)$/))) { flushP(); flushL(); out.push(`<blockquote>${inline(m[1])}</blockquote>`); continue; }
      if ((m = l.match(/^[-*]\s+(.*)$/))) { flushP(); if (!list || list.tag !== 'ul') { flushL(); list = { tag: 'ul', items: [] }; } list.items.push(m[1]); continue; }
      if ((m = l.match(/^\d+[.)]\s+(.*)$/))) { flushP(); if (!list || list.tag !== 'ol') { flushL(); list = { tag: 'ol', items: [] }; } list.items.push(m[1]); continue; }
      flushL(); para.push(l);
    }
    flushP(); flushL();
    return out.join('\n');
  };

  /* ---------- data ---------- */
  let cache = null;
  HR.load = function () {
    if (cache) return Promise.resolve(cache);
    return fetch('data/content.json', { cache: 'no-store' }).then(r => r.ok ? r.json() : Promise.reject(new Error(r.status)))
      .then(c => { c.projects = (c.projects || []).filter(p => p.published !== false); c.posts = (c.posts || []).filter(p => p.published !== false); return (cache = c); })
      .catch(() => null);
  };
  const fmtDate = d => { const t = new Date(d + 'T00:00:00'); return isNaN(t) ? d : t.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }); };
  const tagClass = t => /ready/i.test(t) ? ' tag--dark' : /under|villa|plot/i.test(t) ? ' tag--white' : '';
  const HEART = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#1A1A1A" stroke-width="2" stroke-linejoin="round"><path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/></svg>';
  const CHECK = '<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F58220" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><circle cx="12" cy="12" r="9"/></svg>';

  HR.card = function (p) {
    const img = p.images && p.images[0] ? `<img src="${esc(p.images[0])}" alt="${esc(p.name)}" loading="lazy">` : 'Add project photo';
    const chips = (p.chips && p.chips.length ? p.chips : [p.config, p.carpet, p.possession && 'Possession ' + p.possession, 'RERA ✓']).filter(Boolean).slice(0, 4);
    return `<article class="pcard" data-id="${esc(p.id)}">
  <div class="photo">${img}<span class="tag${tagClass(p.tag)}">${esc(p.tag || 'New launch')}</span><button type="button" class="save" aria-label="Save project" aria-pressed="false">${HEART}</button></div>
  <div class="pcard__body">
    <div class="stack" style="gap:4px"><h3 class="h-4">${esc(p.name)}</h3><span class="pcard__meta">${esc([p.locality, p.city].filter(Boolean).join(', '))} · by ${esc(p.developer)}</span></div>
    <div class="pcard__chips">${chips.map(c => `<span class="chip">${esc(c)}</span>`).join('')}</div>
    <div class="pcard__foot"><div class="stack"><span style="font-size:12px;color:#8A8A8A;font-weight:600">Starting</span><span class="price">${esc(p.price)}</span></div><a href="project.html?id=${encodeURIComponent(p.slug)}" class="btn btn--sm btn--dark">View project</a></div>
  </div>
</article>`;
  };
  function bindHearts(root) {
    root.addEventListener('click', e => {
      const b = e.target.closest('.save'); if (!b) return;
      b.classList.toggle('is-saved'); b.setAttribute('aria-pressed', b.classList.contains('is-saved'));
    });
  }

  /* ---------- filters ---------- */
  const AREA = { 'new town': ['new town', 'rajarhat'], 'salt lake': ['salt lake', 'sector v'], 'em bypass': ['bypass'], 'joka': ['joka', 'behala'], 'howrah': ['howrah'] };
  function matchArea(p, opt) {
    if (!opt || /anywhere/i.test(opt)) return true;
    const key = Object.keys(AREA).find(k => opt.toLowerCase().includes(k));
    const hay = `${p.locality} ${p.address} ${p.city}`.toLowerCase();
    return key ? AREA[key].some(w => hay.includes(w)) : hay.includes(opt.toLowerCase());
  }
  function matchType(p, opt) {
    if (!opt || /^(any|all)/i.test(opt)) return true;
    const c = (p.config || '').toLowerCase();
    if (/villa/i.test(opt)) return /villa/.test(c);
    if (/4/.test(opt)) return /\b[4-9]\b/.test(c);
    const n = opt.match(/\d/); return n ? new RegExp('\\b' + n[0] + '\\b').test(c) : true;
  }
  function matchBudget(p, opt) {
    if (!opt || /any/i.test(opt)) return true;
    const v = p.priceLakh || 0;
    if (/under/i.test(opt)) return v <= 50;
    if (/50\s*L/i.test(opt)) return v > 50 && v <= 100;
    if (/1\s*[–-]\s*2/i.test(opt)) return v > 100 && v <= 200;
    if (/2\s*Cr/i.test(opt)) return v > 200;
    return true;
  }
  function matchPossession(p, opt) {
    if (!opt || /any/i.test(opt)) return true;
    const y = new Date().getFullYear(), py = p.possessionYear || 0;
    if (/ready/i.test(opt)) return p.status === 'ready';
    if (/within 1/i.test(opt)) return p.status === 'ready' || (py && py <= y + 1);
    if (/1\s*[–-]\s*3/i.test(opt)) return py && py > y + 1 && py <= y + 3;
    return true;
  }
  function matchMode(p, mode) { return !mode || mode === 'all' || (p.mode || 'buy') === mode; }
  function matchQ(p, q) { if (!q) return true; const hay = `${p.name} ${p.locality} ${p.address} ${p.developer} ${p.config}`.toLowerCase(); return q.toLowerCase().split(/\s+/).every(w => hay.includes(w)); }

  /* ---------- pages ---------- */
  function projectsPage(c) {
    const grid = $('[data-projects-grid]'); if (!grid) return;
    const params = new URLSearchParams(location.search);
    const form = $('form.bar--4') || $('form.bar');
    const selects = form ? $$('select', form) : [];
    const sortSel = $('[data-projects-sort]');
    const statusBoxes = $$('[data-filter-status] input[type="checkbox"]');
    const seg = $('#rent') || $('.seg');
    const sub = $('[data-projects-sub]'); const count = $('[data-projects-count]');
    let mode = (params.get('mode') || (location.hash === '#rent' ? 'rent' : 'buy')).toLowerCase();
    const q = params.get('q') || '';

    // preset selects from the home search panel
    const preset = (sel, val) => { if (!sel || !val) return; const o = $$('option', sel).find(o => o.textContent.trim().toLowerCase() === val.trim().toLowerCase()); if (o) sel.value = o.value; };
    preset(selects[1], params.get('type')); preset(selects[2], params.get('budget')); preset(selects[3], params.get('possession'));
    if (seg) { const b = $$('button', seg).find(b => (b.dataset.value || b.textContent.trim()).toLowerCase() === mode); if (b && !b.classList.contains('is-on')) b.click(); }
    if (sub) sub.textContent = `${c.projects.length} RERA-registered projects · verified by our team · zero brokerage on new launches`;
    bindHearts(grid);

    const render = () => {
      const [area, type, budget, poss] = selects.map(s => s.value);
      const statuses = statusBoxes.filter(b => b.checked).map(b => b.parentElement.textContent.trim().toLowerCase());
      let list = c.projects.filter(p => matchMode(p, mode) && matchQ(p, q) && matchArea(p, area) && matchType(p, type) && matchBudget(p, budget) && matchPossession(p, poss));
      if (statuses.length && statuses.length < statusBoxes.length) {
        list = list.filter(p => statuses.some(s => (s.includes('new') && p.status === 'new-launch') || (s.includes('under') && p.status === 'under-construction') || (s.includes('ready') && p.status === 'ready')));
      }
      const sort = sortSel ? sortSel.value : '';
      if (/low to high/i.test(sort)) list.sort((a, b) => (a.priceLakh || 0) - (b.priceLakh || 0));
      else if (/high to low/i.test(sort)) list.sort((a, b) => (b.priceLakh || 0) - (a.priceLakh || 0));
      else if (/soonest/i.test(sort)) list.sort((a, b) => (a.status === 'ready' ? 0 : a.possessionYear || 9999) - (b.status === 'ready' ? 0 : b.possessionYear || 9999));
      else list.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0));
      grid.innerHTML = list.length ? list.map(HR.card).join('') : `<div class="stack" style="grid-column:1/-1;align-items:center;text-align:center;padding:48px 0;gap:10px"><strong class="h-4">No projects match these filters yet</strong><span style="color:#6E6E6E;font-size:14px">Try widening the budget or area, or tell us your brief and we will shortlist for you.</span><a href="contact.html" class="btn btn--sm" style="margin-top:8px">Get a shortlist</a></div>`;
      if (count) count.textContent = `${list.length} project${list.length === 1 ? '' : 's'}`;
      grid.classList.add('is-in');
    };
    selects.forEach(s => s.addEventListener('change', render));
    if (form) form.addEventListener('submit', e => { e.preventDefault(); render(); });
    statusBoxes.forEach(b => b.addEventListener('change', render));
    if (sortSel) sortSel.addEventListener('change', render);
    if (seg) seg.addEventListener('segchange', e => { mode = String(e.detail).toLowerCase(); render(); });
    render();
  }

  function featured(c) {
    const grid = $('[data-featured-grid]'); if (!grid) return;
    const list = c.projects.filter(p => p.featured).concat(c.projects.filter(p => !p.featured)).slice(0, 3);
    if (list.length) { grid.innerHTML = list.map(HR.card).join(''); bindHearts(grid); }
  }

  function setText(sel, v) { const el = $(`[data-p="${sel}"]`); if (el && v != null && v !== '') el.textContent = v; return el; }
  function projectPage(c) {
    if (!$('[data-p="name"]')) return;
    const slug = new URLSearchParams(location.search).get('id');
    const p = c.projects.find(x => x.slug === slug) || c.projects[0];
    if (!p) return;
    document.title = `${p.name} · HouseRoot`;
    setText('crumb', p.name); setText('name', p.name); setText('address', p.address || [p.locality, p.city].filter(Boolean).join(', ')); setText('developer', p.developer);
    const tag = setText('tag', p.tag); if (tag) tag.className = 'tag' + tagClass(p.tag); setText('rera', p.rera ? `RERA ${p.rera}` : 'RERA registered');
    setText('price', p.price); setText('psf', p.pricePerSqft);
    const gal = $('[data-p="gallery"]');
    if (gal && p.images && p.images.length) $$('.photo', gal).forEach((ph, i) => { const src = p.images[i] || p.images[0]; const keep = $$('button, .pill', ph); ph.textContent = ''; ph.innerHTML = `<img src="${esc(src)}" alt="${esc(p.name)} photo ${i + 1}">`; keep.forEach(k => ph.appendChild(k)); });
    const facts = $$('[data-p="facts"] .fact strong'); const fv = [p.config, p.carpet, p.possession, p.towers];
    facts.forEach((f, i) => { if (fv[i]) f.textContent = fv[i]; });
    const about = $('[data-p="about"]');
    if (about && (p.about || p.developerNote)) { const ps = $$('p', about); if (ps[0]) ps[0].textContent = p.about || ''; if (ps[1]) { ps[1].textContent = p.developerNote || ''; ps[1].hidden = !p.developerNote; } }
    const units = $('[data-p="units"]');
    if (units && p.units && p.units.length) units.innerHTML = p.units.map(u => `<tr><td style="font-weight:600">${esc(u.type)}</td><td>${esc(u.carpet)}</td><td>${esc(u.builtup)}</td><td>${esc(u.facing)}</td><td style="font-weight:700;color:#F26B0E">${esc(u.price)}</td><td><a href="contact.html" style="font-weight:700;font-size:13px">Floor plan →</a></td></tr>`).join('');
    const sel = $('[data-p="unitselect"]');
    if (sel && p.units && p.units.length) sel.innerHTML = p.units.map(u => `<option>Interested in: ${esc(u.type)}</option>`).join('');
    const amen = $('[data-p="amen"]');
    if (amen && p.amenities && p.amenities.length) { amen.innerHTML = p.amenities.map(a => `<div>${CHECK}${esc(a)}</div>`).join(''); amen.classList.add('is-in'); }
    const near = $('[data-p="near"]');
    if (near && p.nearby && p.nearby.length) near.innerHTML = p.nearby.map(n => `<div class="near"><span>${esc(n.label)}</span><strong>${esc(n.value)}</strong></div>`).join('');
    const map = $('[data-p="map"]');
    if (map && p.mapEmbed) { const src = p.mapEmbed.match(/src="([^"]+)"/); const url = src ? src[1] : p.mapEmbed; if (/^https:\/\/(www\.)?google\.[a-z.]+\/maps/.test(url)) map.innerHTML = `<iframe src="${esc(url)}" width="100%" height="100%" style="border:0;position:absolute;inset:0" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen title="Map"></iframe>`; }
    if (p.verdict) {
      if (p.verdict.goodFor) setText('goodfor', `Good for: ${p.verdict.goodFor}`);
      const liked = $('[data-p="liked"]'); if (liked && p.verdict.liked && p.verdict.liked.length) liked.innerHTML = p.verdict.liked.map(x => `<li>${esc(x)}</li>`).join('');
      const watch = $('[data-p="watch"]'); if (watch && p.verdict.watch && p.verdict.watch.length) watch.innerHTML = p.verdict.watch.map(x => `<li>${esc(x)}</li>`).join('');
    }
    if (p.advisor) { setText('advisor', p.advisor); setText('advpic', p.advisor.split(/\s+/).map(w => w[0]).join('').slice(0, 2).toUpperCase()); setText('walked', `Walked by ${p.advisor}${p.walkedOn ? ', ' + p.walkedOn : ''}. We're paid by the developer; our verdict is still ours.`); }
    const sim = $('[data-similar-grid]');
    if (sim) { const others = c.projects.filter(x => x.id !== p.id); const near = others.filter(x => x.locality === p.locality); const list = near.concat(others.filter(x => !near.includes(x))).slice(0, 3); if (list.length) { sim.innerHTML = list.map(HR.card).join(''); bindHearts(sim); } }
  }

  function blogPage(c) {
    const list = $('[data-blog-list]'); if (!list) return;
    const posts = c.posts.slice().sort((a, b) => (b.date || '').localeCompare(a.date || ''));
    list.innerHTML = posts.length ? posts.map(p => `<article class="post-card">
  <a href="post.html?slug=${encodeURIComponent(p.slug)}" class="post-card__img photo">${p.cover ? `<img src="${esc(p.cover)}" alt="" loading="lazy">` : 'Add cover image'}</a>
  <div class="post-card__body stack" style="gap:8px">
    <span class="post-card__meta">${esc(fmtDate(p.date))}${p.author ? ' · ' + esc(p.author) : ''}</span>
    <h2 class="h-4"><a href="post.html?slug=${encodeURIComponent(p.slug)}">${esc(p.title)}</a></h2>
    <p>${esc(p.excerpt)}</p>
    <a href="post.html?slug=${encodeURIComponent(p.slug)}" class="link">Read more →</a>
  </div>
</article>`).join('') : '<p class="lede">No posts yet. Add one from the admin panel.</p>';
  }
  function postPage(c) {
    const el = $('[data-post]'); if (!el) return;
    const slug = new URLSearchParams(location.search).get('slug');
    const p = c.posts.find(x => x.slug === slug) || c.posts[0];
    if (!p) { el.innerHTML = '<p class="lede">Post not found. <a href="blog.html">Back to the blog</a>.</p>'; return; }
    document.title = `${p.title} · HouseRoot`;
    el.innerHTML = `<div class="stack" style="gap:12px"><span class="eyebrow">Blog</span><h1 class="h-2">${esc(p.title)}</h1><span class="post-card__meta">${esc(fmtDate(p.date))}${p.author ? ' · ' + esc(p.author) : ''}</span></div>
${p.cover ? `<div class="photo post-cover"><img src="${esc(p.cover)}" alt=""></div>` : ''}
<div class="prose">${HR.md(p.body)}</div>
<div class="row" style="gap:12px;flex-wrap:wrap;padding-top:8px"><a href="blog.html" class="btn btn--outline btn--sm">← All posts</a><a href="contact.html" class="btn btn--sm">Talk to an advisor</a></div>`;
  }

  function applySettings(c) {
    const s = c.settings || {};
    if (s.whatsapp) $$('a[href*="wa.me/91XXXXXXXXXX"]').forEach(a => a.href = `https://wa.me/${s.whatsapp}`);
    if (s.phone) $$('a[href^="tel:"]').forEach(a => { a.href = `tel:${s.phone.replace(/\s/g, '')}`; });
    const swap = (from, to) => { if (!to) return; const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); const nodes = []; while (walker.nextNode()) if (walker.currentNode.nodeValue.includes(from)) nodes.push(walker.currentNode); nodes.forEach(n => n.nodeValue = n.nodeValue.split(from).join(to)); };
    swap('[WB/XXXXX]', s.rera); swap('[+91 XXXXX XXXXX]', s.phone); swap('[Office address line 1]', s.address1); swap('[Line 2], Kolkata – [PIN]', s.address2);
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (document.body.classList.contains('admin')) return;
    HR.load().then(c => { if (!c) return; applySettings(c); featured(c); projectsPage(c); projectPage(c); blogPage(c); postPage(c); });
  });
})();
