---
title: "Maven Components and (maximum) Java bytecode"
date: 2026-01-15T15:31:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - java
projects:
  - Maven
---

Multiple times I see people confused about "what is the java bytecode version Maven supports"?

It depends very much on which version of Maven you want to support:
* Maven 3.8.9-3.9.5 uses Sisu 0.3.5 that **shades ASM 5.0.2**
* Maven 3.9.6-3.9.7 uses Sisu 0.9.0.M2 that **shades ASM 9.4**
* Maven 3.9.8-3.9.9 uses Sisu 0.9.0.M3 that **shades ASM 9.6**
* Maven 3.9.10-3.9.11 uses Sisu 0.9.0.M4 that **depend on ASM 9.8**
* Maven 3.9.12+ uses Sisu 0.9.0.M4 that **depend on ASM 9.9**

The ASM library is used by Sisu to "lightly introspect" classes enumerated on sisu-index for annotations. Hence, 
it depends on used ASM version, what bytecode versions can Sisu inspect, and in essence, what maximum bytecode level 
components may be, to have them picked up by Maven. Components not recognized (not being able to introspect) are
silently skipped. Your friend is `-Dsisu.debug` that will tell you about all the issues it finds.

Latest Sisu version 0.9.0.M4 followed Guice and ASM is not shaded anymore, is "demoted" to a plain dependency of Sisu.

Sadly, older versions like Maven 3.8.x are stuck on max Java 13 or so.

One reason more, why follow patch releases of Maven: they have not only bugfixes, but also ASM updates...
