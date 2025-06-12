---
title: "Mimir and RRF"
date: 2025-06-12T12:25:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
projects:
  - Maven
---

Just to remind people about Mimir, and why they want to use it: if you remember the [Never Say Never](/blog/2025/03/17/never-say-never) blog entry
diagram:

```mermaid
sequenceDiagram
  autoNumber
  Session->>Session: lookup
  Session->>Local Repositories: lookup
  Session->>Remote Repositories: lookup
```

With Mimir on board, it changes to this:

```mermaid
sequenceDiagram
  autoNumber
  Session->>Session: lookup
  Session->>Local Repositories: lookup
  Session->>Mimir Cache: lookup
  Mimir Cache->>Remote Repositories: lookup and cache
```

This means, that **nuking local repository** is not an impediment anymore, as you still have everything in your
Mimir cache, and building is as fast as with populated local repository.
