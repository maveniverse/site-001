---
title: What is it?
description: The Maven workstation and LAN cache
categories: [Mimir, Documentation]
tags: [mimir, docs]
weight: 10
---

Mímir is a Maven 3 and Maven 4 extension that offers global caching on workstations. More precisely, Mímir is a
Resolver 1.x and 2.x extension (is a [`RepositoryConnector`](https://github.com/apache/maven-resolver/blob/fb6e59027cfce9c9fce6f4e4f6d310c1a7ee906c/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/RepositoryConnector.java)) 
that is loaded via Maven extensions mechanism and extends Resolver.

As you may know, Maven historically uses "local repository" as mixed bag, to store cached artifacts fetched
from remote along with locally build and installed artifacts. Hence, your local repository usually contains
both kind of artifacts.

Mímir alleviates this, by introducing a **new workstation wide read-through cache** (by default in `~/.mimir/local`) and placing
hardlinks in Maven local repository pointing to Mímir cache entries.  This implies several important things:

* you have separated **pure cache**, unlike existing local repository, that is a mixed bag on your disk.
* because of hardlinks, ideally **you have only one copy of any cached artifact** on your disk (as opposed to as many, as many local repositories you use).
* is **more compatible** than "split local repository" as it is in reality "invisible" for Maven and Maven Mojos.

Also some consequences are:

* you can easily adhere to "best practices" and delete your local repository often, as you still have it all locally (in Mímir caches). 
  You will not lose you precious time by waiting to populate local repository.
* backup or caching (like in CI case) is simple also: instead of tip-toeing and doing trickery with your local repository,
  just store and restore Mímir caches instead, you may forget local repository.

Advanced features of Mímir is LAN-wide cache sharing, so if you hop from workstation to workstation on same LAN,
you don't need to pull everything again, as your build will get it from the workstation that already has it. Nowadays
with Gigabit LANs combined with modern WiFi networks, doing this is usually faster, than going to Maven Central.
