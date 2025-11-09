---
title: "Maven Local Repository"
date: 2025-11-09T12:34:23+01:00
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

## The Problems

The problem with Maven local repository is manifold: it is **global** and is **mutable**. To solve these issues
we chased things like "repository locking" in Maven 3.9 that proved futile, somewhat.

## First problem

Originally, in Maven2 (hence the `~/.m2` directory) the local repository (by default located in `~/.m2/repository`)
was a "bunch of files": it contained cached artifacts from remote, and also installed (hence, locally built) artifacts
too. Basically, a file was present or absent, hence it got used if present or download was attempted if absent. On the
other hand, this behaviour introduced several problems too, most of them resulting in "works for me" mysterious issues,
usually revealed once user nuked local repository (ie build passed on one but failed on other workstation; most often
due a dependency artifact present in local repository on one workstation but not other; while the initial issue was 
build POM lacking one repository declaration, from where the artifact in question should come. Basically, build
depend on "state" of workstation, or more precisely, on "state" of local repository).

In Maven 3.0 with introduction of Resolver (historically Aether), things changed, but were not fully fixed. Maven 3.0
and later versions used Resolver, that contained **two** local repository implementations: the "simple" one, that 
100% reimplemented Maven 2 local repository logic ("just a bunch of files") and "enhanced", that tried to address
the above-mentioned problem. The artifacts "availability" was introduced, where artifact was "available" only if it was
**present** on disk, and **origin tracking** of it corresponded to one of repositories in local search request
(example: enhanced local repository cached an artifact from Central repository, and on subsequent calls -- it from
totally unrelated build, it would hand over artifact to caller only if the request would carry Central repository 
as well, otherwise, despite artifact file being present, would respond "present, but not available"). Obviously, 
and while this is a "technical detail", to understand consequences, we have to look into this detail: "origin
tracking" used [`ArtifactRepository`](https://maven.apache.org/resolver/apidocs/org/eclipse/aether/repository/ArtifactRepository.html)
"id". In short, this means that if an artifact was originally cached from remote repository having ID "central",
and subsequently asked for using remote repository having ID "maven-central", despite having possibly same URL,
Resolver can report only "unavailable", as `"central" != "maven-central"`.

Initially, in Maven 3.0 the "enhanced" local repository implementation was coded with simultaneous Maven 2 usage
(same repository may be used on same workstation by two major Maven versions), hence the enforcement was made "as mild
as possible", it would kick in in only very rare cases. Starting with Maven 3.9.x line (Resolver 1.9.x) things changed,
we introduced the `aether.artifactResolver.simpleLrmInterop` Resolver configuration property that controls this 
"automatic interoperability", and defaults to `false` (so by default is turned off). But this alone is still not 
enough to fix the original problem.

As we know, artifacts within one remote repository are unique. Or in other words, a remote repository cannot have
two conflicting artifacts having same coordinates, this is physically impossible. But what happens when we introduce
two or three remote repositories in our build? In such cases, we say that "artifact is unique in the build when 
we factor in repository of its origin as well". These are the cases when we write `RGAV` instead of `GAV`, former
coordinate carries origin repository as well, while latter only Maven Artifact coordinates, hence, latter is
uniquely identified only within one single repository.

As we see, within remote repository, `GAV` is unique, and within **one build** the `RGAV` is unique. But what happens
in **global local repository**? Or in other words, as remote repositories **unique**? Practice shows, they are not.
Moreover, practice shows that same repositories (even very same URLs) may carry IDs that are wildly different.

Typical examples are `apache-snapshots` vs `apache.snapshots` (dash vs dot) or `apache-snapshot` (plural vs singular).
In this case, "enhanced" local repository immediately fails: despite you cached some artifact from `apache-snapshots`,
if your next build asks for same `GAV` from `apache.snapshot`, despite that artifact being present in your local
repository, Resolver cannot respond "available", only "unavailable".

