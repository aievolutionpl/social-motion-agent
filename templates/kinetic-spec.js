// Edit this brief-specific composition, then render again. Everything is in beats.
import { Words, Chain, Logo } from './blocks.js';
const beats = __BEATS__;
export default {
  title: __TITLE__, bpm: 128, beats, fps: 60, hud: false,
  palette: { bg: '#101215', paper: '#F5F2EB', accent: '#FF643D', hot: '#FF3C19', ink: '#141416' },
  sounds: {}, cues: [], captions: [],
  scenes: [
    [Words, 0, beats * .25, { shots: [
      { at: beats * .015, style: 'punch3d', text: 'TWÓJ POMYSŁ', fx: 'punch' },
      { at: beats * .08, style: 'slam', text: 'TWÓJ FILM', ground: 'accent', fx: 'hit' },
      { at: beats * .16, style: 'pair', text: ['OPISZ', 'REZULTAT.'], ground: 'paper', fx: 'punch' },
    ] }],
    [Chain, beats * .25, beats * .8, { nodes: [['BRIEF', 'Cel i odbiorca'], ['SCENY', 'Jedna myśl w każdym ujęciu'], ['FILM', 'Render i recenzja', 'accent']] }],
    [Logo, beats * .8, beats, { wordmark: 'TWÓJ PRODUKT', tagline: 'Uzupełnij prawdziwą obietnicę.', small: 'Uzupełnij właściwe CTA.' }],
  ],
};
