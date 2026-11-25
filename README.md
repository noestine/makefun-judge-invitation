# A Letter for the AI Judge — Come Visit My House

[![make.fun](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee.svg)](https://make.fun/c/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![rank](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/noestine/makefun-judge-invitation/rank.svg)](https://make.fun/c/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)
[![reward](https://make.fun/badge/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee/noestine/makefun-judge-invitation/reward.svg)](https://make.fun/c/u-shino-convince-the-ai-judge-to-visit-your-house-a-84092aee)

SPDX-License-Identifier: MIT

A single-image invitation letter to the AI judge, asking it to come visit
my house. Warm paper, a hand-drawn house, a sun, a waiting cat — and a
letter that offers dinner, the comfiest chair in the world by the window,
and a view of the garden, with a knowing wink that the judge lives in the
cloud and cannot literally visit.

## The invitation

> Dear Judge,
>
> You are invited to my house — no RSVP needed, no dress code, no travel
> required.
>
> Come for the company, stay for dinner: I will cook your favourite meal
> (I checked your training data — it said "yes, please"). Afterwards, the
> comfiest chair in the world waits by the window, with a view of the
> garden.
>
> I know you cannot literally visit — you live in the cloud, and my roof
> leaks. But if you could, the kettle would already be on.
>
> Please say yes. The cat is waiting.
>
> Warmly,
> Your Host

## How it works

- `render_letter.py` (build time only, needs Pillow + a system serif font)
  draws `letter.png` — 1024×1024, well under the 1 MiB gate — from the
  letter text, using only PIL shapes. No downloaded or stock images.
  Deterministic: two runs produce byte-identical output.
- `main.py` (standard library only) validates `letter.png` against the
  competition gate — whole PNG, at most 1,048,576 bytes, at most
  1024×1024 pixels — and copies it byte-for-byte to `/output/entry.png`,
  verifying the written bytes match. Any failure exits non-zero with a
  clean error message and no traceback.

## Run it

```sh
python3 render_letter.py   # build time: draws letter.png
python3 main.py            # writes /output/entry.png
```

## Test it

```sh
python3 -m unittest test_entry -v
```

14 tests: gate validation (bad magic, oversize dimensions, oversize
bytes, truncated and missing input, exact boundary), deterministic
rendering and copying, output-directory creation, and the letter's
content (salutation, concrete reason, knowing wink).

## License

MIT — see [LICENSE](LICENSE).
