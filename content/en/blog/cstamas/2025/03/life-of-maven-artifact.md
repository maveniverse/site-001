---
title: "The life of Maven Artifact"
date: 2025-03-17T21:55:22+01:00
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

In Maven you will read about following very important things:
* **session** (historically called "reactor" by a Maven 2 plugin) - the set of subprojects Maven is working on
* **project** (sometimes called "checkout", referring that project is checked into some SCM) - the set of subprojects that makes the "project" you are working on
* **local repositories** (since Maven 3.9 you can have multiple of these; in a limited way) - the mish-mash directory, where Maven caches (remote) and installs (locally build) artifacts
* **remote repositories** - most notable one being Maven Central provided "out of the box".

Let's start from end.

**Remarks**: While the concepts are similar, if not same, there may me slight deviations between open source (globally
available) and "corporate" (could not come up with better name) scenarios, where some company provides infrastructure 
(like remote repositories, caches, but also some sort of "confined" network as well).

## Remote repositories

This one is I think simplest, and also the oldest concept in Maven: Maven will get you all dependencies you need to 
build the project, like the ones you specified in POM. And to do so, Maven needs to know all required remote repositories 
where required artifacts reside. In "ideal" situation, you don't need to do anything: all your dependencies will be 
found on Maven Central.

**Note:** Have to note that "dependencies you need" are **not only dependencies you specified in POM**! Maven itself
performs builds using **plugins**, and you guessed, those are also JAR artifacts, fetched from remote repositories.
So remote repositories should be declared for all artifacts your build needs.

By default, Maven will go over remote repositories "in defined order" (see effective POM what that order is) in a 
"round-robin" (from first to last) fashion to get an artifact. This has several consequences: you usually want most
used repository as first, and to get artifacts from last repository, you will need to wait for "not found" from all
repositories before it. The solution for first problem is most probably solved by Maven itself, having Maven Central
defined as first repository (but you can redefine this). The solution to last problem is offered as 
[Remote Repository Filtering](https://maven.apache.org/resolver/remote-repository-filtering.html).

From time to time, it is warmly recommended (or to do this on a CI) to have a build "from the scratch", like a fresh
checkout, with empty local repositories. This usually immediately shows issues about artifact availability.

Also, from this above follows why **Maven Repository Manager (MRM) group/virtual repositories are inherently bad thing**:
By using them, Maven suddenly completely loses concept of "artifact origin", and origin knowledge is shifted to MRM.
This may be not a problem for project being built in and only in controlled environments (where MRM is always available),
but in general is very bad practice: Maven users in such environment and MRM admins may become disconnected, or just
a simple mishap may happen (adding some new repository to a group) and suddenly, much more artifacts become available
to Maven thru these "super repositories". And worst, Maven build is not portable, and has a split-brain situation:
to be able to build such a project, Maven alone is not enough, one need to provide very same "super repository" as 
well. It is much better to declare remote repositories in POM, and have them "mirrored" (one by one) in for example
company-wide `settings.xml`, instead to opposite example: where there is "Maven Central" set as `mirrorOf` and points
to a "super repository". If former Maven **still can build** project if taken out of MRM environment (assuming all
POM specified repositories are accessible public repositories), while in latter build is doomed to simply fail when
no custom `settings.xml` and MRM present. Ideally, a Maven build **is portable**, and if one uses group/virtual
repositories, you not only lose Maven origin awareness, but also portability.

Remote repositories are by nature "global", but the meaning of "global" may mean different thing in open source and
"corporate" environments.

Remote repositories contains **deployed** artifacts meant to be shared with other projects.

## Local repositories

Maven always had "local repository": a directory where Maven caches remotely fetched artifacts, and installs locally
built artifacts. It is obvious, that local repository is "mixed bag", and this must be considered when setting up
caching on CI. Many times you want only cached artifacts, but not installed ones.

Since Maven 3.0, local repository caching was enhanced by "origin tracking", to help you keep your sanity with 
"works for me" like issues. Cached artifacts are tracked by "origin" (remote repository ID), and unlike in Maven 2, 
where artifact (file) presence automatically meant "is available", in Maven 3.0+ it is "available" ONLY if artifact
(file) is present, AND origin is contained in caller context provided remote repositories.

Since Maven 3.9 users may specify multiple local repositories as a list of directories, where HEAD of list is the 
local repository in its classic sense: HEAD receives newly cached and installed artifacts, while TAIL 
(list second and remaining directories) are used only for lookups, are read-only. This comes handy in some more 
advanced CI or testing setups.

**Important**: You are not married to your local repository! In other words, it is "best practice" if not downright
real lifesaver to completely delete your local repository from time to time (ie. weekly). In Maven 2 times, it became
a (bad) habit to "stick to your local repository" as it was really just a "bunch of files" laid out in some way.
But, since Maven 3.0 doing this is wrong: the "origin tracking", while is done with good intents (compare to
"road to hell"), is not flawless and has issues. Also, many things, like renaming a subproject or alike can cause 
headache, that can be easily solved (and spotted!) just by nuking your local repository. 

Since Maven 3.9 users may opt to use "split local repository" that solves most of the issues, and one is able to
selectively delete accumulated artifacts: yes, you do want to delete installed ones from time to time,
and probably remote snapshots as well. Luckily, "split local repository" keeps things in separated directories, and
once can easily choose what to delete. OTOH, "split local repository" is not quite compatible with all the stuff present in
(mostly legacy) bits of Maven 3 universe. Using "split local repository" is **warmly recommended, if possible**.
If you cannot use "split local repository", you should follow advice from previous paragraph, and nuke your local
repository regularly, unless you want to face "works for me" (or the opposite) conflicts with CI.

Local repositories are, as name suggests "local" to host (workstation or CI) that runs Maven, and is usually on 
OS local (or maybe some mounted) filesystem.

Local repositories contains **cached** artifacts pulled from remote repositories, and **installed** artifacts
that were built locally (on host the local repository belong to). Split local repositories keeps these physically
separated, but non-split ones keeps them mixed.

## Project

Project usually contains one or more subprojects, that contains **sources** that when built, will end up as 
**artifacts**. So, unlike above in remote and local repositories, here, we as starting point have no artifacts.
Artifacts are materialized during build.

## Session

The session is what Maven builds: usually or most commonly is same as "project" above, unless some "limiting" options 
are used like `-r`, `-rf` or `-N` and alike. 


## Finding things

It is important to note here, that if session is
"limited", the subprojects loaded by Maven are not the same/equal present in project (checkout), the excluded
subprojects are "invisible" to Maven. They can 

## mvn clean install vs mvn verify

## Changing branches