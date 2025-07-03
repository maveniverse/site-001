---
title: Heimdall (Heimdallr)
description: Filtering at next level!
categories: [Heimdall, Documentation]
tags: [heimdall, docs]
weight: 90
---

{{% pageinfo %}}
Heimdall enhances [Maven Remote Repository Filtering](https://maven.apache.org/resolver/remote-repository-filtering.html) (RRF) feature tremendously. The RRF feature is present
in Apache Maven since 3.9.0 release.
{{% /pageinfo %}}

Maveniverse Heimdall hooks into Resolver and enhances filtering the remote repositories.

Sources: https://github.com/maveniverse/heimdall

The main differences from "vanilla" RRF are:
* Prefix files **does not have to be checked in with sources**, is automatically discovered, fetched and cached for you
* Group files **got enhancements, and are much more expressive and powerful**.

Just by loading the extension, prefix filter will auto-activate itself and will fetch and cache (according Maven
update policies) the prefix files for you. This immediately means that remote repositories that offer prefix files 
(like Central, ASF forge, Eclipse forge, etc) will not be asked by your build to deliver files they don't have, 
this is "win-win" for both parties: your build is faster (no need to wait for HTTP 404s) and target repo is relieved 
of sending 404s for stuff not there.

If you configure group filters as well, you can fully control which Maven Artifact groupIDs are allowed (or not) to come
from given remote repository, making your build even faster by making Maven knowledgeable where to get stuff from.

The IT included is based on "oldie" [RRF demo](https://github.com/cstamas/rrf-demo), but Heimdall will of course
happily work with "vanilla" RRF as well.

Note: using Resolver filters (thet need to be explicitly enabled) along with Heimdall is not recommended.
