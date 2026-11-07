/* Pomocnicze funkcje ruchu i efektów wizualnych do scen HTML sterowanych czasem: window.seek(t).
   Czyste funkcje czasu t, bez timerów i bez Math.random() w pętli klatkowej.
   Źródła i inspiracje:
   - awesome-ai-motion (MIT): easingi zgodne z GSAP (power3.out, back.out, elastic.out)
   - awesome-opus5-5-videos (MIT): zamknięte sprężyny skokowe (stepSpring, springTimeline, liquidSpan)
   - unslop by Damir Sokolovsky (@heydamir, CC BY 4.0): deterministyczne traktowania obrazu (bakeGlyphAtlas, drawGlyphs, drawHalftone)
   - bang-motion by Bang Tutorial (MIT): idee rigu ujęć kamery, żywego ziarna i asymetrycznego rytmu wejść/wyjść
     (shotCamera, cameraTransform, grainOffset, enterEase/exitEase, directionalBlur), napisane od nowa jako czyste funkcje t */
const clamp01 = (x) => Math.min(1, Math.max(0, x));
/* postęp 0..1 odcinka [start, start + duration] w chwili t */
const progress = (t, start, duration) => clamp01((t - start) / duration);
const lerp = (a, b, p) => a + (b - a) * p;
const easeOut = (n = 3) => (x) => 1 - Math.pow(1 - clamp01(x), n);       /* powerN.out */
const easeIn = (n = 3) => (x) => Math.pow(clamp01(x), n);                 /* powerN.in */
const easeInOut = (n = 3) => (x) => {                                      /* powerN.inOut */
  x = clamp01(x);
  return x < 0.5 ? Math.pow(2 * x, n) / 2 : 1 - Math.pow(2 * (1 - x), n) / 2;
};
const backOut = (s = 1.70158) => (x) => { x = clamp01(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
const elasticOut = (amp = 1, period = 0.3) => (x) => {
  x = clamp01(x);
  if (x === 0 || x === 1) return x;
  const s = (period / (2 * Math.PI)) * Math.asin(1 / amp);
  return amp * Math.pow(2, -10 * x) * Math.sin(((x - s) * 2 * Math.PI) / period) + 1;
};
/* sprężyna tłumiona na odcinku [0..1]: zeta < 1 daje przeregulowanie i miękkie lądowanie */
const spring = (zeta = 0.55, omega = 9) => (x) => {
  const t = clamp01(x) * 1.2;
  const d = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * t) * (Math.cos(d * t) + (zeta * omega / d) * Math.sin(d * t));
};
/* start i-tego elementu przy stagger */
const stagger = (start, gap, i) => start + gap * i;

/* Zamknięta odpowiedź skokowa sprężyny od chwili t0 (w sekundach), czysta funkcja czasu (wzorzec twoclipping / Opus 5.5) */
const stepSpring = (t, t0, zeta = 0.72, omega = 14) => {
  const dt = t - t0;
  if (dt <= 0) return 0;
  const d = omega * Math.sqrt(Math.max(0.0001, 1 - zeta * zeta));
  return 1 - Math.exp(-zeta * omega * dt) * (Math.cos(d * dt) + (zeta * omega / d) * Math.sin(d * dt));
};

/* Wartość zmieniająca cel wielokrotnie jako suma sprężyn skokowych: keyframes = [[t0, v0], [t1, v1], ...] */
const springTimeline = (t, keyframes, zeta = 0.72, omega = 14) => {
  if (!keyframes || !keyframes.length) return 0;
  let value = keyframes[0][1];
  for (let i = 1; i < keyframes.length; i++) {
    const [ti, target] = keyframes[i];
    const prev = keyframes[i - 1][1];
    value += (target - prev) * stepSpring(t, ti, zeta, omega);
  }
  return value;
};

/* Płynny wskaźnik (liquid tab / toggle knob): prowadząca krawędź jedzie szybszą sprężyną niż tylna */
const liquidSpan = (t, keyframes, fastOmega = 18, slowOmega = 11, zeta = 0.76) => {
  const a = springTimeline(t, keyframes, zeta, fastOmega);
  const b = springTimeline(t, keyframes, zeta, slowOmega);
  return { start: Math.min(a, b), end: Math.max(a, b), center: (a + b) / 2, stretch: Math.abs(a - b) };
};

/* Deterministyczny generator pseudo-losowy dla indeksu komórki (zamiast Math.random) */
const cellHash = (x, y) => {
  const h = Math.sin(x * 127.1 + y * 311.7) * 43758.5453123;
  return h - Math.floor(h);
};

/* Zestawy znaków dziedzinowych z unslop (Damir Sokolovsky @heydamir, CC BY 4.0) */
const GLYPH_CHARSETS = {
  finance: ". : 1 7 4 0 8 $ %",
  code: ". : / { } < > = #",
  music: "c d e g a b #",
  data: ". · : | + ▪"
};

/* Pre-kompilacja obrazu do siatki glifów (wywołaj raz po załadowaniu obrazu, nigdy wewnątrz seek(t)) */
const bakeGlyphAtlas = (image, width, height, { cell = 8, chars = GLYPH_CHARSETS.data, font = "monospace" } = {}) => {
  const columns = Math.max(1, Math.floor(width / cell));
  const rows = Math.max(1, Math.floor(height / cell));
  const sample = document.createElement("canvas");
  sample.width = columns;
  sample.height = rows;
  const sampler = sample.getContext("2d", { willReadFrequently: true });
  sampler.drawImage(image, 0, 0, columns, rows);
  const pixels = sampler.getImageData(0, 0, columns, rows).data;
  const palette = [...chars].filter((c) => c !== " ");
  const cells = [];
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < columns; x++) {
      const i = (y * columns + x) * 4;
      const light = (0.2126 * pixels[i] + 0.7152 * pixels[i + 1] + 0.0722 * pixels[i + 2]) / 255;
      cells.push({
        x, y, light,
        color: `rgb(${pixels[i]},${pixels[i + 1]},${pixels[i + 2]})`,
        seed: cellHash(x, y)
      });
    }
  }
  return { cell, columns, rows, palette, font, cells };
};

