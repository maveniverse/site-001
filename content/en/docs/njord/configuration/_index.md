---
title: Configuring it
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 30
---

Njord uses existing Maven infrastructure to get the configuration, still a bit more explanation is needed for some bits.

For start, user interacts with Njord via `njord:` URI using vanilla Maven plugins like `maven-deploy-plugin` is, and
also using `njord-maven-plugin` goals. All the mojos **do not require projects** to be run (and are also aggregator
Mojos). Still, IF goals are invoked with Maven Project present (ie in a checkout where POM is present, and Maven loads
it) the Project will be used as "extra contextual source" for some operations.

## Njord basedir

By default, Njord uses `~/.njord` directory (in user home) directory as basedir. All the stores (locally staged artifacts)
are here. This directory may also contain a plain Java properties file `njord.properties` to define some workstation-wide
Njord configuration (usually not needed). The file full path is `~/.njord/njord.properties`.

## Njord properties

Njord merges properties from the following sources to calculate effective (configuration) properties:
1. Maven system properties (from Java system properties and environment variables)
2. Njord system-wide properties (from `~/.njord/njord.properties`)
3. Server configuration, **only for some properties which are annotated below** (from effective server with the given server id in [`settings.xml`](https://maven.apache.org/settings.html)) 
4. Maven project properties (if present)
5. Maven user properties

This implies, that if you want to define for example `njord.dryRun` property, you can achieve it in multiple ways: it is
possible even to have it in (effective) Project properties set by some profile. But be warned: in this example case, the 
property will be defined ONLY if you invoke Njord Mojos in this very same project using very same active profiles!
Basic Maven stuff.

Of course, the recommended way to set this very property from example is Maven user property like `mvn -Dnjord.dryRun ...`.

### Njord Server Configurations

Some properties may be added to the Maven `[settings.xml]` like this

```
    <server>
      <id>sonatype-central-portal</id>
      <username>$TOKEN1</username>
      <password>$TOKEN2</password>
      <configuration>
        <njord.publisher>sonatype-cp</njord.publisher>
        <njord.releaseUrl>njord:template:release-sca</njord.releaseUrl>
        <njord.snapshotUrl>njord:template:snapshot-sca</njord.snapshotUrl>
      </configuration>
    </server>
```

The server id used for the lookup is determined from `project.distributionManagement.repository.id` / `project.distributionManagement.snapshotRepository.id`. 

In addition the used server can be redirected with
`njord.serviceRedirect` (or if not set with `njord.authRedirect`, the latter only effective for credentials).
The redirect properties (`njord.serviceRedirect` and `njord.authRedirect`) must be used exclusively inside the server configuration of `settings.xml` and lead to only leveraging the configuration/authentication from the server id contained in the redirect property.

### Global properties

The following properties are applicable irrespective of the actual publisher being used.

Name | Description | Default Value | Mandatory | Optionally sourced from `settings.xml`
--- | --- | --- | --- | ---
`njord.enabled` | Boolean flag determining whether Njord should be active at all. | `true` | `no` | `no`
`njord.dryRun` | Boolean flag determining whether Njord should prevent actual publishing. | `false` | `no` | `no`
`njord.autoPublish` | Boolean flag determining whether publication should happen automatically at the end of the session. | `false` | `no` | `no`
`njord.autoDrop` | Boolean flag determining whether a local staging should be automatically dropped after publishing. | `true` | `no` | `no`
`njord.prefix`| The prefix to use for local Njord stores/staging repositories. | Determined from `<top level project>.artifactId` | `no` | `no`
`njord.publisher` | The publisher to use with this repository. Supported publisher ids listed in [Using it](../using-it/). | not set | `yes` | `yes`
`njord.releaseUrl` | The url identifying the local Njord store/staging repository for release artifacts. Must always start with `njord:`. For details on the URI format refer to [What is it](../what-is-it/). | Determined from `project.distributionManagement.repository.url` | `yes` | `yes`
`njord.snapshotUrl` | The url identifying the local Njord store/staging repository for SNAPSHOT artifacts. Must always start with `njord:`. For details on the URI format refer to [What is it](../what-is-it/). | Determined from `project.distributionManagement.snapshotRepository.url` | `yes` (only if Njord should be used with Snapshots, one can continue to use `maven-deploy-plugin` for SNAPSHOTs) | `yes`
`njord.authRedirect` | Id of the server from which to retrieve the credentials from [Maven's `settings.xml`](https://maven.apache.org/settings.html) instead of the one determined by `project.distributionManagement.repository.id` / `project.distributionManagement.snapshotRepository.id`. Only used if `njord.serviceRedirect` is not set. | - | `no` | `exclusively`
`njord.serviceRedirect` | Id of the server from which to retrieve Njord properties from [Maven's `settings.xml`](https://maven.apache.org/settings.html) instead of the one determined by `project.distributionManagement.repository.id` / `project.distributionManagement.snapshotRepository.id`. | - | `no` | `exclusively`

### Publisher specific properties

There are some properties only evaluated with certain publishers.
The most relevant ones are listed below. None of them are mandatory though.
For the full list look at the source code.

#### Sonatype Central Portal Publisher

Name | Alias | Description | Default Value 
--- | --- | --- | ---
`njord.publisher.sonatype-cp.publishingType` | `njord.publishingType` | Either `automatic` or `user_managed`. See <https://central.sonatype.org/publish/publish-portal-api/#uploading-a-deployment-bundle> for details. | `user_managed`
`njord.publisher.sonatype-cp.waitForStates` | `njord.waitForStates` | Boolean flag determining whether publishing should block until deployment reached the final state. Makes the publishing fail in case the final state is an error state. | `false` | `no`


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