The problem just deepens: assume you work as a consultant, and you have multiple clients, and all of your 
"well behaving" clients use MRMs (Maven Repository Manager, as it is best practice). MRMs are usually set up not only 
to cache Central and other often accessed public repositories, they usually contain hosted repositories like 
`releases` or `snapshots` as well. And client builds usually declare their internal hosted repositories as sources 
for their (own, developed and built by them) artifacts in their POM. Hence, you will end up with two checkouts on your 
workstation, both having `releases` repositories definition, but containing wildly different artifacts! Basically, 
same repository ID represents totally different remote repositories. Also, this example above is true for forges as
well, this is very same pattern as above for ASF snapshots.

But all this above can happen if you stay only on OSS grounds: you may build locally same ASF Maven and maybe other ASF 
projects, maybe some Eclipse projects, maybe Mojohaus and Plexus projects, some Quarkus or Spring, Netty.. as their 
"dictionary" all may conflict and diverge: they can define various other remote repositories with different IDs and
URLs (like they do). Usually "within a parent", their own repositories are aligned (ie ASF or Eclipse forges), but 
still ASF and Eclipse project, especially if project needs to introduce own remote repository (outside of forge)
pointing "outside" of own forge controlled infra (think ASF project defining Eclipse repository for example).

We can see an emerging pattern:
* `GAV` is unique per given remote repository
* `R` is unique per given build (not always! -- even here we can have deviation). Hence, we can say `RGAV` is unique within build
* remote repositories are not unique globally: they may have wildly different IDs assigned, different URLs assigned (they can move, change URLs, get redirected, and so on)

{{% alert title=Note color=info %}}

Transitive dependencies may introduce "their own" repositories! Not only that, they may override them even (in controlled
way, only for their own subtree). Hence, Maven 3.9.x introduced `-itr` (or `--ignore-transitive-repositories`) option, that
will make your build fail if dependency cannot be fetched, and allows your own POM to be in "full control" of used
remote repositories instead. Various tools exist to scout for needed remote repositories as well.

Moreover, "split local repository" feature of Maven 3.9 somewhat alleviates the problem of uniqueness as well, as it
**can** store same `GAV` coming from different `R` (if configured to do so), but split repository proved too invasive
for many cases and may break builds and IDEs.

{{% /alert %}}

And here comes the problem: with Maven Local Repository being **global**, what do you think, what happens after a week
of building various projects, as explained above? Even if you do not **install**, the very same still applies...

Moreover, if you build (not same, maybe two completely different checkouts/projects) on same workstation, and it happens
that two builds define two remote repositories that again, happen to have overlapping `GAV`s... you will end up with
inevitable conflict in local repository (even worse, not "conflict" per se, but silently introduced issue you may not
notice even, or you may by getting unexpected runtime errors).

## Second problem

Contents of local repository, at least _some of them_ are also mutable (on file level). This improved a lot since 
Maven 2, but Maven 3 still left many kind of local repository entries **mutable**. In fact, it is easier to enumerate 
what is immutable in local repository, instead to enumerate what is mutable: cached release artifacts are the only 
immutable content in local repository. Everything else, snapshot artifacts ([yes!](https://github.com/apache/maven-resolver/blob/master/maven-resolver-impl/src/main/java/org/eclipse/aether/internal/impl/DefaultArtifactResolver.java#L96-L106)), repository metadata and resolver 
"internal files", are all mutable. And due to that, various solutions were made, that peaked by addition of 
"named locks" in Resolver 1.9, to protect local repository from mutating by different (Maven or other local 
repository altering) processes.

Named locks did provide some relief, but there are still ongoing issues with it (just check our issue tracker) by 
various people having pretty much similar issues: lock timeouts. Latest discoveries points toward suboptimal
design of [`SyncContext`](https://maven.apache.org/resolver/apidocs/org/eclipse/aether/SyncContext.html), that in turn, fully reflects all written things about local repository above (excluding the
split that happened after it): a `GAV` irrelevant of its `R` origin will land on the same file path. This implies, that if your
build depends on `GAV` and use 10 remote repositories, Resolver has to lock `GAV` corresponding lock _without factoring
in `R`_, only to wait for results of accessing 10 various repositories. And there will be some timeouts.

## Solution

Simplest solution is: get rid of **global** and **mutable** aspects. More about it in next blog.