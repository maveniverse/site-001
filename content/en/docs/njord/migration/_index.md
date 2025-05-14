---
title: Migrating project to Njord and Central Portal
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 40
---

Here will try to explain required steps to migrate your project to Njord. Assuming Maven basic knowledge, and some
experience about existing publishing to Central, using phased out services like Sonatype OSS or Sonatype S01 are.

## Setup your namespace on Sonatype portal

Not much to say here, [just follow the guide](https://central.sonatype.org/register/central-portal/).

Grab your publishing tokens. Also, **do not forget to enable SNAPSHOTS for namespace**, if you intend to use them.

