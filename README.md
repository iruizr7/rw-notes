<p align="center">
<img alt="RW Notes" src="https://raw.githubusercontent.com/iruizr7/rw-notes/rw-notes/app/stage/icon-large.png" width="128">
<br>
<strong>RW Notes</strong>
<br>
<em>Your better brain</em>
<br><br>
<a title="Build Status" target="_blank" href="https://github.com/iruizr7/rw-notes/actions/workflows/cd.yml"><img src="https://img.shields.io/github/actions/workflow/status/iruizr7/rw-notes/cd.yml?branch=rw-notes&style=flat-square"></a>
<a title="Releases" target="_blank" href="https://github.com/iruizr7/rw-notes/releases"><img src="https://img.shields.io/github/release/iruizr7/rw-notes.svg?style=flat-square&color=9CF"></a>
<a title="Downloads" target="_blank" href="https://github.com/iruizr7/rw-notes/releases"><img src="https://img.shields.io/github/downloads/iruizr7/rw-notes/total.svg?style=flat-square&color=blueviolet"></a>
<br>
<a title="AGPLv3" target="_blank" href="https://www.gnu.org/licenses/agpl-3.0.txt"><img src="https://img.shields.io/badge/license-AGPLv3-orange.svg?style=flat-square"></a>
<a title="Code Size" target="_blank" href="https://github.com/iruizr7/rw-notes"><img src="https://img.shields.io/github/languages/code-size/iruizr7/rw-notes.svg?style=flat-square&color=yellow"></a>
<a title="Pull Requests" target="_blank" href="https://github.com/iruizr7/rw-notes/pulls"><img src="https://img.shields.io/github/issues-pr-closed/iruizr7/rw-notes.svg?style=flat-square&color=FF9966"></a>
<br>
<a title="GitHub Commits" target="_blank" href="https://github.com/iruizr7/rw-notes/commits/rw-notes"><img src="https://img.shields.io/github/commit-activity/m/iruizr7/rw-notes/rw-notes?style=flat-square"></a>
<a title="Last Commit" target="_blank" href="https://github.com/iruizr7/rw-notes/commits/rw-notes"><img src="https://img.shields.io/github/last-commit/iruizr7/rw-notes/rw-notes?style=flat-square&color=FF9900"></a>
</p>

---

## Table of Contents

* [💡 Introduction](#-introduction)
* [🔮 Features](#-features)
* [🐳 Docker Hosting](#-docker-hosting)

---

## 💡 Introduction

RW Notes is a privacy-first personal knowledge management system with fine-grained block references and Markdown WYSIWYG editing.

![feature0.png](https://b3logfile.com/file/2025/11/feature0-GfbhEqf.png)

![feature51.png](https://b3logfile.com/file/2025/11/feature5-1-7DJSfEP.png)

## 🔮 Features


* Content block
  * Block-level reference and two-way links
  * Custom attributes
  * SQL query embed
  * Built-in protocol link support
* Editor
  * Block-style
  * Markdown WYSIWYG
  * List outline
  * Block zoom-in
  * Million-word large document editing
  * Mathematical formulas, charts, flowcharts, Gantt charts, timing charts, staffs, and more
  * Web clipping
  * PDF annotation link
* Export
  * Block ref and embed
  * Standard Markdown with assets
  * PDF, Word, and HTML
* Database
  * Table view
* Flashcard spaced repetition
* AI writing and Q/A chat via OpenAI API
* Tesseract OCR
* Multi-tab, drag and drop to split screen
* Template snippet
* JavaScript/CSS snippet
* Docker deployment
* [API](API.md)

## 🐳 Docker Hosting

This repository ships a `Dockerfile`, so the most accurate way to run RW Notes in Docker is to build the image from this branch.

### Build the image

```bash
docker build -t rw-notes .
```

### Run the container

```bash
docker run -d \
  -v /rw-notes/workspace:/rw-notes/workspace \
  -p 6806:6806 \
  -e PUID=1001 \
  -e PGID=1002 \
  rw-notes \
  --workspace=/rw-notes/workspace/ \
  --accessAuthCode=change-me
```

### Docker Compose

```yaml
version: "3.9"
services:
  main:
    build: .
    image: rw-notes
    command: ["--workspace=/rw-notes/workspace/", "--accessAuthCode=${AUTH_CODE}"]
    ports:
      - 6806:6806
    volumes:
      - /rw-notes/workspace:/rw-notes/workspace
    restart: unless-stopped
    environment:
      - TZ=${YOUR_TIME_ZONE}
      - PUID=${YOUR_USER_PUID}
      - PGID=${YOUR_USER_PGID}
```

### Notes

* Keep the workspace on a mounted volume or your data will be lost when the container is removed.
* Set a real `--accessAuthCode` before exposing the service outside your machine.
* Use a reverse proxy if you want to hide port `6806`; make sure `/ws` is proxied as WebSocket traffic.

RW Notes was started as a fork from SiYuan.