/* Rysowanie siatki glifów w chwili t (deterministyczne, 8 kroków/s zgodnie z unslop/references/effects.md) */
const drawGlyphs = (ctx, baked, t = 0, { fps = 8, overrideColor = null } = {}) => {
  const step = Math.floor(t * fps);
  const { cell, palette, font, cells } = baked;
  ctx.save();
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ctx.font = `500 ${cell + 1}px ${font}`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  for (const c of cells) {
    if (c.light < 0.06) continue;
    const jitter = Math.sin(c.seed * 999 + step) > 0.92 ? 1 : 0;
    const idx = Math.min(palette.length - 1, Math.floor(c.light * palette.length) + jitter);
    ctx.fillStyle = overrideColor || c.color;
    ctx.fillText(palette[idx], c.x * cell + cell / 2, c.y * cell + cell / 2);
  }
  ctx.restore();
};

/* Rysowanie rastra półtonowego (halftone dots z unslop/references/effects.md) */
const drawHalftone = (ctx, baked, { inkColor = "#ededed" } = {}) => {
  const { cell, cells } = baked;
  ctx.save();
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);
  ctx.fillStyle = inkColor;
  for (const c of cells) {
    if (c.light < 0.05) continue;
    const r = (c.light * cell) / 2;
    ctx.beginPath();
    ctx.arc(c.x * cell + cell / 2, c.y * cell + cell / 2, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
};

/* ---------- Rig ujęć kamery: wide ↔ medium close-up ↔ close-up jako czysta funkcja t ----------
   keys: [{ t, s, x, y, ease? }] — s = skala, (x, y) = punkt ostrości w koordynatach świata.
   Między kluczami: ease z klucza docelowego (domyślnie powerN.inOut). Oddech kamery (breathe)
   to tylko warstwa bazowa; "zoom in-out" to zmiana wielkości ujęcia do elementu, który właśnie mówi. */
const shotCamera = (t, keys, { breathe = 0, breatheRate = 0.7 } = {}) => {
  let cam = { s: keys[0].s, x: keys[0].x, y: keys[0].y };
  for (let i = 1; i < keys.length; i++) {
    const a = keys[i - 1], b = keys[i];
    if (t <= b.t) {
      const p = (b.ease || easeInOut(3))(progress(t, a.t, Math.max(1e-6, b.t - a.t)));
      cam = { s: lerp(a.s, b.s, p), x: lerp(a.x, b.x, p), y: lerp(a.y, b.y, p) };
      break;
    }
    cam = { s: b.s, x: b.x, y: b.y };
  }
  cam.s *= 1 + breathe * Math.sin(t * breatheRate);
  return cam;
};

/* Przelicz kamerę na translate/scale świata W×H; krawędź świata nigdy nie wychodzi w kadr (overscan). */
const cameraTransform = (cam, width, height) => {
  const s = Math.max(1, cam.s);
  const tx = Math.min(0, Math.max(width - width * s, width / 2 - cam.x * s));
  const ty = Math.min(0, Math.max(height - height * s, height / 2 - cam.y * s));
  return { tx, ty, s, css: `translate(${tx}px, ${ty}px) scale(${s})` };
};

/* Kadr na element: skala, przy której element wypełnia `fill` kadru (close-up ~0.6, medium ~0.35). */
const frameOn = (rect, fill, width, height) => ({
  s: Math.max(1, Math.min((width * fill) / rect.w, (height * fill) / rect.h)),
  x: rect.x + rect.w / 2,
  y: rect.y + rect.h / 2,
});

/* Żywe ziarno bez losowości: przesunięcie kafla szumu skacze fps razy na sekundę, wyliczone z t. */
const grainOffset = (t, fps = 12, range = 64) => {
  const k = Math.floor(t * fps);
  const wrap = (v) => (((v % range) + range) % range) - range / 2;
  return { x: wrap(k * 37), y: wrap(k * 61) };
};

/* Asymetryczny rytm: wejście wolniej i stanowczo (0.7–1.3 s, power4.out), wyjście szybko (0.35–0.55 s, power2.in). */
const enterEase = easeOut(4);
const exitEase = easeIn(2);
const enterExit = (t, tIn, tOut, { inDur = 0.9, outDur = 0.45 } = {}) =>
  t < tOut ? enterEase(progress(t, tIn, inDur)) : 1 - exitEase(progress(t, tOut, outDur));

/* Kierunkowy motion blur dla feGaussianBlur stdDeviation="x y": rozmycie wzdłuż ruchu, nie we wszystkie strony.
   amount 0..1 (np. 1 - enterEase(p) przy wejściu); horizontal=false dla ruchu pionowego. Zdejmij filtr przy 0. */
const directionalBlur = (amount, { max = 30, horizontal = true, ratio = 0.08 } = {}) => {
  const v = clamp01(amount) * max;
  return horizontal ? `${v.toFixed(2)} ${(v * ratio).toFixed(2)}` : `${(v * ratio).toFixed(2)} ${v.toFixed(2)}`;
};
