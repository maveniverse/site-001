---
title: "Lockfiles"
date: 2025-12-06T15:31:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - LRM
  - lockfile
projects:
  - Maven
---

{{% pageinfo color="info" %}}

A short attempt to explain why Maven does not have "lockfile", at least not in a sense many other build tools
and ecosystems have. Next, will try to point out features that somewhat supplement various aspects
of lock files. Finally, will throw in some bait and markers where we plan to go from here.

{{% /pageinfo %}}

## What are lock files?

For context would like to point to ML discussion [ongoing here](https://lists.apache.org/thread/ofmy316jk9z0y6dwcjybvrwbv71993fh).
In general, lock files usually carry following information or aspects:
* resolved artifact versions, some varies by plugins/extensions and their dependencies being counted in, or 
  only the transitive hull of project dependencies. Main reason for this is build reproducibility enforcement (collection 
  reproducibility, to be precise, as "build reproducibility" is much broader topic).
* usually cryptographic checksums (hashes), for those artifacts above. Reason for this is integrity enforcement.

Optionally, they may record more metadata and aspects, such as:
* signatures for those artifacts above. Reason is similar as for cryptographical checksums (signature verification).
* platform specific information (OS, Maven and Java, given we talk about Maven)
* other requirements or constraints

It is colloquially and generally stated that "Lock files reduce build times, help verify the integrity of resolved 
packages, and support build reproducibility across environments and time". Which of these claims stand for Maven?

{{% pageinfo color="info" %}}

I have to note, that Maven, even today, without lock file support, do support reproducible builds, **if documented
practices and rules are followed**, [as explained here](https://maven.apache.org/guides/mini/guide-reproducible-builds.html). Also, as [Reproducible Central](https://github.com/jvm-repo-rebuild/reproducible-central) project shows, 
this is already doable.

{{% /pageinfo %}}

Also, let me paraphrase the usual response (present on the referenced mailing list thread above) about lock files for 
Maven: "they are **not needed** for Maven because..." (fine-print: IF you follow "best practices" and other things...).

## Are Maven lock files needed?

As I paraphrased above the "usual Maven-er response": no, it claims it is not. The fine-print in turn adds constraints as
"if you follow some rules we call **best practices**".

Let's check step by step, aspects of lock file and how it applies to Maven.

### Collection reproducibility

Note: here, "reproducibility" targets strictly **Maven dependency collection reproducibility** and not build 
reproducibility.

Maven dependency collection is stable, if some constraints applied. Essentially, resolving from same starting state will
always end up with same ending state, but there is a fine print: **when no version ranges, and meta-versions are used**
(for this discourse, let's stick to releases and leave out SNAPSHOT versions). As if your build happens to use any of 
those, initial claim does not stand anymore. But this is fine, is it? Meta-versions ("RELEASE" and "LATEST") has been 
clearly deprecated since Maven 3 initial release, and you should just not use evil ranges, right? 

The problem with this claim, is that even if your project does not use version ranges, you may still end up using them, via
some transitive dependency. And in that case, user only option is to either phone vendor and politely ask them to stop 
using ranges, switch vendor or manage it. Problem here, is that aside of these, user have no third option. The 
"do not use ranges" mantra (dogma?) goes so far, that there is even an enforcer rule banning "dynamic versions" 
(called `badDynamicVersions`). It may help one to "manage" range version, but still, they may fall in out of the blue.
And this represents more work for user, to manage things he should not manage.

### Artifacts integrity

Maven since very beginning used checksums (that ironically were implemented as hashes) to **verify artifact integrity 
during transport**. The last part of sentence is very important: If you build with empty local repository, and you use
strict checksum policy, Maven will fail your build if any checksum mismatch is detected (otherwise will just WARN).
The original intent of these checksums were simply bit-rot or transfer corruption detection. By default, the "default
Maven checksums" are SHA-1 and MD5 (order matters: the ordered list instructs Resolver how to asks for remote artifact
checksums, as in aforementioned order, it will first try SHA-1 and then fallback to MD5. This is the reason why local
repository always contains only one of these checksums, and those are usually SHA-1 as they are always present, and
the MD5 fallback in reality never happens).

Since Maven 3.9 the [checksums are made into SPI](https://maven.apache.org/resolver/about-checksums.html), and set of 
out of the box supported checksums has been expanded with SHA-256 and SHA-512. This was a huge change, as before this,
in Maven 3.8 and older versions, checksums were simply "baked in". Now, users can add really any kind
of checksum algorithms via extensions SPI. But, how can one make use of newly added checksums like SHA-512 if commodity repositories
like Maven Central does not have them?

Meet **provided checksums feature**, also added in Maven 3.9. In Maven 3.9, along with checksum SPI Resolver got many
other improvements as well, and among them are support for 3 [checksums kind](https://github.com/apache/maven-resolver/blob/3fc3557e332927917f8d8cce86068fee3fd38cc6/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/checksum/ChecksumPolicy.java#L70):
* remote external
* remote included
* provided

The first two kind comes from remote, as name implies, and in this case you rely on same trust for checksums as you rely
on trust that artifacts served by remote are "proper". The first kind is the "good old" checksum file laid down next to
artifact file, as we knew them since Maven was Maven. The remote included checksums kind introduced huge performance
boost for users even without any change on their part, it essentially cuts HTTP request count in half, as second 
request for checksum becomes not needed: many repositories and MRMs "include" artifact checksums in their response
(for example as HTTP headers), so Maven gets them at the moment response headers are available. 

But the third kind is special, they are "provided" ahead of time, from somewhere, anywhere. And this allows user to 
enforce trust, by for example getting artifact from one remote, while checksums for integrity checks may come from 
somewhere else. Naturally, this also implies that artifact serving remote even does not have to contain given checksums, 
or any checksums at all, as they come from elsewhere and remote is never asked for them.

The "remote external" and "remote included" kinds always coexist in Maven, and if "remote included" is detected, is used, 
otherwise fallback to "remote external" is triggered, and subsequent request is made to get the external checksum 
from remote. The third kind needs user intervention, as user has to provide checksums in some way.
In local repository no change can be seen, the local repository persists checksums in very same way as before, 
irrelevant how they arrived, they will be stored.

But this still does not solve the problem, since all this happens **during transport** only!

To connect the dots, another neat feature that Maven 3.9 got was Resolver post-processor SPI: it is basically a hook, that 
is invoked for **every resolved artifact**. And as very first natural implementation of this hook (and is provided out
of the box), is **trusted checksums** feature.

Trusted checksums, in contrary to provided ones, are not tied to transport, they are available in any scope. Moreover, 
with adapters in place, every trusted checksum becomes immediately a provided checksums as well. 
Trusted checksums are used as:
* in transport, as "provided" kind (since they are automatically adapted to provided kind of checksums)
* in resolver post processor, for verification of each resolved artifact

And, the circle closes here. As can be seen, **Maven 3.9 allows one to provide even cryptographic checksums (not  
present in remote) ahead of time as trusted checksums, and those checksums will be used to verify artifacts always**,
not only if transport is involved. Naturally, all this will have some overhead to your build, but its nuance diminishes 
when you consider what you get with it. Also, one can do these verifiable builds on CI only, and not literally on 
each build (but nothing prevents you to do so).

### Optional elements of lockfile

I will not spend a lot of time on these, but just mention some things in short. 

Signature validation can already be done with a cool [Maven plugin](https://github.com/s4u/pgpverify-maven-plugin) from 
Slawek. See [Maven GPG Plugin](https://github.com/apache/maven-gpg-plugin) for usage example.

Enforcer Maven Plugin has many rules that may lock down Java, Maven or OS versions even. Combined with 
[Nisse suite](https://github.com/maveniverse/nisse) (also a drop in for abandoned os-detector) can help you lay
down even more broad "rules" related to OS and other properties.

{{% pageinfo color="info" %}}

For a trusted checksum demo, see here: https://github.com/cstamas/tc-demo

{{% /pageinfo %}}

## But what about version ranges?

Well, this is where I disagree with "usual response". Maven supports ranges, and while they were really problematic in
Maven 2 and 3 era, in Maven 4+ they got several huge improvements. 
To me, current situation is like buying a car, that has a trunk, but the dealer advises you "It's better to not use trunk
to avoid any problems. In fact, if trunk is used, the car warranty is breached, you are on your own". Wat?

Have to note, that the improvements present right now in Maven 4 still do not solve lack of lockfile (collection reproducibility), 
but that goal is planned too, along with many others.

Right now, with Maven 3.9+ what one can do is to enforce that you provide
all required checksums for the build (see `aether.artifactResolver.postProcessor.trustedChecksums.failIfMissing` 
[configuration property](https://maven.apache.org/resolver-archives/resolver-1.9.24/configuration.html)). As if anything changes, 
for example Maven "wanders off" over some range, as new
version pops up, build will fail and
will force you to look into the reasons of failure. And if this happens, two outcomes are possible: your inspection
deems new version (that is picked into range) as "okay", and you update the trusted checksums index, and life goes on. Or,
you can just manage it back to "proper" version. Trust is re-established, but reproducibility is lost. For reproducibility,
the only solution today with Maven 3.9 is always managing the dependency that uses range, which is an unwanted extra work for you.