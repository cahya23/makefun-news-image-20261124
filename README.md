# The World Today — 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/cahya23/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/cahya23/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A one-page newspaper front page summing up world news on Tuesday, 24 November 2026.

## What the image shows

Masthead **THE WORLD TODAY**, dated Tuesday, 24 November 2026, above a lead
story on Nvidia's surge as Jensen Huang returns as chief, with a drawn
chart of the jump, and smaller stories on Ukraine, Vietnam, the Pacific,
Iraq, Myanmar and the ICC. Everything is drawn from scratch with Python's
standard library only — a hand-made 5x7 bitmap font and a hand-written PNG
encoder — no photographs or copied images.

## The stories

1. **HUANG IS BACK AND THE AI TRADE ROARS** — Nvidia jumps 31.5% after
   Jensen Huang returns as chief, the biggest one-day gain in 23 years.
   Asia follows: Nikkei up 4.5%, Seoul up 7.5%, Taiwan up 9.1%.
   (Reuters, 24 Nov 2026.)
2. **ZAPORIZHZHIA STRIKE KILLS 2, HURTS 22** — A Russian attack overnight
   killed two and wounded 22, among them two children, officials said.
   (Reuters, 24 Nov 2026.)
3. **BLAST IN HANOI KILLS 6** — An explosion at a food shop in a crowded
   street killed six and injured ten, police said. (Reuters, 24 Nov 2026.)
4. **SOLOMONS TO DROP CHINA PACT** — The Solomon Islands will end its 2022
   security pact with China and sign a treaty with Australia on Wednesday.
   (Reuters, 24 Nov 2026.)
5. **BAGHDAD TAKES OVER KURD BORDER POSTS** — The prime minister ordered
   federal control of crossings after an oil-smuggling inquiry.
   (Reuters, 24 Nov 2026.)
6. **AFTER GENOCIDE RULING, REFUGEE TALKS GO ON** — Malaysia will keep
   working with Myanmar on Rohingya returns after the world court's
   genocide ruling. (Reuters, 24 Nov 2026.)
7. **JAPAN PAYS ICC EARLY AS SANCTIONS BITE** — Tokyo will pay its full
   2027 share by year-end. Japan is the court's biggest funder.
   (Reuters, 24 Nov 2026.)
8. **ALSO TODAY** — Amnesty seeks a war-crimes probe over Tigray shelling;
   Hasina plans a return to Dhaka on 16 Dec; 11 killed in a UAE bus crash;
   Canada and Qatar sign a pact. (Reuters, 24 Nov 2026.)

## Build

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` paints the page pixel by pixel and encodes the PNG by hand with
`zlib` and `struct`. It reads no files, uses no network and no randomness,
so two runs write identical bytes.
