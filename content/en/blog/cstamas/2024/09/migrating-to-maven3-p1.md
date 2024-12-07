---
title: "Migrating to Maven 3, part 1"
date: 2024-09-07T17:55:22+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://twitter.com/cstamas))
categories:
  - Blog
tags:
  - plexus
  - sisu
  - jsr330
projects:
  - Maven

---

As weird as title sounds, given Maven 4 is "around the corner", the sad reality is that there are still way too many libraries and 
plugins in "Maven ecosystem" that rely on some sort of "compatibility" layers (and deprecated things) in Maven 3. For example
[Eclipse Sisu](https://github.com/eclipse-sisu/sisu-project) is fully functional and in charge since 
Maven 3.1.0 (released in 2013, when last missing piece, support for "sisu index" was added). Maven project during it's 
existence did pile up some of the debts, or in other words, "moved past" some well known libraries. 
Plexus DI Container and Wagon being the most notable examples.

## The Problem

The Plexus DI Container is from the Plexus umbrella project that started on great 
[Codehaus](https://github.com/codehaus/www-codehaus-org/blob/master/app/history.md) (and **do smile** while you read this). 
Plexus project consists of **many** subprojects: the 
"die hard" `plexus-utils`, Plexus DI container, Plexus Compilers, Plexus Interactivity, and so on, and so on.
But let's focus on Plexus DI.

When I joined Sonatype in 2007., we started "porting" the Proximity from Spring DI 1.x to Plexus DI to make Nexus 1.0.
While we were porting it, more and more issues cropped up with Plexus Container, that mostly stemmed from the 
vastly different use case for it: at that point, Plexus DI was mostly used as container for Maven (mvnd was nowhere
yet!), a one-time CLI that started up, discovered, created and wired up components, did the build, and then JVM exited. 
It was a big contrast in use case, Nexus was meant to be a long-running web application. We started fixing and 
improving Plexus, but then stepped in [Stuart](https://www.linkedin.com/in/mcculls/), and he made Sisu happen. 
Sisu was a suite, or layers of DI, that built upon then "brand new" Guice, and it added a "shim" layer on top of it, 
that implemented the "Plexus layer". In short, Sisu builds upon Guice, and Plexus-shim builds upon Sisu. All the 
giants in a row.

## The Solution

The goal of Plexus-shim was to provide a true "drop in replacement" for old `plexus-container-default`, and funnily 
enough, Nexus 1.x project served as "functional test ground". The reason for that was Plexus DI never had any TCK or 
similar test suite. Basically, all we had was some existing codebases (Maven, Nexus) with their own suite of functional 
and integration tests, and codebase used `plexus-container-default`. So we then just built the project with swapped out 
Plexus DI (using Plexus-shim instead) and ran same test suite again. Rinse and repeat. It was fun times.

The original Plexus DI was great at the time (mid 2000s), but new DI solutions surpassed it. Biggest problem with 
Plexus DI was that all it "knew" was field injection that, among other things, made writing UTs a bit problematic. 
Since modern DIs, we all know that "constructor injection" is the way, but it never happened in Plexus DI. 
The implication was that libraries using Plexus DI (that to be frank, was mostly around and in "Maven ecosystem") 
could not write immutable components or proper unit tests (am not saying it was not possible, but was more a burden 
than it should have been).

My childhood fencing trainer had a saying: "is like reaching to your left pocket with right hand". Same feeling was
about Plexus DI when Guice barged in. We desperately needed something better, and Sisu DI made that happen.

## The Real Problem

As I mentioned above, since Maven 3.1 Sisu is "fully functional" in Maven. Still, most likely due inertia, many
projects left unchanged, even Maven "core" ones, and remained in a cozy state: why change, if everything works? Sure, that 
is merely the proof of great job Stuart did back then.

Around early 2021. frustration of several Maven PMCs resulted in creating a 
["cleanup manifesto"](https://cwiki.apache.org/confluence/display/MAVEN/Maven+Ecosystem+Cleanup) to simply stop postponing
the inevitable, as Maven codebase almost came to the grinding halt: no progress or innovation was possible, as whatever 
we touched, the other pile broke. Moreover, the "future of Maven" was way too long in the air. The heck,
even I had a presentation in 2014. called ["The Life and Death of Apache Maven"](https://www.slideshare.net/slideshow/life-anddeathofmaven/34284731) (in Hungarian).
Ideas like "new POM model" and many other things were left floating around for way too long.

Just let me repeat, the **"de-plexus"** notion is heavily emphasized in that "cleanup manifesto" document, for a good
reason.

## Prepare for the Future

Maven 4 will come with its own API (more about it in some later post), but one fact stands: the 
Maven DI (new in 4) **resembles the JSR330, not the Plexus DI (with all the XML and stuff)**.

Basically, just do yourself a favor, and move from Plexus DI to JSR330 now. You will thank me later.