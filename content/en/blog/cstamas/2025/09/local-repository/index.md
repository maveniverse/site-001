---
title: "Maven Local Repository (I)"
date: 2025-09-16T12:34:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - LRM
projects:
  - Maven
---

{{% pageinfo color="info" %}}

The topic is about Maven Local Repository. You know, that thing that some people insist on protecting from "pollution".

{{% /pageinfo %}}

## Where to start?

Maven Local Repository, as we know it, is a mish-mash of cache and staging (locally built and installed) artifacts.
Hence, no matter how much you dislike it, it **is part of your "build context"**, as without it, you would have no build.

Then a logical followup would be something along this: maybe we should tinker about stop using **global** local 
repository, and make it **per-project** instead?

Basically, this is what you already have, when you, as a good Maven Universe citizen use Mimir: Mimir
offers **pure global cache**, and it lets you consider you local repository really just as a "local something"
(mish-mash). If you nuke your local "something", you are still not condemned for endless cups of coffee ("while Maven 
downloads the Internet"), as you still have all you need cached locally, in Mimir caches (for some deleting/nuking
their local repository may involve some separation anxiety, but they should really get over it quickly).

We cannot get rid of it in Maven 4 timeframe (due Maven 3 compatibility), but as explained above, users can already
achieve it. So, why not?
