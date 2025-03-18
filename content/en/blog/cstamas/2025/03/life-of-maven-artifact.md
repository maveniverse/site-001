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

{{% pageinfo color="info" %}}

This article assumes reader has basic knowledge about Maven, POM and related things. The main point is to offer high
level conceptualization and explain things "why's" and "why not", and finally explain why you don't want to listen to
folks that tells you "never do..." (unless they are your parents).

{{% /pageinfo %}}

{{% alert title="Disclaimer" color="info" %}}

While the concepts are similar, if not same, there may me slight deviations between open source (globally
available) and "corporate" (could not come up with better name) scenarios, where some company provides infrastructure
(like remote repositories, caches, but also some sort of "confined" network as well).

{{% /alert %}}

## The pieces

In Maven you will read about following very important things:
* **session** (historically called "reactor" by a Maven 2 plugin) - the set of subprojects Maven is working on
* **project** (sometimes called "checkout", referring that project is checked out from some SCM) - the set of subprojects that makes the "project" you are working on
* **local repositories** (since Maven 3.9 you can have multiple of these; in a limited way) - the mish-mash directory, where Maven caches (remote) and installs (locally built) artifacts
* **remote repositories** - remote repositories that contains deployed artifact meant to be shared. Most notable one being Maven Central provided "out of the box". Most often they are reached via HTTPS.

Let's start from end.

### Remote repositories

This one is I think simplest, and also the oldest concept in Maven: Maven will get you all dependencies you need to 
build the project, like the ones you specified in POM. And to do so, Maven needs to know all remote repositories 
where required artifacts reside. In "ideal" situation, you don't need to do anything: all your dependencies will be 
found on Maven Central.

{{% alert title="Important" color="warning" %}}

Have to note that "dependencies you need" are **not only dependencies you specified in POM**! Maven itself
performs builds using **plugins**, and you guessed, those are also JAR artifacts, fetched from remote repositories.
Hence, remote repositories should be declared for all artifacts your build needs.

{{% /alert %}}

