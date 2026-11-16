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
const SESSION_DAYS = 7;
const MAX_BODY = 8 * 1024 * 1024;

const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.svg': 'image/svg+xml', '.gif': 'image/gif', '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8',
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
  const initial = process.env.ADMIN_PASSWORD || 'houseroot123';
  admin = hashPassword(initial);
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
  res.writeHead(code, Object.assign({ 'Content-Type': isObj ? 'application/json; charset=utf-8' : 'text/plain; charset=utf-8', 'X-Content-Type-Options': 'nosniff' }, headers));
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
const attempts = new Map();
function tooManyAttempts(ip) {
  const a = attempts.get(ip); if (!a) return false;
  if (Date.now() - a.first > 15 * 60 * 1000) { attempts.delete(ip); return false; }
  return a.count >= 6;
}
function noteFailure(ip) {
  const a = attempts.get(ip) || { first: Date.now(), count: 0 };
  a.count++; attempts.set(ip, a);
}

/* ---------- API ---------- */
async function api(req, res, url) {
  const p = url.pathname;
  const method = req.method;
  const mutating = method !== 'GET';
  if (mutating && req.headers['x-requested-with'] !== 'HouseRootAdmin') return send(res, 403, { error: 'Missing request header' });

  if (p === '/api/login' && method === 'POST') {
    const ip = req.socket.remoteAddress;
    if (tooManyAttempts(ip)) return send(res, 429, { error: 'Too many attempts. Try again in 15 minutes.' });
    const body = await readJson(req);
    if (!checkPassword(String(body.password || ''))) { noteFailure(ip); return send(res, 401, { error: 'Wrong password' }); }
    attempts.delete(ip);
    const token = sign({ exp: Date.now() + SESSION_DAYS * 864e5, r: crypto.randomBytes(6).toString('hex') });
    return send(res, 200, { ok: true }, { 'Set-Cookie': `${COOKIE}=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${SESSION_DAYS * 86400}` });
  }
  if (p === '/api/logout' && method === 'POST') return send(res, 200, { ok: true }, { 'Set-Cookie': `${COOKIE}=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0` });
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
    writeContent(content); return send(res, 200, content.settings);
  }
  if (resource === 'password' && method === 'POST') {
    const b = await readJson(req);
    if (!checkPassword(String(b.current || ''))) return send(res, 400, { error: 'Current password is wrong' });
    if (String(b.next || '').length < 8) return send(res, 400, { error: 'New password must be at least 8 characters' });
    admin = hashPassword(String(b.next)); fs.writeFileSync(ADMIN_FILE, JSON.stringify(admin), { mode: 0o600 });
    return send(res, 200, { ok: true });
  }
  if (resource === 'upload' && method === 'POST') {
    const b = await readJson(req);
    const ext = path.extname(String(b.name || '')).toLowerCase();
    if (!['.jpg', '.jpeg', '.png', '.webp', '.gif', '.pdf'].includes(ext)) return send(res, 400, { error: 'Only jpg, png, webp, gif or pdf' });
    const buf = Buffer.from(String(b.data || '').replace(/^data:[^;]+;base64,/, ''), 'base64');
    if (!buf.length || buf.length > 6 * 1024 * 1024) return send(res, 400, { error: 'File is empty or over 6 MB' });
    const name = `${Date.now().toString(36)}-${crypto.randomBytes(3).toString('hex')}${ext}`;
    fs.writeFileSync(path.join(UPLOAD_DIR, name), buf);
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
    list.unshift(item); writeContent(content); return send(res, 201, item);
  }
  const idx = list.findIndex(x => x.id === id);
  if (idx < 0) return send(res, 404, { error: 'Not found' });
  if (method === 'PUT') {
    const b = await readJson(req);
    const item = clean(b, list[idx]); item.id = id; item.slug = uniqueSlug(list, item.slug, id);
    list[idx] = item; writeContent(content); return send(res, 200, item);
  }
  if (method === 'DELETE') { list.splice(idx, 1); writeContent(content); return send(res, 200, { ok: true }); }
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
    res.writeHead(200, { 'Content-Type': type, 'Content-Length': st.size, 'Cache-Control': cache, 'X-Content-Type-Options': 'nosniff' });
    fs.createReadStream(file).pipe(res);
  });
}

http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
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
