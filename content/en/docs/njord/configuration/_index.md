---
title: Configuring it
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 30
---

Njord uses existing Maven infrastructure to get the configuration, still a bit more explanation is needed for some bits.

For start, user interacts with Njord via `njord:` URI using vanilla Maven plugins like `maven-deploy-plugin` is, and
also using `njord-maven-plugin` goals. All the mojos **does not require projects** to be run (and are also aggregator
Mojos). Still, IF goals are invoked with Maven Project present (ie in a checkout where POM is present, and Maven loads
it) the Project will be used as "extra contextual source" for some operations.

## Njord basedir

By default, Njord uses `~/.njord` directory (in user home) directory as basedir. All the stores (locally staged artifacts)
are here. This directory may also contain a plain Java properties file `njord.properties` to define some workstation-wide
Njord configuration (usually not needed). The file full path is `~/.njord/njord.properties`.

## Njord properties

Njord applies following "precedence" rule to calculate effective (configuration) properties:
* Maven system properties
* Njord system-wide properties (sourced from `~/.njord/njord.properties`)
* Maven project properties (if present)
* Maven user properties

This implies, that if you want to define for example `njord.dryRun` property, you can achieve it in multiple ways: it is
possible even to have it in (effective) Project properties set by some profile. But be warned: in this example case, the 
property will be defined ONLY if you invoke Njord Mojos in this very same project using very same active profiles!
Basic Maven stuff.

Of course, the recommended way to set this very property from example is Maven user property like `mvn -Dnjord.dryRun ...`.

## Project

Njord goals do **not require project**, and they can be invoked without any. But, in that case all the "heuristics" will be
unavailable, and you will need to provide all the required input to goals explicitly. For example, assuming you have 
locally staged `myproject-00001`, you can still publish it by explicitly configuring `publish` goal from a directory
where no project exists:

```
$ mvn njord:publish -Dstore=myproject=00001 -Dpublisher=sonatype-cp
```

Naturally, your user wide `settings.xml` should be configured for this: authentication tokens should be set for server `sonatype-cp`.

When project is present, it implies several things: 

First, "prefix" is known (top level project `artifactId`), in this 
example case, it would be `myproject`. When prefix is known, Njord will use simple heuristics, and will implicitly use 
last (newest) store prefixed with this prefix (so if you have `myproject-00001` and `myproject-00002` the latter would
be selected). 

Second, if project is present, and if `distributionManagement` is configured (usually is for projects being deployed), 
then Njord can deduce the publisher using the `server.id` from POM and the server configuration present in your `settings.xml`.
