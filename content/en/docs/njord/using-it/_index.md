---
title: Using it
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 20
---

Short explanation how to use Njord. It is totally non-invasive, but still you can integrate it as well with your
project. To prove it, there is example at end of this page.

There is only one **required thing**: the extension must be loaded when publishing. Still, the extension is non-invasive, and
remains fully dormant, does not interfere with your build at all, merely defines the `njord:` transport.

## Setting it up

Maveniverse Njord is a suite of Maven (core or build; works both ways) extension and a Maven Plugin. You should keep 
the versions of extension and plugin aligned. Simplest way to achieve this is to:

* create a property like version.njord in your parent POM carrying Njord version.
* adding a build/pluginManagement section with Njord plugin and version property.
* adding a build/extensions section wirh Njord extension and version property.

Depending on your needs, Njord can be defined in parent POMs but can also be "sideloaded" as user or project extension, 
maybe even only when you are about to publish (so not all the time).

If you want to add Njord to your parent POM, the recommended way is this:

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

Alternatively, with Maven 3 create project-wide, or with Maven 4+ create user-wide `~/.m2/extensions.xml` like this:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.njord</groupId>
        <artifactId>extension</artifactId>
        <version>${currentVersion}</version>
    </extension>
</extensions>
```

It is recommended (but not mandatory) to add this stanza to your `settings.xml` as well if you don't have it already
(to not type whole G of plugin):
```xml
  <pluginGroups>
    <pluginGroup>eu.maveniverse.maven.plugins</pluginGroup>
  </pluginGroups>
```

Next, set up authentication. Different publishers require different server, for example the recommended entry for
Sonatype Central Portal publishing service is following stanza in your `settings.xml` (assuming you enabled snapshots
on your namespace, and you wish directly to deploy to it, not locally stage them):

```xml
  <servers>
    <server>
      <id>sonatype-central-portal</id>
      <username>$TOKEN1</username>
      <password>$TOKEN2</password>
      <configuration>
        <njord.publisher>sonatype-cp</njord.publisher>
        <njord.releaseUrl>njord:template:release-sca</njord.releaseUrl>
      </configuration>
    </server>
  </servers>
```

Supported publishers are:

| Publisher (publisher ID)                                       | server.id               | What is needed                                                                                                                               |
|----------------------------------------------------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Sonatype Central Portal (`sonatype-cp`)                        | -                       | Obtain tokens for publishing by following [this documentation](https://central.sonatype.org/publish/generate-portal-token/).                 |
| Sonatype OSS on https://oss.sonatype.org/ (`sonatype-oss`)     | -                       | Obtain tokens for publishing by following [this documentation](https://central.sonatype.org/publish/generate-token/) and using OSS instance. |
| Sonatype S01 on https://s01.oss.sonatype.org/ (`sonatype-s01`) | -                       | As above but using S01 instance.                                                                                                             |
| Apache RAO on https://repository.apache.org/ (`apache-rao`)    | `apache.releases.https` | As above but using RAO instance.                                                                                                             |

Make sure your `settings.xml` contains token associated with proper `server.id` corresponding to you publishing service you want to use.

In case you are about to publish a project you cannot alter distribution management for some reason, and assuming 
Central Portal publishing is enabled for it, just add this stanza in your `settings.xml`:

```xml
     <server>
       <id>the-project-releases</id>
       <configuration>
         <njord.serviceRedirect>sonatype-central-portal</njord.serviceRedirect>
       </configuration>
     </server>
```

This basically **redirects** the server "the-project-release" (in POM that you are unable to change) to your defined
`sonatype-central-portal` entry.

That's all! No project change needed at all.

## Using it

Next, let's see an example of Apache Maven project (I used `maven-gpg-plugin`):

1. For example’s sake, I took last release of plugin (hence am simulating release deploy): `git checkout maven-gpg-plugin-3.2.7`
2. Deploy it (locally stage): `mvn -P apache-release deploy -DaltDeploymentRepository=id::njord:` (The `id` is really unused, is there just to fulfil deploy plugin syntax requirement. The URL `njord:` will use "default" store template that is RELEASE. You can target other templates by using, and is equivalent of this `njord:release`. You can stage locally snapshots as well with URL `njord:snapshot`. Finally, you can target existing store with `njord:store:storename-xxx`).
3. Check staged store names: `mvn njord:list`
4. Optionally, check locally staged content: `mvn njord:list-content -Dstore=release-xxx` (use store name from above)
5. Optionally, validate locally staged content: `mvn njord:validate -Ddetails -Dstore=release-xxx` (use store name from above)
6. Publish it to ASF: `mvn njord:publish -Dstore=release-xxx -Dtarget=apache-rao` (use store name from above)
7. From now on, the repository is staged on RAO, so you can close it, vote, and on vote pass, release it. All the usual fluff as before.
8. Drop locally staged store: `mvn njord:drop -Dstor=release-xxx` (use store name from above)

Check out [Maven generated plugin documentation](../plugin-documentation/plugin-info.html) for more mojos.