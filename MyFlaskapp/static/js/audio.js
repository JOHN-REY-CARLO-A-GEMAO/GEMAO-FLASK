const AudioManager = (() => {
  let ctx;
  let masterGain;
  let categoryGains = {};
  let ambientOsc;
  let ambientGain;
  let ambientAudio;
  let ambientNode;
  let ambientBufferSource;
  let ambientTrackGain;
  let ready = false;
  let muted = false;
  const categories = ["ui", "notification", "ambient", "game"];
  function updateStatus(text) {
    const el = document.getElementById('audio-status');
    if (el) el.textContent = text;
  }
  function defaultVolume(cat) {
    if (cat === 'ambient') return 0.5;
    if (cat === 'ui' || cat === 'notification' || cat === 'game') return 0.7;
    return 0.5;
  }
  function ensure() {
    if (ready) return;
    try {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      masterGain = ctx.createGain();
      masterGain.gain.value = getStoredVolume("master", 0.4);
      masterGain.connect(ctx.destination);
      categories.forEach((c) => {
        const g = ctx.createGain();
        g.gain.value = getStoredVolume(c, defaultVolume(c));
        g.connect(masterGain);
        categoryGains[c] = g;
      });
      ambientGain = categoryGains["ambient"];
      const src = typeof window !== 'undefined' ? window._AmbientAudioUrl : undefined;
      if (src) initAmbientFromSrc(src);
      ready = true;
    } catch (e) {}
  }
  function getStoredVolume(key, def) {
    try {
      const v = localStorage.getItem(`audio.vol.${key}`);
      if (v === null) return def;
      const n = parseFloat(v);
      if (Number.isFinite(n)) return Math.max(0, Math.min(1, n));
    } catch (e) {}
    return def;
  }
  function storeVolume(key, val) {
    try {
      localStorage.setItem(`audio.vol.${key}`, String(val));
    } catch (e) {}
  }
  function blip(freq, dur, cat) {
    ensure();
    if (!ready) return;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = "sine";
    osc.frequency.value = freq;
    g.gain.setValueAtTime(0, ctx.currentTime);
    g.gain.linearRampToValueAtTime(0.2, ctx.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
    osc.connect(g);
    g.connect(categoryGains[cat] || masterGain);
    osc.start();
    osc.stop(ctx.currentTime + dur);
  }
  function chime(notes, cat) {
    ensure();
    if (!ready) return;
    const now = ctx.currentTime;
    notes.forEach((n, i) => {
      const t = now + i * 0.12;
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.type = "triangle";
      osc.frequency.value = n;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.25, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.25);
      osc.connect(g);
      g.connect(categoryGains[cat] || masterGain);
      osc.start(t);
      osc.stop(t + 0.3);
    });
  }
  async function initAmbientFromSrc(src) {
    try {
      updateStatus('Loading');
      const res = await fetch(src, { cache: 'force-cache' });
      const buf = await res.arrayBuffer();
      const audioBuf = await ctx.decodeAudioData(buf);
      const trackGain = ctx.createGain();
      trackGain.gain.setValueAtTime(0, ctx.currentTime);
      ambientTrackGain = trackGain;
      ambientBufferSource = ctx.createBufferSource();
      ambientBufferSource.buffer = audioBuf;
      ambientBufferSource.loop = true;
      ambientBufferSource.connect(trackGain);
      trackGain.connect(ambientGain || masterGain);
      const title = typeof window !== 'undefined' && window._AmbientAudioTitle ? window._AmbientAudioTitle : 'Ambient';
      crossfadeStart(() => {
        ambientBufferSource.start();
      }, title);
    } catch (err) {
      try {
        ambientAudio = new Audio(src);
        ambientAudio.loop = true;
        ambientAudio.preload = 'auto';
        ambientAudio.crossOrigin = 'anonymous';
        ambientNode = ctx.createMediaElementSource(ambientAudio);
        const trackGain = ctx.createGain();
        trackGain.gain.setValueAtTime(0, ctx.currentTime);
        ambientTrackGain = trackGain;
        ambientNode.connect(trackGain);
        trackGain.connect(ambientGain || masterGain);
        ambientAudio.addEventListener('canplay', () => { updateStatus('Ready'); });
        ambientAudio.addEventListener('canplaythrough', () => { updateStatus('Loaded'); });
        ambientAudio.addEventListener('waiting', () => { updateStatus('Buffering'); });
        ambientAudio.addEventListener('error', () => { updateStatus('Unavailable'); });
        const title = typeof window !== 'undefined' && window._AmbientAudioTitle ? window._AmbientAudioTitle : 'Ambient';
        crossfadeStart(() => {
          const p = ambientAudio.play();
          if (p && typeof p.then === 'function') p.catch(() => {});
        }, title);
      } catch (e) {
        updateStatus('Unavailable');
      }
    }
  }
  function crossfadeStart(startFn, title) {
    try { if (ctx && ctx.state === 'suspended') ctx.resume(); } catch (e) {}
    const now = ctx.currentTime;
    const fadeDur = 0.8;
    if (ambientTrackGain) {
      ambientTrackGain.gain.cancelScheduledValues(now);
      ambientTrackGain.gain.setValueAtTime(0, now);
      ambientTrackGain.gain.linearRampToValueAtTime(getStoredVolume('ambient', 0.5), now + fadeDur);
    }
    if (ambientOsc) {
      const og = ctx.createGain();
      og.gain.value = 0.1;
      ambientOsc.disconnect();
      ambientOsc.connect(og);
      og.connect(ambientGain || masterGain);
      og.gain.setValueAtTime(0.1, now);
      og.gain.linearRampToValueAtTime(0, now + fadeDur);
      setTimeout(() => { try { ambientOsc.stop(); } catch (e) {} ambientOsc = null; }, fadeDur * 1000);
    }
    updateStatus((title ? title + ' · ' : '') + 'Playing');
    try { startFn(); } catch (e) {}
  }
  function startAmbient() {
    ensure();
    if (!ready) return;
    if (ambientAudio) {
      const p = ambientAudio.play();
      if (p && typeof p.then === 'function') { p.catch(() => {}); }
      return;
    }
    if (ambientBufferSource) {
      try { ambientBufferSource.start(); } catch (e) {}
      return;
    }
    if (ambientOsc) return;
    ambientOsc = ctx.createOscillator();
    ambientOsc.type = "sine";
    ambientOsc.frequency.value = 110;
    const lfo = ctx.createOscillator();
    lfo.type = "sine";
    lfo.frequency.value = 0.1;
    const lfoGain = ctx.createGain();
    lfoGain.gain.value = 30;
    lfo.connect(lfoGain);
    lfoGain.connect(ambientOsc.frequency);
    const g = ctx.createGain();
    g.gain.value = 0.1;
    ambientOsc.connect(g);
    g.connect(ambientGain || masterGain);
    lfo.start();
    ambientOsc.start();
  }
  function stopAmbient() {
    if (ambientAudio) { try { ambientAudio.pause(); } catch (e) {} }
    if (ambientBufferSource) { try { ambientBufferSource.stop(); } catch (e) {} ambientBufferSource = null; }
    if (ambientOsc) {
      try { ambientOsc.stop(); } catch (e) {}
      ambientOsc = null;
    }
  }
  function setMuted(m) {
    ensure();
    if (!ready) return;
    muted = !!m;
    masterGain.gain.value = muted ? 0 : getStoredVolume("master", masterGain.gain.value);
    if (ambientAudio) ambientAudio.muted = muted;
    try { localStorage.setItem('audio.muted', String(muted)); } catch (e) {}
  }
  function getMuted() {
    try { return localStorage.getItem('audio.muted') === 'true'; } catch (e) { return false; }
  }
  function setMasterVolume(v) {
    ensure();
    if (!ready) return;
    const vol = Math.max(0, Math.min(1, v));
    masterGain.gain.value = vol;
    storeVolume("master", vol);
  }
  function setCategoryVolume(cat, v) {
    ensure();
    if (!ready) return;
    const vol = Math.max(0, Math.min(1, v));
    const g = categoryGains[cat];
    if (g) g.gain.value = vol;
    storeVolume(cat, vol);
  }
  function playClick() { blip(440, 0.08, "ui"); }
  function playNav() { blip(320, 0.12, "ui"); }
  function playNotification() { chime([523.25, 659.25, 783.99], "notification"); }
  function hookUI() {
    ensure();
    if (!ready) return;
    document.addEventListener("click", (e) => {
      const t = e.target;
      if (!t) return;
      if (t.closest(".btn") || t.closest("button")) playClick();
      if (t.closest(".nav-link")) playNav();
    });
    const alerts = document.querySelectorAll(".alert");
    if (alerts.length) playNotification();
  }
  function init() {
    ensure();
    hookUI();
    const resume = async () => {
      try { if (ctx && ctx.state === 'suspended') await ctx.resume(); } catch (e) {}
      startAmbient();
      document.removeEventListener('click', resume, true);
      document.removeEventListener('touchstart', resume, true);
    };
    document.addEventListener('click', resume, true);
    document.addEventListener('touchstart', resume, true);
    const m = getMuted();
    if (m) setMuted(true);
  }
  return { init, startAmbient, stopAmbient, setMasterVolume, setCategoryVolume, playClick, playNav, playNotification, setMuted, getMuted };
})();

window.AudioManager = AudioManager;
