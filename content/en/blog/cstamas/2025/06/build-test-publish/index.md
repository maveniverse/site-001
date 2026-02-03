---
title: "build != testing != publishing"
date: 2025-06-01T12:15:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - CI
  - publish
projects:
  - Maven
---

{{% pageinfo color="info" %}}

This article represents my own stance, and should not be taken as any kind of "rule".

{{% /pageinfo %}}


# build != testing != publishing

People tend to go for simplest solutions, and that is okay. Still, that is many times not quite feasible.

As an awkward example, that is completely viable: you may want to use Maven 4.0.x to build a Maven 3 plugin (why not?). But this is raising several questions, one of them is how to test the built plugin? Assuming you want to support Maven 3 with built plugin, it has to be Java 8 level. Using Maven 4 to run directly ITs for Java 8 is not doable, as Maven 4 requires Java 17 at runtime.

If you go for "simplest" way, by throwing matrix onto `./mvnw clean install -P run-its` this will not allow you give full Java coverage. In other words, if you do this, it **implies that your whole stack must be capable to work in your whole test matrix** (like Java 8 or older and ancient Maven versions like 3.6), and this is many times not the case).

This was simple while Java was "slow", and it was mostly about Java 7 or 8, but today, when Maven 3 specifies Java 8 baseline, but current LTS is soon Java 25, the envelope is stretching far too broader than before.

This also may imply that "good old" way of doing things, like just stick something to parent POM that building, testing or publishing (but only one of them) requires, may not work anymore.

For me, typical set is like:
* build with "latest LTS": that is as at the time this is written: Java 21 LTS and Maven 3.9 (latest patch release, 3.9.9)
* test with "wide" matrix, if needed, and it may go from Java 8 all way up to Java 24, same with Maven, test may want to pull in old Maven as 3.6.3 is.
* publish to some service that is usually not controlled by you (typical example: publishing to Central)

As one can see, "build", "test" and "publishing" poses wildly different requirements. Expecting that **whole your stack fits the widest (test) matrix is just unreal**.

