---
title: "Finding own footsteps"
date: 2026-01-16T18:48:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - resolver
  - java
projects:
  - Maven
---

I bet many of us faced a problem, spent almost whole day on chasing it, just to discover their own footsteps around...

My case was that I had a strange issue with Njord ITs: one PR was "fine", except the ITs failed only on single combo: Maven 4-rc-5 
on Java 17. Matrix had 21 and even 25, and they were fine.

It all started by adding this "mostly harmless" repository stanza to the POM:

```xml
    <repository>
      <releases>
        <enabled>true</enabled>
      </releases>
      <snapshots>
        <enabled>false</enabled>
      </snapshots>
      <id>jitpack.io</id>
      <url>https://jitpack.io</url>
    </repository>
```

And some (seemingly unrelated) code changes, and voilà: there goes your day.

Problem was that somehow a "known bug" got manifested with Maven 4 on Java 17, exactly [this one](https://github.com/apache/maven-resolver/pull/1698).
**First footstep discovered**. The fix is in Maven Resolver 2.0.14 but Maven 4-rc-5 still uses Resolver 2.0.13. Meh.

But still, how could this happen?

Turns out, Maven 4 uses JDK Transport as default HTTP transport. Hence, Java "builtin" HttpClient is being used.
Shady, is it?

But just for any case, checked jitpack.io GitHub to see for known issues, only to find [this issue](https://github.com/jitpack/jitpack.io/issues/7186).
**Second footstep discovered**. The issue is closed, but they obviously did not even look at it (was automatically closed).

Finally, it was time to check out Java. Locally and GH CI used currently latest Java 17, that is 17.0.17 Temurin at the time of this writing.
Just to find this issue [JDK-8283544](https://bugs.openjdk.org/browse/JDK-8283544). This was reported by us (Maven project) via
Christian Stein (Hi Christian! :wawe:). And look, the fix is about to arrive in 17.0.18: [JDK-8373393](https://bugs.openjdk.org/browse/JDK-8373393).

Still, what happened that triggered the bug in the first place?

Maven 4 on Java 17 and Java 21 (and 25) got **different responses**! The "good" outcome, on Java versions with fixed
HttpClient the response was 404 Not Found. On "bad" outcome, on Java 17.0.17, the response from jitpack.io was
500 Server Error instead!

And what this resulted in? Nothing big, right? HTTP 404 or HTTP 500, does it matter?

Well, check out Resolver [`ResolutionErrorPolicy`](https://github.com/apache/maven-resolver/blob/2340c676f3aaf920ea7bbb5120b0ade4829a737c/maven-resolver-api/src/main/java/org/eclipse/aether/resolution/ResolutionErrorPolicy.java) class.
It is obvious that Resolver _caches errors_ but also distinguish (sparingly) two types of them: "not found" types and "other".
Also, there is a Maven 4 CLI command:
```
-canf,--cache-artifact-not-found <arg>            Defines caching behaviour for 'not found' artifacts. Supported values are 'true' (default), 'false'.
```

The default is to _cache not found errors, while do not cache other errors_.

And finally, the whole picture was like this: in Maven 4 by default the HTTP 4xx errors _are cached_, while 5xx are not (to be retried).
But alas, this also meant that the "known bug" in 4-rc-5 above got triggered, and the outcome was that IT failed.
All this did not happen on Java 21 and 25, as there Java HttpClient does not sent `Content-Length: 0` on GET
requests, and they got proper 404 and request was not reattempted, and did not trigger the bug.

Hopefully, Java 17.0.18 is out soon, with fixes among others to HttpClient as well.

Cheers!