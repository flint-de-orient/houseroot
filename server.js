#!/usr/bin/env node
/* HouseRoot — tiny content server + admin API.
   No dependencies. Run:  node server.js
   Env: PORT (default 8080), HOST (default 127.0.0.1), ADMIN_PASSWORD (optional override). */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = __dirname;
const DATA_DIR = path.join(ROOT, 'data');
const CONTENT = path.join(DATA_DIR, 'content.json');
const ADMIN_FILE = path.join(DATA_DIR, 'admin.json');
const SECRET_FILE = path.join(DATA_DIR, 'secret.key');
const UPLOAD_DIR = path.join(ROOT, 'assets', 'uploads');
const PORT = Number(process.env.PORT || 8080);
const HOST = process.env.HOST || '127.0.0.1';
const COOKIE = 'hr_admin';
const SESSION_HOURS = Number(process.env.ADMIN_SESSION_HOURS || 12);
const LOCK_FILE = path.join(DATA_DIR, 'lockouts.json');
const AUDIT_FILE = path.join(DATA_DIR, 'audit.log');
const MAX_FAILS = 5;                 // wrong passwords allowed per window
const FAIL_WINDOW = 15 * 60 * 1000;  // window for counting failures
const BASE_LOCK = 15 * 60 * 1000;    // first lockout; doubles on each repeat, capped at 24 h
const MAX_LOCK = 24 * 60 * 60 * 1000;
const ALLOW_IPS = (process.env.ADMIN_ALLOW_IPS || '').split(',').map(s => s.trim()).filter(Boolean);
const MAX_BODY = 8 * 1024 * 1024;

const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.svg': 'image/svg+xml', '.gif': 'image/gif', '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml; charset=utf-8',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.map': 'application/json', '.pdf': 'application/pdf', '.mp4': 'video/mp4'
};

/* ---------- setup ---------- */
fs.mkdirSync(DATA_DIR, { recursive: true });
fs.mkdirSync(UPLOAD_DIR, { recursive: true });
if (!fs.existsSync(SECRET_FILE)) fs.writeFileSync(SECRET_FILE, crypto.randomBytes(32).toString('hex'), { mode: 0o600 });
const SECRET = fs.readFileSync(SECRET_FILE, 'utf8').trim();

function hashPassword(pw, salt) {
  salt = salt || crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(pw, salt, 64).toString('hex');
  return { salt, hash };
}
function safeEqual(a, b) {
  const ba = Buffer.from(String(a)), bb = Buffer.from(String(b));
  return ba.length === bb.length && crypto.timingSafeEqual(ba, bb);
}
let admin;
if (fs.existsSync(ADMIN_FILE)) {
  admin = JSON.parse(fs.readFileSync(ADMIN_FILE, 'utf8'));
} else {
  const initial = process.env.ADMIN_PASSWORD || 'houseroot1';
  admin = hashPassword(initial); admin.v = 1;
  fs.writeFileSync(ADMIN_FILE, JSON.stringify(admin), { mode: 0o600 });
  console.log(`[admin] First run: password set to "${initial}". Change it from the admin panel (Settings → Password).`);
}
function checkPassword(pw) {
  if (process.env.ADMIN_PASSWORD) return safeEqual(pw, process.env.ADMIN_PASSWORD);
  return safeEqual(hashPassword(pw, admin.salt).hash, admin.hash);
}

/* ---------- sessions (signed cookie) ---------- */
function sign(payload) {
  const data = Buffer.from(JSON.stringify(payload)).toString('base64url');
  const mac = crypto.createHmac('sha256', SECRET).update(data).digest('base64url');
  return `${data}.${mac}`;
}
function verify(token) {
  if (!token || !token.includes('.')) return null;
  const [data, mac] = token.split('.');
  const expect = crypto.createHmac('sha256', SECRET).update(data).digest('base64url');
  if (!safeEqual(mac, expect)) return null;
  try {
    const payload = JSON.parse(Buffer.from(data, 'base64url').toString());
    if (!payload.exp || payload.exp < Date.now()) return null;
    if ((payload.v || 0) !== (admin.v || 0)) return null; // password changed since: session is dead
    return payload;
  } catch { return null; }
}
function parseCookies(req) {
  const out = {};
  (req.headers.cookie || '').split(';').forEach(c => { const i = c.indexOf('='); if (i > 0) out[c.slice(0, i).trim()] = decodeURIComponent(c.slice(i + 1).trim()); });
  return out;
}
function isAdmin(req) { return !!verify(parseCookies(req)[COOKIE]); }

