# Indic Letters

A chart of the consonant sounds of 15 Indic languages. The chart puts each sound
where the mouth makes it: rows go from the throat to the lips, and columns show
how the air moves (plain, puff, buzz, nose, hiss and so on).

Pick your home language. Then move the slider to compare it with another
language. Each letter shows both languages side by side in eight fixed columns, one per
way the air moves. Press a letter to hear both sounds, hear it against its plain
neighbour, and see where the data comes from.

Live site: <https://micahchoo.github.io/indic-letters/>

Languages: Hindi, Marathi, Nepali, Konkani, Gujarati, Punjabi, Bengali,
Assamese, Bishnupriya Manipuri, Odia, Telugu, Kannada, Malayalam, Tamil, Sinhala.

## What a cell means

| Look | Meaning |
|---|---|
| Solid letter | The language has this sound and a letter for it. |
| Dashed outline | The language says this sound but has no letter of its own for it (Tamil *g* in அகம்). |
| Faded letter | The language has the letter, but speakers say it like another sound (Bengali ষ is said *sh*). |
| Hatched, with "2/5" | Only some descriptions of the language list this sound. Some speakers use it. |
| Coloured border | When comparing: the other language has this sound and yours does not. The chip says what you will probably hear instead. |
| **!** | The robot voice (espeak-ng) plays this letter differently from the chart. Press it to hear a real word instead. |
| ⚙ after a word | No recording of a real speaker; the robot voice reads the word. |

## Where the data comes from

- **Which sounds a language has:** [PHOIBLE 2.0](https://phoible.org). A sound
  counts when at least half of the language's descriptions list it.
- **Example words and their IPA:** Wiktionary, through
  [kaikki.org](https://kaikki.org).
- **Recordings of words:** Wikimedia Commons and Lingua Libre. Each speaker and
  license is in [credits.html](credits.html).
- **Letter sounds:** espeak-ng.
- **Checks:** Epitran reads each letter a second way. When espeak-ng disagrees
  with Epitran and PHOIBLE, the cell gets a **!**. PanPhon finds the nearest
  sound a speaker will probably hear for a sound their language lacks.

Hand corrections are marked in each cell's details. They cover Tamil ற,
Malayalam ഴ, Assamese merged sounds (Mahanta 2012), and Sinhala nose-before-stop
letters.

## Known limits

- Bishnupriya Manipuri has no PHOIBLE or Wiktionary data. Its cells come from
  espeak-ng only.
- Konkani and Sinhala words have no recordings. espeak-ng reads them.
- The slider orders languages by how many sounds they share. PHOIBLE
  descriptions differ in detail between languages, so some neighbours are
  surprising (Bengali's nearest is not Assamese).
- Vowels are not in the chart yet.

## Rebuild the data

The scripts in `build/` run from one work folder with this layout:

```
proto/        build_espeak.py output (data.json, data.js), then lang/*.json, core.js
phoible/      phoible.csv from github.com/phoible/dev, compare.py
kaikki/       <Language>.jsonl from kaikki.org, audio/ cache
```

1. `python build/build_espeak.py` — letter sounds from espeak-ng (needs `espeak-ng`, `lame`).
2. `python phoible/compare.py proto/data.json` — PHOIBLE sounds per cell.
3. `python build/epi.py` — Epitran readings (needs `epitran`).
4. Set `WIKIMEDIA_CONTACT` to your email or URL, as the
   [Wikimedia User-Agent policy](https://meta.wikimedia.org/wiki/User-Agent_policy) asks.
5. `python build/build_all.py` — cell states, words, recordings (needs `panphon`, `ffmpeg`).
   It downloads slowly and caches each recording.
6. `python build/credits.py` — speaker and license for each recording.
7. `python build/export.py <site-folder>` — writes `index.html`, `credits.html`, `core.js`, `lang/`.

## License

Code: MIT, see [LICENSE](LICENSE). Data in `lang/` and `core.js`: CC BY-SA 4.0,
because it contains material from Wiktionary and PHOIBLE. Each recording keeps
its own license, listed in [credits.html](credits.html).
