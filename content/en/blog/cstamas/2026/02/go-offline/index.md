---
title: "Goal go-offline must go"
date: 2026-02-03T10:55:53+01:00
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

The Maven [`go-offline`](https://maven.apache.org/plugins/maven-dependency-plugin/go-offline-mojo.html) goal is inherently bad, and will try explain it why.
For related discussion, see [this issue](https://github.com/apache/maven-dependency-plugin/issues/1405).

## Maven 4 is not Maven 2

The history of this goal predates many Maven version, and it appeared around Maven 1 or Maven 2. People simply wanted
to "go offline" (fx while traveling, those were the 2000s!) and pre-populate their local repository with required
artifacts cached.

But, as I tried to explain my several previous articles (see [Local repository](/blog/2025/11/09/maven-local-repository/)),
in Maven 2 and before, local repository was really just a "bunch of files". This is not true since Maven 3.0 released in
2010!

The "enhanced" Local Repository Manager (LRM) introduced in Maven 3.0 helps you by doing "origin tracking", that fixes one
of the biggest source of confusion with Maven 2.0: when your build became dependent on state (and content) of your 
local repository. It was the most common source of "it works for me!" issues. And it was most commonly sorted out by
**nuking (deleting) given local repository**.

As mentioned many times, in Maven 4, that must provide Maven 3 backward compatibility, we still cannot fully rework LRM.
We provided Split Local Repository feature, that is almost doing it right, but it proved too invasive and is not always
usable for any use case.

I still stand even today, that goals like `go-offline` must go away, as due all these reasons above, must always be
executed in the context of the project "going offline", but also as it is really windmill battle.

On the other hand, use case like "hermetic builds", while they seem related to this goal, IMHO can and should be
solved differently, but more about it later!