---
title: "POM proliferation, part 1"
date: 2025-07-02T12:34:23+01:00
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

This blog entry was done as a response to [Pom-Pom-Pom](https://www.liutikas.net/2025/06/12/Pom-Pom-Pom.html).
Note: this entry does not want to be hurting, personal or anything like that; still my native language is not
english, so bear with me (and feel free to create updates to it).

{{% /pageinfo %}}

## Where to start?

By reading that article, I frankly have no idea where to start. Take the title for example: "Brief history of 
POM proliferation", and the article has nothing about it at all. So let me fill in, as history is important.

Around end of 2005., when Maven "as we know it today" (Maven 2.0) was born, in fact two things happened: not only the 
Maven CLI (the command line utility that performs the build), but also Maven Central was born too 
(true, not in today's form), the venerable `repo1.maven.org`. One was envisioned with another, and one cannot exist
(or would be severely crippled, or dysfunctional) without the other. And this is the real strength of the Maven:
the idea of remote repository. Maven Central was created by Maven for Maven, as part of Maven as whole. It was 
initially ran by one person (!), then a group of people, and finally since 2010s by Sonatype, as it is run today. 
Maven today is kinda split-brain: the Java CLI part is maintained by volunteers only in their free time (or hobby time)
as part of ASF top level project, while the Maven Central, as mentioned above, is maintained by Sonatype.

Important to note: **nobody pays for using Maven Central, it is a public good**, with all the good and bad parts of it.

Fast-forward seven years, for first GA version of Gradle (2012), a commercially backed build tool to appear,
that sat on the bandwagon with many other Java related tools, and consume Maven Central. As at that time, Maven Central 
was already de-facto the standard for OSS Java library distribution. Other tools learned (or tried to learn) to use it, and some, 
like Gradle even extended it with extra metadata (am unsure is any other tool using that extra metadata).

In short, Maven Central was created as part of Maven project, hence is a "Maven thing", and together with CLI 
both have a history spanning over almost quarter of century. Knowing this, one could really expect it to be "all about POMs".
And you can imagine, during these years, we had always been approached by people or organizations coming to us 
(I was Sonatype in sonatype for almost 10 years) claiming they "know things better" or having better ideas or better solutions. 
But, here we are where we are.

## What is Maven?

Maven historically had a very convoluted and not-much-saying description, something along these lines: "Maven is a 
software project management and comprehension tool". But let's just focus on it's "build tool" facet, and for sake
of simplicity, ignore all its other aspects like "site building" etc.

While Maven is primarily used in Java projects ("Java build tool"), it can do more. In fact, Maven had many "native" 
plugins, that did or did not survive until present. But in its core, the `"java"` is just one identifier for artifact
language, and Maven always supported other languages as well (native C/C++, Flex or even .NET).

Maven is a highly pluggable beast, in fact its "core" is really, really simple: it is just like an executor; you put
your nibbles (plugin executions) on threads (lifecycle), and pack those into blocks (modules) and you have your
reactor. Reactor can be executed linearly (single threaded) or there are different executors like [Takari Smart Builder](https://github.com/takari/takari-smart-builder)
or [Maven Turbo Builder](https://github.com/maveniverse/maven-turbo-builder) that even rearranges your "nibbles" for better performance (with some sane restrictions).

Finally, the strength of Maven is declarative nature: you say what you want, and not how to do it (like Prolog vs Pascal).
And yes, Maven has downsides, many, but none of them can become as hard to solve as solving spaghetti build scripts or Ant
build XMLs. You always want to keep it simple (stupid), and if you do it, Maven will be your friend.

## Assumptions about Maven

I always smile when people say "Maven is dead", as it always reminds me of people doing same to Java. Java is "dead" for 
quite some time, according to some, just that it is not: we have constantly improving Java releases. And same thing happens 
with Maven: in fact, currently it is very vibrant community with its ups and downs, as every community driven project 
can be, where there are no "managers", "roadmaps" and "budget" in question.

Right now, the "stable" Maven 3.9.x line is getting new releases and improvements, while Maven 4.0.x is heavily in the 
works, getting close to its GA. Maven 4.0.x line, due Maven 3 backward compatibility, cannot disrupt a lot (as it must 
support Maven 3 plugins and work with most of the existing builds out there), but is about to get first class support 
for JPMS among many other things.

## Problems with Maven 

The biggest problem of Maven today is simple: **lack of resources**. And due lack of resources, Maven suffers from:

* stale or incomplete documentation (there is huge ongoing effort on this)
* users getting lost in that above, or reading ancient Stack Overflow entries (as Maven itself exists for 20 years),
  getting wrong conclusions, learning the "bad way" (or rather: "it should not be done like that anymore" ways)
* users blogging, posting about Maven bringing up misinformation. We have a nice, for some maybe "archaic" [mailing lists](https://maven.apache.org/mailing-lists.html), 
  where anyone can ask! But there is also [Maveniverse discussions](https://github.com/orgs/maveniverse/discussions) if you find it more convenient.

And we cannot sort all of these, and many more issues in one go (plus, we should also work on Maven 4 codebase).
On related note, even Maven 3.9.x line [got myriad of improvements](https://cwiki.apache.org/confluence/display/MAVEN/Notes+for+Maven+3.9.x+users), that were never properly communicated by us.

Any help is warmly welcome and appreciated!

## So, what is the response to Pom-Pom-Pom?

To find it out, wait for part 2. This above was only very brief history of POM file "proliferation".
