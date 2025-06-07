---
title: Migrating projects
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 40
---

Here will try to explain required steps to migrate your project to Njord. Assuming Maven basic knowledge, and some
experience about existing publishing to Central, using phased out services like Sonatype OSS or Sonatype S01 are.
Also, assuming you do have a project already, set up and probably published used via these legacy services.

## Setup your namespace on Sonatype portal

Not much to say here, [just follow the guide](https://central.sonatype.org/register/central-portal/).
**Do not forget to enable SNAPSHOTS for namespace**, if you intend to use them.

Edit your `settings.xml` and add your tokens to it. One of the main goals of Njord is **to prevent** copy-pasta
happening in your Maven Settings. Users publishing one namespace may not experience this, but users publishing multiple
namespaces are currently forced to copy-paste their auth tokens, as each project usually "invent" their own
distribution management server IDs (exception is ASF, where ASF parent POM contains "well known" server ID).

Hence, Njord recommend to name and store your tokens **only once** in your Maven Settings (this example is for
Sonatype Central Portal):

```xml
    <server>
      <id>sonatype-central-portal</id>
      <username>$TOKEN1</username>
      <password>$TOKEN2</password>
    </server>
```

Next, we will add a bit of Njord configuration: what publisher we want to use with this server, and what templates.
Edit the server entry above to contain something like this:

```xml
    <server>
      <id>sonatype-central-portal</id>
      <username>$TOKEN1</username>
      <password>$TOKEN2</password>
      <configuration>
        <!-- Sonatype Central Portal publisher -->
        <njord.publisher>sonatype-cp</njord.publisher>
        <!-- Releases are staged locally (if omitted, would go directly to URL as per POM) -->
        <njord.releaseUrl>njord:template:release-sca</njord.releaseUrl>
        <!-- Only if you want snapshots locally staged (if omitted, would go directly to URL as per POM) -->
        <njord.snapshotUrl>njord:template:snapshot-sca</njord.snapshotUrl>
      </configuration>
    </server>
```

One more nit, for simplicity sake:

```xml
  <pluginGroups>
    <pluginGroup>eu.maveniverse.maven.plugins</pluginGroup>
  </pluginGroups>
```

To not have to type plugin G on each invocation (this is not mandatory, but makes life easier).

And that's it! Your `settings.xml` now contains auth for Sonatype Central Portal, and also tells Njord which publisher
to use with this server (it is `sonatype-cp`), and which templates to use.

Note: if you want to use Central Portal Snapshots feature, then don't forget to first enable these on Portal Web UI.
Next, in that case you can remove the `njord.snapshotUrl` element, and enjoy "direct deploy" (so Njord does not 
meddle, or stage snapshots). Maven will go directly for Central Portal Snapshot endpoint. Any service that supports
SNAPSHOT deploy and accepts `maven-deploy-plugin` deploy requests may be left without `njord.snapshotUrl` configuration
as in that case that good old deploy plugin can do the job as well, no Njord needed.

## Setup your project

As your project was already published to Central, the POM may contain distribution management like this:

```xml
  <distributionManagement>
    <snapshotRepository>
      <id>myproject-snapshots</id>
      <name>My Project Snapshots</name>
      <url>https://oss.sonatype.org/content/repositories/snapshots/</url>
    </snapshotRepository>
    <repository>
      <id>myproject-releases</id>
      <name>My Project Releases</name>
      <url>https://oss.sonatype.org/service/local/staging/deploy/maven2/</url>
    </repository>
  </distributionManagement>
```

**You do not have to change anything!**. But, it is worth to change it. For start, the URLs for releases here are "fake",
and some tools like SBOM engines cannot use them as intended, as the URL is not "where artifacts are published", it is 
"service used to publish" instead. It is recommended to change this POM section into something like this:

```xml
  <distributionManagement>
    <snapshotRepository>
      <id>sonatype-central-portal</id>
      <name>My Project Snapshots</name>
      <url>https://central.sonatype.com/repository/maven-snapshots</url>
    </snapshotRepository>
    <repository>
      <id>sonatype-central-portal</id>
      <name>My Project Releases</name>
      <url>https://repo.maven.apache.org/maven2</url>
    </repository>
</distributionManagement>
```

Yes, you see it right: POM now says the truth: "we publish to Central" and "we use Sonatype Central Portal" service. 
Also, there is no need to distinguish server for "release" and "snapshot".

Finally, IF you have some existing plugin that did the job before, just remove, and undo all the hoops and loops that
the plugin or tool required (like adding some properties, profiles, whatnot).

And you are done!

## Extension

Finally, you need to make sure that Njord extension is loaded as extension. Ideally as POM project/build/extensions:

```xml
    <properties>
      <version.njord>VERSION</version.njord>
    </properties>

    <build>
    <extensions>
      <extension>
        <groupId>eu.maveniverse.maven.njord</groupId>
        <artifactId>extension</artifactId>
        <version>${version.njord}</version>
      </extension>
    </extensions>
    <pluginManagement>
      <plugins>
        <plugin>
          <groupId>eu.maveniverse.maven.plugins</groupId>
          <artifactId>njord</artifactId>
          <version>${version.njord}</version>
        </plugin>
      </plugins>
    </pluginManagement>
```

But you can do it as core extension, in `.mvn/extensions.xml` or Maven 4 user wide `~/.m2/extensions.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.njord</groupId>
        <artifactId>extension</artifactId>
        <version>VERSION</version>
    </extension>
</extensions>
```

## Summary

To get summary, invoke `mvn njord:status`.

Note: this line above will work for you as-is IF you added `pluginGroup` to your `settings.xml`.

It will tell you all publishing related information about your project, even is the auth present or not (ie you may
have a typo in server.id in POM or your `settings.xml`).

With this setup as above, one should see output like this (example is from [BOM builder plugin](../../bom_builder_maven_plugin)),
with added right hand "annotated explanations":

```
[cstamas@angeleyes bom-builder-maven-plugin (master)]$ mvn njord:status
[INFO] Scanning for projects...
[INFO] Njord 0.6.0 session created
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Build Order:
[INFO] 
[INFO] eu.maveniverse.maven.bom-builder:bom-builder                       [pom]
[INFO] eu.maveniverse.maven.plugins:bom-builder3                 [maven-plugin]
[INFO] eu.maveniverse.maven.bom-builder:it3                               [pom]
[INFO] 
[INFO] ------------< eu.maveniverse.maven.bom-builder:bom-builder >------------
[INFO] Building eu.maveniverse.maven.bom-builder:bom-builder 1.1.1-SNAPSHOT [1/3]
[INFO]   from pom.xml
[INFO] --------------------------------[ pom ]---------------------------------
[INFO] 
[INFO] --- njord:0.6.0:status (default-cli) @ bom-builder ---
[INFO] Project deployment:
[INFO]   Store prefix: bom-builder  <------------------------------------------------ store prefix, build-builder-00001, etc
[INFO] * Release
[INFO]   Repository Id: sonatype-central-portal
[INFO]   Repository Auth: Present  <------------------------------------------------- auth is present
[INFO]   POM URL: https://repo.maven.apache.org/maven2/  <--------------------------- POM "truth", once published, artifacts are here
[INFO]   Effective URL: njord:template:release-sca  <-------------------------------- The Njord URL we use when deploy releases
[INFO] - release-sca  <-------------------------------------------------------------- The template we set, detailed
[INFO]     Default prefix: 'bom-builder'
[INFO]     Allow redeploy: false
[INFO]     Checksum Factories: [SHA-512, SHA-256, SHA-1, MD5]
[INFO]     Omit checksums for: [.asc, .sigstore, .sigstore.json]
[INFO] * Snapshot
[INFO]   Repository Id: sonatype-central-portal
[INFO]   Repository Auth: Present
[INFO]   POM URL: https://central.sonatype.com/repository/maven-snapshots/  <-------- Snapshots do not use Njord, mvn deploy deploys directly Portal
[INFO] 
[INFO] No candidate artifact stores found  <----------------------------------------- Nothing has been locally staged yet
[INFO] 
[INFO] Project publishing:
[INFO] - 'sonatype-cp' -> Publishes to Sonatype Central Portal  <-------------------- The publishing service we set, detailed
[INFO]   Checksums:
[INFO]     Mandatory: SHA-1, MD5
[INFO]     Supported: SHA-512, SHA-256
[INFO]   Signatures:
[INFO]     Mandatory: GPG
[INFO]     Supported: Sigstore
[INFO]   Published artifacts will be available from:
[INFO]     RELEASES:  central @ https://repo.maven.apache.org/maven2/
[INFO]     SNAPSHOTS: sonatype-central-portal @ https://central.sonatype.com/repository/maven-snapshots
[INFO]   Service endpoints:
[INFO]     RELEASES:  sonatype-central-portal @ https://central.sonatype.com/api/v1/publisher/upload
[INFO]     SNAPSHOTS: sonatype-central-portal @ https://central.sonatype.com/repository/maven-snapshots
[INFO] 
[INFO] ------------------------------------------------------------------------
[INFO] Reactor Summary for eu.maveniverse.maven.bom-builder:bom-builder 1.1.1-SNAPSHOT:
[INFO] 
[INFO] eu.maveniverse.maven.bom-builder:bom-builder ....... SUCCESS [  0.037 s]
[INFO] eu.maveniverse.maven.plugins:bom-builder3 .......... SKIPPED
[INFO] eu.maveniverse.maven.bom-builder:it3 ............... SKIPPED
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  0.329 s
[INFO] Finished at: 2025-05-24T22:49:03+02:00
[INFO] ------------------------------------------------------------------------
[INFO] Njord session closed
[cstamas@angeleyes bom-builder-maven-plugin (master)]$ 
```

## Publish it!

With this setup, you just perform `mvn deploy` as you did before. If your checkout is snapshot, you will deploy to
Central Portal Snapshots. If your checkout is a release, it will be locally staged once Maven finishes. 

To publish, just use `mvn njord:publish`, or just do `mvn deploy -Dnjord.autoPublish`.

Once Maven returns, your project is being validated at https://central.sonatype.com/publishing

Check out [Maven generated plugin documentation](../plugin-documentation/plugin-info.html) for more mojos.

## What if don't want (or cannot) change the POM?

In this case Njord can still be used, but the "inconvenience" is that you need to hand over all info to Njord.

The maven user settings change is **mandatory**, you need to have tokens set in your `settings.xml`.

The presence of Njord extension is **mandatory** as well, You can load it as user-wide extension (`~/m2/extensions.xml`)
if you use Maven 4 or you can create (or edit if exists) project `.mvn/extensions.xml`.

Below I assume you work with a release checkout (ie you checked out a tag, also the "release profile" in this example
follow ASF convention):

```
$ mvn -P apache-release deploy \                                                     1)
         -DaltDeploymentRepository=id::njord: \                                      2)
         -Dnjord.autoPublish \                                                       3)
         -Dnjord.publisher=sonatype-cp \                                             4)
         -Dnjord.publisher.sonatype-cp.releaseRepositoryId=sonatype-central-portal   5)
```

So what happens here? We invoke "deploy for release" (1), but using "alternate deployment repository" (2),
that will create an artifact store from default template. Note that `id::url` form is standard format accepted
by `maven-deploy-plugin` but the `id` is in fact unused, as store ID will be known only after it is created.
At session end (3) the created store with deployed artifacts will be published, using specified publisher service (4) 
and auth material from specified server (5) in user `settings.xml`.
