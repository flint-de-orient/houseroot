/* HouseRoot — main.js
   Progressive enhancement only: every page works without this file. */
(function () {
  'use strict';
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Sticky header shrink ---------- */
  const header = $('.header');
  if (header) {
    const onScroll = () => header.classList.toggle('is-stuck', window.scrollY > 24);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ---------- Active nav link ---------- */
  const here = location.pathname.split('/').pop() || 'index.html';
  $$('.nav a:not(.btn), .drawer a:not(.btn)').forEach(a => {
    const href = a.getAttribute('href') || '';
    if (href === here || (here === 'index.html' && href === './')) a.classList.add('is-active');
  });

  /* ---------- Mobile drawer ---------- */
  const burger = $('.nav__burger');
  const drawer = $('.drawer');
  if (burger && drawer) {
    const open = (v) => {
      drawer.classList.toggle('is-open', v);
      burger.classList.toggle('is-open', v);
      burger.setAttribute('aria-expanded', String(v));
      document.body.style.overflow = v ? 'hidden' : '';
    };
    burger.addEventListener('click', () => open(!drawer.classList.contains('is-open')));
    $('.drawer__scrim', drawer).addEventListener('click', () => open(false));
    $('.drawer__close', drawer).addEventListener('click', () => open(false));
    document.addEventListener('keydown', e => { if (e.key === 'Escape') open(false); });
  }

  /* ---------- Reveal on scroll ---------- */
  const revealEls = $$('[data-reveal], [data-stagger]');
  if (revealEls.length && 'IntersectionObserver' in window && !reduced) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    revealEls.forEach(el => io.observe(el));
  } else {
    revealEls.forEach(el => el.classList.add('is-in'));
  }

  /* ---------- Word-by-word headline ---------- */
  $$('.words').forEach(h => {
    if (reduced) return;
    const walk = (node) => {
      Array.from(node.childNodes).forEach(n => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach(part => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            const s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
      });
    };
    walk(h);
    $$('.w', h).forEach((w, i) => w.style.animationDelay = (0.08 + i * 0.07) + 's');
  });

  /* ---------- Count-up numbers ---------- */
  const counters = $$('[data-count]');
  if (counters.length) {
    const run = (el) => {
      const target = parseFloat(el.dataset.count);
      const suffix = el.dataset.suffix || '';
      const decimals = (String(target).split('.')[1] || '').length;
      const dur = 1400, t0 = performance.now();
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        const e = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * e).toFixed(decimals) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      };
      if (reduced) { el.textContent = target.toFixed(decimals) + suffix; return; }
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver((entries) => {
      entries.forEach(en => { if (en.isIntersecting) { run(en.target); io.unobserve(en.target); } });
    }, { threshold: 0.5 });
    counters.forEach(c => io.observe(c));
  }

  /* ---------- Segmented controls (sliding thumb) ---------- */
  $$('.seg').forEach(seg => {
    let thumb = $('.seg__thumb', seg);
    if (!thumb) { thumb = document.createElement('span'); thumb.className = 'seg__thumb'; seg.prepend(thumb); }
    const btns = $$('button', seg);
    const move = (b) => {
      thumb.style.left = b.offsetLeft + 'px';
      thumb.style.width = b.offsetWidth + 'px';
      btns.forEach(x => { x.classList.toggle('is-on', x === b); x.setAttribute('aria-pressed', String(x === b)); });
      seg.dispatchEvent(new CustomEvent('segchange', { detail: b.dataset.value || b.textContent.trim() }));
    };
    const byHash = () => btns.find(b => seg.id && location.hash === '#' + seg.id && (b.dataset.value || b.textContent.trim()).toLowerCase() === seg.id);
    const init = byHash() || btns.find(b => b.classList.contains('is-on')) || btns[0];
    if (init) { thumb.style.transition = 'none'; move(init); requestAnimationFrame(() => thumb.style.transition = ''); }
    seg.addEventListener('hashtarget', () => { const b = byHash(); if (b) move(b); });
    btns.forEach(b => b.addEventListener('click', () => move(b)));
    window.addEventListener('resize', () => { const on = btns.find(b => b.classList.contains('is-on')); if (on) move(on); });
  });

  /* ---------- Finder tabs (home search panel) ---------- */
  $$('.finder__tabs').forEach(tabs => {
    const hidden = $('input[name="mode"]', tabs.closest('form'));
    $$('button', tabs).forEach(b => b.addEventListener('click', () => {
      $$('button', tabs).forEach(x => { x.classList.toggle('is-on', x === b); x.setAttribute('aria-selected', String(x === b)); });
      if (hidden) hidden.value = b.dataset.value || b.textContent.trim().toLowerCase();
    }));
  });

  /* ---------- Agent filter (contact page) ---------- */
  const agentSeg = $('[data-agent-filter]');
  if (agentSeg) {
    agentSeg.addEventListener('segchange', (e) => {
      const v = e.detail.toLowerCase();
      $$('.agent').forEach(a => {
        const areas = (a.dataset.area || '').toLowerCase();
        a.classList.toggle('is-hidden', !(v === 'all' || areas.includes(v)));
      });
    });
  }

  /* ---------- Save hearts ---------- */
  $$('.save').forEach(b => b.addEventListener('click', () => {
    b.classList.toggle('is-saved');
    b.setAttribute('aria-pressed', b.classList.contains('is-saved'));
  }));

  /* ---------- Filter rail toggle (mobile) ---------- */
  const railToggle = $('.rail__toggle');
  if (railToggle) railToggle.addEventListener('click', () => {
    const rail = railToggle.closest('.rail');
    rail.classList.toggle('is-open');
    railToggle.textContent = rail.classList.contains('is-open') ? 'Hide filters' : 'Show filters';
  });

  /* ---------- Detail page tabs: scroll-spy ---------- */
  const tabs = $('.tabs');
  if (tabs) {
    const links = $$('a', tabs);
    const targets = links.map(a => $(a.getAttribute('href'))).filter(Boolean);
    const io = new IntersectionObserver((entries) => {
      entries.forEach(en => {
        if (en.isIntersecting) links.forEach(a => a.classList.toggle('is-on', a.getAttribute('href') === '#' + en.target.id));
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    targets.forEach(t => io.observe(t));
  }

  /* ---------- FAQ: animated open/close ---------- */
  $$('.faq details').forEach(d => {
    const body = $('.faq__body', d);
    if (!body || reduced) return;
    d.addEventListener('toggle', () => {
      if (d.open) {
        body.style.height = '0px';
        requestAnimationFrame(() => {
          body.style.transition = 'height .35s cubic-bezier(.22,1,.36,1)';
          body.style.height = body.scrollHeight + 'px';
          body.addEventListener('transitionend', () => { body.style.height = ''; body.style.transition = ''; }, { once: true });
        });
      }
    });
  });

  /* ---------- Forms: validate + fake-submit ---------- */
  $$('form[data-lead]').forEach(f => {
    f.addEventListener('submit', (e) => {
      e.preventDefault();
      const phone = $('input[type="tel"]', f);
      if (phone && !/^\+?[\d\s-]{10,15}$/.test(phone.value.trim())) {
        phone.focus(); phone.style.boxShadow = '0 0 0 2px #D14F00';
        phone.addEventListener('input', () => phone.style.boxShadow = '', { once: true });
        return;
      }
      const btn = $('button[type="submit"]', f);
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      // TODO: replace with your endpoint (FlintBox / n8n webhook).
      // fetch('/api/lead', { method:'POST', body: new FormData(f) })
      setTimeout(() => {
        const card = f.closest('.form-card, .glass-form, .sticky-card') || f;
        card.classList.add('is-sent');
        const ok = $('.form-success', card);
        if (ok) ok.classList.add('is-on');
      }, 700);
    });
  });

  /* ---------- Page transition on internal links ---------- */
  if (!reduced) {
    $$('a[href]').forEach(a => {
      const href = a.getAttribute('href');
      if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto') || href.startsWith('tel') || a.target === '_blank') return;
      a.addEventListener('click', (e) => {
        if (e.metaKey || e.ctrlKey) return;
        const target = new URL(href, location.href);
        if (target.pathname === location.pathname) {
          // Same page, only the #anchor changes: let the browser jump, no fade.
          if (target.hash) {
            const el = document.getElementById(target.hash.slice(1));
            if (el) { e.preventDefault(); history.pushState(null, '', target.hash); el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.dispatchEvent(new CustomEvent('hashtarget')); }
          }
          return;
        }
        e.preventDefault();
        document.body.classList.add('is-leaving');
        setTimeout(() => location.href = href, 260);
      });
    });
  }

  /* ---------- Year ---------- */
  $$('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
