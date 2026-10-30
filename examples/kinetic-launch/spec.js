import { Words, Prompt, Chain, Fly, Logo } from './blocks.js';

// Continuous beat-timed camera travel keeps the type alive between its entrances.
// These film-specific blocks extend the supplied engine; no upstream block is changed.
class MovingWords extends Words {
  cam(t) {
    const c = super.cam(t), phase = (t - this.t0) * 128 / 60 * Math.PI;
    return { ...c, x: (c.x || 0) + 110 * Math.sin(phase), y: (c.y || 0) + 65 * Math.cos(phase),
      s: c.s * .9, r: (c.r || 0) + .6 * Math.sin(phase) };
  }
}
class MovingPrompt extends Prompt {
  cam(t) {
    const c = super.cam(t), phase = (t - this.t0) * 128 / 60 * Math.PI;
    return { ...c, x: (c.x || 0) + 75 * Math.sin(phase), y: (c.y || 0) + 45 * Math.cos(phase) };
  }
}

export default {
  title: 'Social Motion Agent',
  bpm: 128, beats: 64, fps: 60,
  palette: { bg: '#101215', paper: '#F5F2EB', accent: '#FF643D', hot: '#FF3C19', ink: '#141416' },
  hud: false,
  logo: 'title.svg',
  music: { file: 'audio/mix.wav', offset: 0, gain: 0, stopBeat: 54 + 10 / 11 },
  sounds: {}, cues: [],
  scenes: [
    [MovingWords, 0, 8, { charge: true, shots: [
      { at: .6, style: 'punch3d', text: 'POMYSŁ.', fx: 'punch' },
      { at: 2, style: 'slam', text: 'BRIEF.', ground: 'accent', fx: 'hit' },
      { at: 3.5, style: 'pair', text: ['A POTEM?', 'CAŁY FILM.'], ground: 'paper', in: 'whipX', second: .7, fx: 'punch' },
      { at: 6, style: 'cut', text: 'ZOBACZ JAK.', ground: 'bg', color: 'paper', size: 280, rot: -3, fx: 'beat' },
    ], whipOut: [0, 1200, .15] }],
    [MovingPrompt, 8, 16, {
      label: 'TWÓJ BRIEF', unit: 'ZNAKÓW', doodles: false,
      text: [['Zrób '], ['film.', 1], [' '], ['30 sekund.', 1]],
    }],
    [MovingWords, 16, 28, { shots: [
      { at: 16, style: 'slam', text: 'RESEARCH.', ground: 'accent', fx: 'punch' },
      { at: 17.5, style: 'cut', text: 'STORYBOARD.', ground: 'paper', size: 220, rot: 2, fx: 'beat' },
      { at: 19, style: 'slam', text: 'MATERIAŁY.', ground: 'bg', fx: 'hit', in: 'whipXr' },
      { at: 20.5, style: 'cut', text: 'TEKST.', ground: 'paper', size: 330, rot: 2, fx: 'beat' },
      { at: 22, style: 'cut', text: 'ANIMACJA.', ground: 'accent', size: 280, rot: -3, fx: 'beat' },
      { at: 23.5, style: 'pair', text: ['DO', 'RYTMU.'], ground: 'paper', second: .45, fx: 'punch' },
      { at: 25, style: 'slam', text: 'RENDER.', ground: 'bg', fx: 'hit' },
      { at: 26.5, style: 'cut', text: 'KONTROLA.', ground: 'accent', size: 260, rot: -2, fx: 'beat' },
    ], whipOut: [-1600, 0, .14] }],
    [Chain, 28, 40, { nodes: [
      ['BRIEF', 'cel · odbiorca · format'],
      ['SCENY', 'tekst · obraz · rytm'],
      ['FILM', 'render · oględziny · odsłuch', 'accent'],
    ] }],
    [Fly, 40, 47, { words: [['TEKST', 'paper'], ['KAMERA', 'accent'], ['RUCH.', 'paper']] }],
    [MovingWords, 47, 54, { shots: [
      { at: 47.1, style: 'cut', text: 'OBRAZ.', size: 380, ground: 'paper', rot: -2, fx: 'beat' },
      { at: 48.6, style: 'cut', text: 'DŹWIĘK.', size: 335, ground: 'accent', rot: 3, fx: 'beat' },
      { at: 50.1, style: 'slam', text: 'KOREKTA.', ground: 'bg', fx: 'hit' },
      { at: 51.6, style: 'split', text: ['NAJPIERW', 'SPRAWDŹ.'], ground: 'paper', second: .5, fx: 'punch' },
    ], exit: { type: 'collapse', at: 53.3, end: 54 } }],
    [Logo, 54, 64, { width: 1240, y: 425,
      tagline: 'Od briefu do sprawdzonego filmu.',
      small: 'github.com/aievolutionpl/social-motion-agent',
    }],
  ],
  captions: [],
};
