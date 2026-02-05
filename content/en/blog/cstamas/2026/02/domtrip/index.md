---
title: "DOMTrip"
date: 2026-02-05T15:07:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
  - pom
projects:
  - DOMTrip
---

{{% pageinfo %}}

Round-trip editing is a programmatic changing/editing of an existing XML document, like for example a Maven POM is, while
preserving all the formatting, comments and all properties of the original document.

{{% /pageinfo %}}

Programmatic "editing" of POMs and other Maven related (mostly XML) files was long time requirement. Just think about
Maven Release Plugin that "rewrites" the version of project during release process.

Moreover, as Maven 4 is coming, the good old Xpp3Dom parser was out of the question, as Maven 4 model contains
substantial changes, and moreover, is not using anymore the Xpp3Dom parser, but the Woodstox XML parser instead.
Still, Maven universe, and especially legacy Maven universe was not always "good citizen" when it comes to XML, many
POMs have to be "lax parsed", as they had (known or unknown) issues. 

Historically, the best choice for "round-trip editing" was [DecentXML](https://central.sonatype.com/artifact/de.pdark/decentxml/versions), a project that since died off. It was used
(and AFAIK, still is) by Eclipse M2E and Tycho. We ignored this library, given it seems dead and unmaintained, last release of it happened
in 2014, and there is no available canonical source repository for it either (only some unmaintained forks on GH).

Next, Maven itself (like the release plugin) uses JDom2. We tried to adopt it, but it was really suitable for "smaller 
edits", like version setting in case of release plugin. And also had issues. Curious ones can read the lengthy
discussion on [Maven Release Plugin issue](https://github.com/apache/maven-release/issues/1381), why JDom2 does not work for us.

There are many other libraries doing similar thing to our requirements, we tried them all and we dropped them all.
Some of these are:
* Pom Tuner https://github.com/l2x6/pom-tuner
* PME https://github.com/project-ncl/pom-manipulation-ext
* Maven Model Helper https://github.com/fabric8io/maven-model-helper
* (deprecated before release) Nielsen https://github.com/maveniverse/nielsen (uses JDom2, and this codebase has long history: origins are from Maven release and other plugins plugin, that were collected and forked and improved by one Maven PMC member, that were forked and improved by a German team, and was finally forked and somewhat improved by me in Maveniverse Nielsen, but it was never released it; is superseded by DOMTrip)

But none of these suited to us. Our goals were:
* do not depend on any Maven internal nor legacy stuff (like Model or Xpp3Dom)
* ideally, to not have any dependency, or just minimal ones
* to 100% support lossless round-tripping and editing
* to support most of Maven related files (hence, XML, with some "extras" for Maven specific stuff)

In fact, it was DecentXML, that was closest to our expectations, but that project was abandoned. Hence, we came up with DOMTrip:
* Sources https://github.com/maveniverse/domtrip
* Site https://maveniverse.github.io/domtrip/

DOMTrip is a Java 17 library that:
* has no dependencies
* does full and lossless round-trip editing
* supports general (laxed) XML, with extra support for Maven files like POM, Settings, Toolchains and Extensions XML files
* offers "low level" and "high level" operations

For example, DOMTrip is being used when you run `mvn toolbox:versions -Dapply` (to apply version upgrades to POM) for example. It will
"edit" your POM, but you still need to review and eventually commit the changes.

Just to give some perspective about "high level" operations, let me give you an example: assume you know that POM
contains a plugin GA with version V1. And you want to upgrade that plugin to version V2. To achieve this, one pay
use `boolean updatePlugin(boolean upsert, Coordinates coordinates)` method of `POMEditor`. This method will perform
following steps for you (while keeping all the formatting and comments of POM): It will look for GA plugin in 
`project/build/plugins`, and if found, and version present, and is not a property, will update it, and work is done.
But, if version is a property, DOMTrip will go and update the property. Finally, if version is not even present, 
will go to `project/build/pluginManagement/plugins` and rinse, repeat. Is smart.

Have fun with it!
