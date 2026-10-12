# Turkmenistan — legislation as Markdown (LawCodex)

Legislation of Turkmenistan (Türkmenistan) as Markdown, in Turkmen (`tk/`, state language) and
Russian (`ru/`). Part of [LawCodex](https://github.com/LawCodex).

Retrieved: **2026-10-12**.

## Coverage

| Path | Contents | Files |
|---|---|---:|
| `tk/kodeksler/` | Codes (Turkmen) | 22 |
| `tk/kanunlar/<year>/` | Laws (Turkmen), 1990–2026 | 371 |
| `tk/konstitusion-kanunlar/` | Constitutional law of 14.09.2016 approving the new edition of the Constitution | 1 |
| `ru/kodeksy/` | Codes (Russian) | 22 |
| `ru/zakony/<year>/` | Laws (Russian) | 371 |
| `ru/konstitutsionnye-zakony/` | Constitutional law of 14.09.2016 (Russian) | 1 |
| `ru/konstitutsiya/` | Constitution, 2016 edition, and the 2020 amending constitutional law (Russian) | 2 |
| **Total** | | **790** |

* **Codes** — all codes published by the Mejlis (Parliament) on its website, in both languages.
* **Laws** — every law listed in the "Kanunlar / Законы" section of the Mejlis website (371 entries,
  1990–2026, including ratification laws and budget laws), in both languages.
  Texts are the versions published by the Mejlis; most codes and older laws are given "with the
  amendments and additions introduced by" later laws (consolidated), which is stated at the top of
  each text. The site does not flag repealed acts, so `status` is `unknown`.
* **Constitution** — the Mejlis site only publishes the 2016 *constitutional law* approving the new
  edition (included under `konstitusion-kanunlar/`). The text of the Constitution itself comes from the
  official government portal turkmenistan.gov.tm (Russian only): the 2016 edition and the
  Constitutional Law of 25 September 2020 amending it are in `ru/konstitutsiya/`.

## Not covered / gaps

* The Turkmen text of the Constitution, and a consolidated text including the 2020 and 2023
  amendments (the government portal only shows the 2016 edition; the 2023 amending law was not found
  on an official open page).
* Resolutions of the Mejlis (`mejlis-decrees`), presidential decrees and resolutions, and
  ministerial orders. The Ministry of Justice's registry of normative acts ("Adalat" EMTP,
  https://law.minjust.gov.tm) requires a login with a Turkmen phone number, so it was not used.

## Sources

* Mejlis of Turkmenistan — https://mejlis.gov.tm (`/codes`, `/laws`, `/constitutional-law`; lists via
  the site's own `?ajax=true` JSON endpoints, texts from `/single-code/<id>` and `/single-law/<id>`,
  `lang=tm` and `lang=ru`).
* "Türkmenistan: Altyn asyr" government portal — https://turkmenistan.gov.tm (Constitution, Russian).

Official texts are not protected by copyright in Turkmenistan: the Law of Turkmenistan on Copyright
and Related Rights excludes official documents (laws, court decisions and other texts of a
legislative, administrative and judicial character, and their official translations) from
protection.

## Structure

```
tk/kodeksler/<slug>-<id>.md                 codes (Turkmen)
tk/kanunlar/<year>/<slug>-<id>.md           laws (Turkmen), by date shown on the Mejlis site
tk/konstitusion-kanunlar/                   constitutional law (2016)
ru/kodeksy/  ru/zakony/<year>/  ru/konstitutsionnye-zakony/   the same, Russian
ru/konstitutsiya/                           Constitution (2016 edition) + 2020 amending law
scripts/                                    fetch + convert code
```

`<id>` is the Mejlis website id of the document. Headings follow the act structure
(bölüm / bap / madda — раздел / глава / статья).

## Regenerate

```
python3 -m pip install -r scripts/requirements.txt
python3 scripts/tm_fetch.py          # downloads to ../_raw/tm/ (outside the repo)
python3 scripts/tm_convert.py
python3 scripts/tm_constitution.py
```