/* ---------- content store ---------- */
function readContent() {
  try { return JSON.parse(fs.readFileSync(CONTENT, 'utf8')); }
  catch { return { settings: {}, projects: [], posts: [] }; }
}
function writeContent(obj) {
  const tmp = CONTENT + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2));
  fs.renameSync(tmp, CONTENT);
}
function publicView(c) {
  return {
    settings: c.settings || {},
    projects: (c.projects || []).filter(p => p.published !== false),
    posts: (c.posts || []).filter(p => p.published !== false)
  };
}
const slugify = s => String(s || '').toLowerCase().normalize('NFKD').replace(/[^\w\s-]/g, '').trim().replace(/[\s_-]+/g, '-').replace(/^-+|-+$/g, '') || 'item';
const newId = p => p + '_' + crypto.randomBytes(4).toString('hex');
const str = (v, max = 4000) => String(v == null ? '' : v).slice(0, max);
const lines = v => Array.isArray(v) ? v.map(x => str(x, 300)).filter(Boolean) : str(v).split('\n').map(s => s.trim()).filter(Boolean);

function cleanProject(input, existing) {
  const p = Object.assign({}, existing || {});
  p.name = str(input.name, 200);
  p.slug = slugify(input.slug || input.name);
  p.locality = str(input.locality, 100);
  p.city = str(input.city || 'Kolkata', 100);
  p.address = str(input.address, 300);
  p.developer = str(input.developer, 200);
  p.tag = str(input.tag, 40);
  p.status = ['new-launch', 'under-construction', 'ready'].includes(input.status) ? input.status : 'new-launch';
  p.mode = ['buy', 'rent', 'plots', 'commercial'].includes(input.mode) ? input.mode : 'buy';
  p.featured = !!input.featured;
  p.published = input.published !== false;
  p.price = str(input.price, 40);
  p.priceLakh = Number(input.priceLakh) || 0;
  p.pricePerSqft = str(input.pricePerSqft, 120);
  p.config = str(input.config, 80);
  p.carpet = str(input.carpet, 80);
  p.possession = str(input.possession, 60);
  p.possessionYear = Number(input.possessionYear) || 0;
  p.towers = str(input.towers, 60);
  p.rera = str(input.rera, 60);
  p.chips = lines(input.chips).slice(0, 6);
  p.about = str(input.about, 5000);
  p.developerNote = str(input.developerNote, 3000);
  p.units = (Array.isArray(input.units) ? input.units : []).slice(0, 20).map(u => ({
    type: str(u.type, 60), carpet: str(u.carpet, 40), builtup: str(u.builtup, 40), facing: str(u.facing, 60), price: str(u.price, 40)
  })).filter(u => u.type);
  p.amenities = lines(input.amenities).slice(0, 30);
  p.nearby = (Array.isArray(input.nearby) ? input.nearby : lines(input.nearby).map(l => { const [label, value] = l.split('|'); return { label, value }; }))
    .slice(0, 15).map(n => ({ label: str(n.label, 100).trim(), value: str(n.value, 40).trim() })).filter(n => n.label);
  const v = input.verdict || {};
  p.verdict = { goodFor: str(v.goodFor, 300), liked: lines(v.liked).slice(0, 8), watch: lines(v.watch).slice(0, 8) };
  p.advisor = str(input.advisor, 100);
  p.walkedOn = str(input.walkedOn, 60);
  p.images = lines(input.images).slice(0, 12);
  p.mapEmbed = str(input.mapEmbed, 1000);
  return p;
}
function cleanPost(input, existing) {
  const p = Object.assign({}, existing || {});
  p.title = str(input.title, 200);
  p.slug = slugify(input.slug || input.title);
  p.date = /^\d{4}-\d{2}-\d{2}$/.test(input.date || '') ? input.date : new Date().toISOString().slice(0, 10);
  p.author = str(input.author, 100);
  p.cover = str(input.cover, 500);
  p.excerpt = str(input.excerpt, 500);
  p.body = str(input.body, 60000);
  p.published = input.published !== false;
  return p;
}
function uniqueSlug(list, slug, id) {
  let s = slug, n = 2;
  while (list.some(x => x.slug === s && x.id !== id)) s = `${slug}-${n++}`;
  return s;
}

