---
title: MASE
description: Maven Search
categories: [Documentation]
tags: [docs]
projects: [ MASE ]
weight: 20
---

{{% pageinfo %}}
Maven Search done simple.
{{% /pageinfo %}}

MASE ("Maven Search") is a fork of the [Maven Indexer](https://github.com/apache/maven-indexer) Search API, and a
drop-in replacement for it: switching requires only changing the `groupId` and `version`. The Search API offers a
simple Java API to search Maven Central and other repositories, using various backends.

The fork existed to allow faster prototyping. All its changes have since been merged back, and as of Maven Indexer
7.1.2 and MASE 1.0.1 the two are equivalent; the Search API from Maven Indexer is the recommended one to use.

Sources: https://github.com/maveniverse/mase
