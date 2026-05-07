---
title: "Nisse got Gradle plugin!"
date: 2026-05-07T11:01:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
  - nisse
  - gradle
projects:
  - Nisse
---

Reusable (minimal-dependency) "core", and thin (no logic, just config) Mojos around, is how things should be done. 
This is how Nisse was done as well among others, and is now the first Maveniverse project, that receives 
"equally capable" Gradle plugin, next to existing Maven one.

Check out the project: https://github.com/maveniverse/nisse

But, is also the first project, that uses new Maveniverse ToolRunner to integrate Gradle build into Maven build. 
Why not Gradle Wrapper and exec plugin? Because, ToolRunner not only executes the tool (Gradle in this case), but 
also is capable to detect it, and provision it. And unlike with Gradle Wrapper, provisioning happens via Maven/MIMA 
configured HTTP client, hence all the transport config, like proxies and authentication and all are applied 
**from Maven** configuration. **Maven drives the process**, from beginning to end 
(well, not -- yet -- the Gradle build process itself, but what if...).

Check out ToolRunner: https://github.com/maveniverse/toolrunner

Initial release supported tools are Ant (no latest discovery, wired in 1.10.17 as latest), Gradle (no latest discovery, 
wired in 9.5.0 as latest), Isx (latest only), JBang (full version discovery), JDK (always "current" JDK running) and 
Maven (full version discovery).

With time, I plan to improve ToolRunner support, and given it is done in same way as Nisse, maybe it also enters
Gradle universe as well?