By default, Maven will go over remote repositories "in defined order" (see effective POM what that order is) in a 
"ordered" (from first to last) fashion to get an artifact. This has several consequences: you usually want most often
used repository as first, and to get artifacts from last repository, you will need to wait for "not found" from all
repositories before it. The solution for first problem is most probably solved by Maven itself, having Maven Central
defined as first repository (but you can redefine this order). The solution to last problem is offered as 
[Remote Repository Filtering](https://maven.apache.org/resolver/remote-repository-filtering.html).

From time to time, it is warmly recommended (or to do this on a CI) to have a build "from the scratch", like a fresh
checkout in a new environment, with empty local repositories. This usually immediately shows issues about artifact availability.
Nothing special needed here, usually is enough just to use `-Dmaven.repo.local=some/alt/loca/repo` to achieve this.

Also, from this above follows why **Maven Repository Manager (MRM) group/virtual repositories are inherently bad thing**:
By using them, Maven completely loses concept of "artifact origin", and origin knowledge is shifted to MRM.
This may be not a problem for project being built exclusively in controlled environments (where MRM is always available),
but in general is very bad practice: In such environment if Maven users and MRM admins become disconnected, or just
a simple configuration mishap happens (by adding some new repository to a group) problems can arise: from suddenly much more artifacts becoming available
to Maven through these "super repositories" to complete build halt. And worse, Maven builds like these are not portable, as they have a split-brain situation:
to be able to build such a project, Maven alone is not enough! One need to provide very same "super repository" as 
well. It is much better to declare remote repositories in POM, and have them "mirrored" (one by one) in
company-wide `settings.xml`, instead to do it opposite: where one have "Uber Repository" set as `mirrorOf *` and points
it to a "super repository". In former case Maven **still can build** project if taken out of MRM environment (assuming all
POM specified repositories are accessible repositories), while in latter case, build is doomed to simply fail when
no custom `settings.xml` and no MRM present. Ideally, a Maven build **is portable**, and if one uses group/virtual
repositories, you not only lose Maven origin awareness, but also portability. Hence, in case of using "super groups",
**MRM becomes Single Point of Failure**, as if you loose MRM due any reason, all your builds are doomed to be halted/fail, 
for as long MRM is not recovered and not set up in very same way as it was before. You are always in better situation, 
if you have a "B plan" that works, especially if having one is really "cheap" (technically).

Remote repositories are by nature "global", but the meaning of "global" may mean different thing in open source and
"corporate" environments.

Remote repositories contains **deployed** artifacts meant to be shared with other projects.

### Local repositories

Maven always had "local repository": a local directory where Maven caches remotely fetched artifacts and installs locally
built artifacts. It is obvious, that local repository is a "mixed bag", and this must be considered when setting up
caching on CI. Most of the time you want cached artifacts only, not the installed ones.

Since Maven 3.0, local repository caching was enhanced by "origin tracking", to help you keep your sanity with 
"works for me" like issues. Cached artifacts are tracked by "origin" (remote repository ID), and unlike in Maven 2, 
where artifact (file) presence automatically meant "is available", in Maven 3.0+ it is "available" **only** if artifact
(file) is present, **and** origin remote repository (from where it was cached) is contained in caller context provided 
remote repositories.

Since Maven 3.9 users may specify multiple local repositories as a list of directories, where HEAD of the list is the 
local repository in its classic sense: HEAD receives newly cached and installed artifacts, while TAIL 
(list second and remaining directories) are used only for lookups, are used in read-only manner. This comes handy in 
some more complex CI or testing setups.

{{% alert title="Important" color="warning" %}}

You are not married to your local repository! In other words, it is "best practice" if not downright
real lifesaver to completely delete your local repository from time to time (ie. weekly). In Maven 2 times, it became
a (bad) habit to "stick to your local repository" as it was really just a "bunch of files" laid out in some way.
But, since Maven 3.0 doing this is wrong: the "origin tracking", while is done with good intents (compare to
"road to hell"), is not flawless and has issues. Also, many things, like renaming a subproject or alike can cause
headache, that can be easily solved (and spotted!) just by nuking your local repository.
Unless, **you can use "split local repository"**... read more on that below.

{{% /alert %}}

Since Maven 3.9 users may opt to use "split local repository" that solves most of the above-mentioned issues, and allows one to
selectively delete accumulated artifacts: yes, you do want to delete installed and remote snapshots from time to time.
Luckily, "split local repository" keeps things in separated directories, and one can easily choose what to delete. 
But all this comes at a price: "split local repository" is not quite compatible with all the stuff present in
(mostly legacy) bits of Maven 3 universe. Using "split local repository" is **warmly recommended, if possible**.
If you cannot use it, you should follow advice from previous paragraphs, and nuke your local
repository regularly, unless you want to face "works for me" (or the opposite) conflicts with CI or colleagues.

Local repositories are, as name suggests "local" to host (workstation or CI) that runs Maven, and is usually on 
OS local filesystem.

Local repositories contains **cached** artifacts pulled from remote repositories, and **installed** artifacts
that were built locally (on the host). You can also `install-file` if you need an artifact present in local repository.
Split local repositories keeps artifacts physically separated, while the default one keeps them mixed, all together.

### Project

Projects are usually versioned in some SCM and usually contain one or more subprojects, that again contain **sources** 
that when built, will end up as **artifacts**. So, unlike above, in remote and local repositories, here, we as starting 
point have no artifacts. Artifacts are materialized during build.

Still, inter-project dependencies are expressed in very same manner as dependencies coming from remote repositories.
And given they are "materialized during build", this has severe implications that sometimes offers surprises as well.

### Session

The session contains projects that Maven effectively builds: usually or most commonly is same as "Project" above, 
unless some "limiting" options are used like `-r`, `-rf` or `-N` and alike. It is important to keep this (not obvious)
distinction, as even if checkout of the project contains certain module, if that module is not part of the Session,
Maven treats it as "external" (to the session). Or in other words, even if "thing is on my disk" (checked out), Maven
if told so, will treat it as external artifact (not part of Session).

## How Maven finds things?

## When to clean?

## When not to clean?

## Practical examples


## mvn clean install vs mvn verify

## Changing branches