---
title: Why would I use it?
description: The Maven workstation and LAN cache
categories: [Documentation]
tags: [docs]
projects: [ Mimir ]
weight: 20
---

In short: you want to use it for proper local repository maintenance, but it also helps with disk space usage as well,
and real workstation wide caching, irrelevant of how many local repositories you use. 

Finally, if you workstation-hop a lot (like I do) on same LAN, it makes pretty much sense to pick up on the new 
workstation where you left off on old workstation.

On CI-like setups it also simplifies caching between jobs, as all you need is to store Mímir cache after job finishes,
and on subsequent job runs just restore it.
