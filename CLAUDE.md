# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A collection of small, independent Python scripts that each run as a scheduled/manual GitHub Actions workflow, using Actions as a free serverless cron runner. There is no shared application code, build system, or test suite — each script + its matching workflow file is a self-contained "task."

## Commands

There is no build/lint/test tooling in this repo. To run a script locally:

```bash
pip install -r requirements.txt
python daily_sign.py        # requires JD_COOKIE env var
python weather_report.py    # requires APP_ID, APP_SECRET, OPEN_ID, TEMPLATE_ID env vars
python love_heart.py        # local GUI only, no env vars, requires tkinter
```

## Architecture

Each feature is a pair: one top-level `*.py` script and one matching workflow under `.github/workflows/`.

- `daily_sign.py` + `.github/workflows/daily_sign.yml` — JD (京东) daily sign-in/bean-collecting request. Reads `JD_COOKIE` from env (sourced from a repo secret) and POSTs to the JD app API.
- `weather_report.py` + `.github/workflows/weather_report.yml` — fetches a forecast from the Japan Meteorological Agency (JMA) public JSON API and an hourly UV index forecast from the Open-Meteo public API for a hardcoded city (`weather_report("市川市")` in `__main__`), then pushes the result via a WeChat 公众号测试号 template message using `APP_ID`/`APP_SECRET`/`OPEN_ID`/`TEMPLATE_ID` secrets. Also fetches a "daily love quote" from an external API to fill a template field. `CITY_AREA_MAP` in `weather_report.py` maps a city to its JMA area code/region/temperature station plus lat/lon (for the UV lookup) — add an entry there to support another city. `get_uv_index` builds the UV field as a space-separated `HH时:value` string for daytime hours (6:00-18:00 JST) from Open-Meteo's hourly series. The WeChat template must include a `{{uv_index.DATA}}` placeholder for the UV field to render.
- `love_heart.py` + `.github/workflows/love_heart_{windows,ubuntu,macos}.yml` — a Tkinter animated heart GUI, built into a standalone executable per-OS via `sayyid5416/pyinstaller` (workflow_dispatch only, no scheduling; outputs an Actions artifact, not a push).

Workflow triggers:
- `daily_sign.yml` and `weather_report.yml` run on a `schedule:` cron (in addition to `workflow_dispatch`). **GitHub Actions cron is always UTC** — comments above each cron line document the intended local time; when changing the schedule, update the cron value and the comment together and re-derive the UTC offset by hand (this repo has no timezone-aware helper).
- `weather_report.yml` additionally sets `env: TZ: Asia/Tokyo` at the job level so the script's own date formatting (`datetime.date.today()`) reflects JST regardless of the runner's default UTC clock. `daily_sign.yml` does not set `TZ`.
- The `love_heart_*` workflows are `workflow_dispatch` only — they build platform-specific executables via PyInstaller and upload them as Artifacts, they don't run/schedule anything.

Secrets are all injected via repo Settings → Secrets and variables → Actions, referenced in each workflow's `env:` block for the run step. There is no `.env` or secrets file in the repo itself.
