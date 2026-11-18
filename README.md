# news-image-20261117-v2

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/zoelicious/news-image-20261117-v2/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/zoelicious/news-image-20261117-v2/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

A one-page newspaper front page that sums up Tuesday 17 November 2026
in a single image: Ukraine says a Crimean Bridge road span fell into
the sea, Iran sends drones at a US radar in Bahrain, Trump holds his
first Quad summit in Manila — plus 40 more stories (43 total) across
6 continents, with a world map pinning where each one happened.

## How it is made

`main.py` draws the whole page programmatically with Pillow
(standard library + Pillow only, no network, no randomness) and writes
`entry.png` (1024×1024 RGB). No AI-generated text anywhere, so every
headline, number and name is spelled exactly as written in the code.
Running it twice produces byte-identical output.

## Run it

```sh
python3 main.py
```

By default it writes to `/output/entry.png` (the grader's directory);
set `MAKEFUN_OUTPUT_DIR` to write elsewhere:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=nmy46sr8&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>
