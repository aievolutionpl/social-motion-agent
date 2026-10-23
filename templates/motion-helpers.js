/* Pomocnicze funkcje ruchu do scen HTML sterowanych czasem: window.seek(t).
   Czyste funkcje, bez timerów i losowości. Nazwy zgodne z easingami z katalogu awesome-ai-motion
   (power3.out, back.out, elastic.out), więc kartę efektu da się przetłumaczyć wprost. */
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
/* sprężyna tłumiona: zeta < 1 daje przeregulowanie i miękkie lądowanie */
const spring = (zeta = 0.55, omega = 9) => (x) => {
  const t = clamp01(x) * 1.2;
  const d = omega * Math.sqrt(1 - zeta * zeta);
  return 1 - Math.exp(-zeta * omega * t) * (Math.cos(d * t) + (zeta * omega / d) * Math.sin(d * t));
};
/* start i-tego elementu przy stagger */
const stagger = (start, gap, i) => start + gap * i;
