---
title: Mímir
description: The Maven workstation and LAN cache
categories: [Documentation]
tags: [docs]
projects: [ Mimir ]
weight: 60
---

{{% pageinfo %}}
Maveniverse Mímir started as solution of my own problem: workstation hopping, and a LOT of download when picking
up where I left on.
{{% /pageinfo %}}

Mímir is a Maven 3.9+/4 core extension that adds a system-wide cache layer between Resolver and the transport. As it
sits "above" the local repository, it works regardless of where the local repository is or of its layout (enhanced,
split, etc.). The cache, by default in `~/.mimir/local`, is shared by all builds on the workstation and consulted
before going remote, which makes deleting the local repository cheap.

By default only release artifacts from Maven Central are cached, but the set of cached repositories is configurable.
Snapshots are never cached. On local caching hard links are used where possible to avoid duplicating content.

Mímir can also share caches across the LAN: a daemon discovers other Mímir nodes and serves cached content to them,
on the assumption that a LAN neighbour is faster than the real remote. It can also log every artifact resolution
(CSV or JSON Lines), recording where each artifact came from and whether it was served from cache.

Sources: https://github.com/maveniverse/mimir