/* ---------- helpers ---------- */
function send(res, code, body, headers = {}) {
  const isObj = body !== null && typeof body === 'object' && !Buffer.isBuffer(body);
  const data = isObj ? JSON.stringify(body) : body;
  res.writeHead(code, Object.assign({ 'Content-Type': isObj ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8', 'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-store' }, SECURITY_HEADERS, headers));
  res.end(data);
}
function readJson(req) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on('data', c => { size += c.length; if (size > MAX_BODY) { reject(new Error('too large')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => { try { resolve(chunks.length ? JSON.parse(Buffer.concat(chunks).toString()) : {}); } catch (e) { reject(e); } });
    req.on('error', reject);
  });
}
/* ---------- login throttling (persisted so a restart does not reset it) ---------- */
function loadLocks() { try { return JSON.parse(fs.readFileSync(LOCK_FILE, 'utf8')); } catch { return {}; } }
function saveLocks(l) { try { fs.writeFileSync(LOCK_FILE, JSON.stringify(l), { mode: 0o600 }); } catch (e) { console.error('lockouts', e.message); } }
function clientIp(req) {
  const fwd = process.env.TRUST_PROXY ? String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() : '';
  return fwd || req.socket.remoteAddress || 'unknown';
}
function lockState(ip) {
  const locks = loadLocks(); const now = Date.now(); let changed = false;
  for (const k of Object.keys(locks)) { const e = locks[k]; if ((!e.until || e.until < now) && now - (e.first || 0) > FAIL_WINDOW && now - (e.last || 0) > MAX_LOCK) { delete locks[k]; changed = true; } }
  if (changed) saveLocks(locks);
  const e = locks[ip] || { fails: 0, first: now, last: 0, until: 0, locks: 0 };
  if (e.until && e.until > now) return { locked: true, retryAfter: Math.ceil((e.until - now) / 1000), remaining: 0 };
  if (now - e.first > FAIL_WINDOW) { e.fails = 0; e.first = now; }
  return { locked: false, retryAfter: 0, remaining: MAX_FAILS - e.fails, entry: e, locks };
}
function noteFailure(ip) {
  const st = lockState(ip); if (st.locked) return st;
  const e = st.entry; const now = Date.now();
  e.fails++; e.last = now;
  if (e.fails >= MAX_FAILS) { const dur = Math.min(BASE_LOCK * Math.pow(2, e.locks || 0), MAX_LOCK); e.until = now + dur; e.locks = (e.locks || 0) + 1; e.fails = 0; e.first = now; }
  st.locks[ip] = e; saveLocks(st.locks);
  return e.until > now ? { locked: true, retryAfter: Math.ceil((e.until - now) / 1000), remaining: 0 } : { locked: false, remaining: MAX_FAILS - e.fails };
}
function clearFailures(ip) { const locks = loadLocks(); if (locks[ip]) { delete locks[ip]; saveLocks(locks); } }
const sleep = ms => new Promise(r => setTimeout(r, ms));
function audit(req, action, detail = '') {
  const line = `${new Date().toISOString()} ${clientIp(req)} ${action}${detail ? ' ' + detail : ''}\n`;
  fs.appendFile(AUDIT_FILE, line, () => {});
}
function cookieFlags(req) {
  const https = process.env.SECURE_COOKIES === '1' || req.headers['x-forwarded-proto'] === 'https';
  return `Path=/; HttpOnly; SameSite=Strict${https ? '; Secure' : ''}`;
}
const SECURITY_HEADERS = { 'X-Frame-Options': 'DENY', 'Referrer-Policy': 'no-referrer', 'Permissions-Policy': 'camera=(), microphone=(), geolocation=()' };
const ADMIN_CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'";
const MAGIC = {
  '.jpg': b => b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF, '.jpeg': b => b[0] === 0xFF && b[1] === 0xD8 && b[2] === 0xFF,
  '.png': b => b.slice(0, 8).equals(Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])),
  '.gif': b => b.slice(0, 4).toString() === 'GIF8',
  '.webp': b => b.slice(0, 4).toString() === 'RIFF' && b.slice(8, 12).toString() === 'WEBP',
  '.pdf': b => b.slice(0, 4).toString() === '%PDF'
};

/* ---------- API ---------- */
async function api(req, res, url) {
  const p = url.pathname;
  const method = req.method;
  const mutating = method !== 'GET';
  if (mutating && req.headers['x-requested-with'] !== 'HouseRootAdmin') return send(res, 403, { error: 'Missing request header' });
  const ip = clientIp(req);
  if (ALLOW_IPS.length && (p === '/api/login' || p.startsWith('/api/admin/')) && !ALLOW_IPS.includes(ip)) { audit(req, 'blocked-ip', p); return send(res, 403, { error: 'Admin access is not allowed from this network' }); }

  if (p === '/api/login' && method === 'POST') {
    const st = lockState(ip);
    if (st.locked) { audit(req, 'login-locked'); return send(res, 429, { error: `Too many wrong passwords. Try again in ${Math.ceil(st.retryAfter / 60)} min.`, retryAfter: st.retryAfter }, { 'Retry-After': String(st.retryAfter) }); }
    const body = await readJson(req);
    const pw = String(body.password || '');
    if (pw.length > 64 || !checkPassword(pw)) {
      const after = noteFailure(ip); audit(req, 'login-fail');
      await sleep(800); // slow down guessing
      if (after.locked) return send(res, 429, { error: `Too many wrong passwords. Locked for ${Math.ceil(after.retryAfter / 60)} min.`, retryAfter: after.retryAfter }, { 'Retry-After': String(after.retryAfter) });
      return send(res, 401, { error: `Wrong password. ${after.remaining} attempt${after.remaining === 1 ? '' : 's'} left before a lockout.`, remaining: after.remaining });
    }
    clearFailures(ip); audit(req, 'login-ok');
    const maxAge = SESSION_HOURS * 3600;
    const token = sign({ exp: Date.now() + maxAge * 1000, v: admin.v || 0, r: crypto.randomBytes(6).toString('hex') });
    return send(res, 200, { ok: true }, { 'Set-Cookie': `${COOKIE}=${token}; ${cookieFlags(req)}; Max-Age=${maxAge}` });
  }
  if (p === '/api/logout' && method === 'POST') { audit(req, 'logout'); return send(res, 200, { ok: true }, { 'Set-Cookie': `${COOKIE}=; ${cookieFlags(req)}; Max-Age=0` }); }
  if (p === '/api/content' && method === 'GET') return send(res, 200, publicView(readContent()), { 'Cache-Control': 'no-store' });

  if (!p.startsWith('/api/admin/')) return send(res, 404, { error: 'Not found' });
  if (!isAdmin(req)) return send(res, 401, { error: 'Not signed in' });

  const content = readContent();
  const seg = p.split('/').filter(Boolean); // api, admin, <resource>, <id?>
  const resource = seg[2], id = seg[3];

  if (resource === 'me') return send(res, 200, { ok: true });
  if (resource === 'content' && method === 'GET') return send(res, 200, content, { 'Cache-Control': 'no-store' });

  if (resource === 'settings' && method === 'PUT') {
    const b = await readJson(req);
    content.settings = { whatsapp: str(b.whatsapp, 20).replace(/\D/g, ''), phone: str(b.phone, 30), email: str(b.email, 120), rera: str(b.rera, 60), address1: str(b.address1, 200), address2: str(b.address2, 200) };
    writeContent(content); audit(req, 'settings-update'); return send(res, 200, content.settings);
  }
  if (resource === 'password' && method === 'POST') {
    const b = await readJson(req);
    if (!checkPassword(String(b.current || ''))) return send(res, 400, { error: 'Current password is wrong' });
    const next = String(b.next || '');
    if (next.length < 8 || next.length > 64) return send(res, 400, { error: 'New password must be 8 to 64 characters' });
    if (!/[a-zA-Z]/.test(next) || !/\d/.test(next)) return send(res, 400, { error: 'Use at least one letter and one number' });
    if (next === String(b.current)) return send(res, 400, { error: 'New password must be different from the current one' });
    admin = Object.assign(hashPassword(next), { v: (admin.v || 0) + 1 }); fs.writeFileSync(ADMIN_FILE, JSON.stringify(admin), { mode: 0o600 });
    audit(req, 'password-changed');
    // every existing session (including this one) is now invalid; the panel asks for a fresh sign-in
    return send(res, 200, { ok: true, reauth: true }, { 'Set-Cookie': `${COOKIE}=; ${cookieFlags(req)}; Max-Age=0` });
  }
  if (resource === 'upload' && method === 'POST') {
    const b = await readJson(req);
    const ext = path.extname(String(b.name || '')).toLowerCase();
    if (!['.jpg', '.jpeg', '.png', '.webp', '.gif', '.pdf'].includes(ext)) return send(res, 400, { error: 'Only jpg, png, webp, gif or pdf' });
    const buf = Buffer.from(String(b.data || '').replace(/^data:[^;]+;base64,/, ''), 'base64');
    if (!buf.length || buf.length > 6 * 1024 * 1024) return send(res, 400, { error: 'File is empty or over 6 MB' });
    if (buf.length < 12 || !MAGIC[ext](buf)) return send(res, 400, { error: 'File content does not match its type' });
    const name = `${Date.now().toString(36)}-${crypto.randomBytes(3).toString('hex')}${ext}`;
    fs.writeFileSync(path.join(UPLOAD_DIR, name), buf);
    audit(req, 'upload', name);
    return send(res, 200, { url: `assets/uploads/${name}` });
  }

  const listKey = resource === 'projects' ? 'projects' : resource === 'posts' ? 'posts' : null;
  if (!listKey) return send(res, 404, { error: 'Not found' });
  const list = content[listKey] = content[listKey] || [];
  const clean = listKey === 'projects' ? cleanProject : cleanPost;
  const prefix = listKey === 'projects' ? 'p' : 'b';

  if (method === 'POST' && !id) {
    const b = await readJson(req);
    const item = clean(b); item.id = newId(prefix); item.slug = uniqueSlug(list, item.slug, item.id);
    list.unshift(item); writeContent(content); audit(req, `${listKey}-create`, item.id); return send(res, 201, item);
  }
  const idx = list.findIndex(x => x.id === id);
  if (idx < 0) return send(res, 404, { error: 'Not found' });
  if (method === 'PUT') {
    const b = await readJson(req);
    const item = clean(b, list[idx]); item.id = id; item.slug = uniqueSlug(list, item.slug, id);
    list[idx] = item; writeContent(content); audit(req, `${listKey}-update`, id); return send(res, 200, item);
  }
  if (method === 'DELETE') { list.splice(idx, 1); writeContent(content); audit(req, `${listKey}-delete`, id); return send(res, 200, { ok: true }); }
  return send(res, 405, { error: 'Method not allowed' });
}

/* ---------- static ---------- */
function serveStatic(req, res, url) {
  let pathname = decodeURIComponent(url.pathname);
  if (pathname === '/admin' || pathname === '/admin/') pathname = '/admin/index.html';
  if (pathname.endsWith('/')) pathname += 'index.html';
  const rel = path.normalize(pathname).replace(/^(\.\.[\/\\])+/, '');
  const file = path.join(ROOT, rel);
  if (!file.startsWith(ROOT)) return send(res, 403, 'Forbidden');
  const parts = rel.split(/[\\/]/).filter(Boolean);
  if (parts.some(s => s.startsWith('.')) || parts[0] === 'data' || parts[0] === 'node_modules' || parts[0] === 'server.js') return send(res, 404, 'Not found');
  fs.stat(file, (err, st) => {
    if (err || !st.isFile()) return send(res, 404, 'Not found');
    const ext = path.extname(file).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    const cache = ext === '.html' || ext === '.json' ? 'no-cache' : 'public, max-age=3600';
    const isAdminPath = rel.replace(/\\/g, '/').replace(/^\/+/, '').startsWith('admin/');
    const extra = isAdminPath ? Object.assign({ 'Content-Security-Policy': ADMIN_CSP }, SECURITY_HEADERS) : { 'Referrer-Policy': 'strict-origin-when-cross-origin' };
    res.writeHead(200, Object.assign({ 'Content-Type': type, 'Content-Length': st.size, 'Cache-Control': cache, 'X-Content-Type-Options': 'nosniff' }, extra));
    fs.createReadStream(file).pipe(res);
  });
}

http.createServer(async (req, res) => {
  // A malformed path (e.g. "//") or Host header makes new URL() throw; answer 400 instead of crashing the process.
  let url;
  try { url = new URL(req.url, 'http://localhost'); } catch { return send(res, 400, 'Bad request'); }
  try {
    if (url.pathname.startsWith('/api/')) return await api(req, res, url);
    if (url.pathname === '/data/content.json') {
      const c = readContent();
      return send(res, 200, isAdmin(req) ? c : publicView(c), { 'Cache-Control': 'no-store' });
    }
    return serveStatic(req, res, url);
  } catch (e) {
    console.error(e);
    return send(res, 500, { error: 'Server error' });
  }
}).listen(PORT, HOST, () => {
  console.log(`HouseRoot running at http://${HOST}:${PORT}/  (admin: http://${HOST}:${PORT}/admin/)`);
});
