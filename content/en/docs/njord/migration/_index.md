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
      <id>sonatype-cp</id>
      <username>$TOKEN1</username>
      <password>$TOKEN2</password>
    </server>
```

And that's it! Your `settings.xml` now contains auth for Sonatype Central Portal.

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
      <id>myproject-publish</id>
      <name>My Project Snapshots</name>
      <url>https://central.sonatype.com/repository/maven-snapshots</url>
    </snapshotRepository>
    <repository>
      <id>myproject-publish</id>
      <name>My Project Releases</name>
      <url>https://repo.maven.apache.org/maven2</url>
    </repository>
</distributionManagement>
```

Yes, you see it right: POM now says the truth: "we publish to Central". Also, there is no need to distinguish server for "release" 
and "snapshot" anymore. Next, let's make same changes in Maven user settings: add following entry to your `settings.xml`:

```xml
   <server>
     <id>myproject-publish</id>
     <configuration>
       <!-- Auth redirect -->
       <njord.authRedirect>sonatype-cp</njord.authRedirect>
       <!-- Sonatype Central Portal publisher -->
       <njord.publisher>sonatype-cp</njord.publisher>
       <!-- Releases are staged locally (if omitted, would go directly to URL as per POM) -->
       <njord.releaseUrl>njord:template:release-sca</njord.releaseUrl>
       <!-- Snapshots are staged locally (if omitted, would go directly to URL as per POM) -->
       <njord.snapshotUrl>njord:template:snapshot-sca</njord.snapshotUrl>
     </configuration>
   </server>
```

And you are done!

## Extension

Finally, you need to make sure that Njord extension is loaded as extension. As POM/build/extensions:

```xml
    <extensions>
      <extension>
        <groupId>eu.maveniverse.maven.njord</groupId>
        <artifactId>extension</artifactId>
        <version>${maveniverse.release.njordVersion}</version>
      </extension>
    </extensions>
```

or as core extension:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.njord</groupId>
        <artifactId>extension</artifactId>
        <version>${maveniverse.release.njordVersion}</version>
    </extension>
</extensions>
```

If you are putting Njord into POM, it is recommended to tie plugin version to extension version, by adding
plugin management entry to POM/build/pluginManagement/plugins as:

```xml
        <plugin>
          <groupId>eu.maveniverse.maven.plugins</groupId>
          <artifactId>njord</artifactId>
          <version>${maveniverse.release.njordVersion}</version>
        </plugin>
```


## Publish it!

With this setup, you just perform `mvn deploy` as you did before. It will locally stage. To publish, just use
`mvn njord:publish`. Or just do `mvn deploy -Dnjord.autoPublish`.

Check out [Maven generated plugin documentation](../plugin-documentation/plugin-info.html) for more mojos.