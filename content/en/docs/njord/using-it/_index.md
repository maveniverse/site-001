---
title: Using it
description: Using Njord!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 20
---

Short explanation how to use Njord. It is totally non-invasive, but still you can integrate it as well with your
project. The example below is not touching (modifying) the project it is about to publish.

## Setting it up

With Maven 3 create project-wide, or with Maven 4+ create user-wide `~/.m2/extensions.xml` like this:
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

Next, set up authentication. Different publishers require different server, for example `sonatype-cp` publisher
needs following stanza in your `settings.xml`:

```xml
    <server>
      <id>sonatype-cp</id>
      <username>USER_TOKEN_PT1</username>
      <password>USER_TOKEN_PT2</password>
    </server>
```

Supported publishers and corresponding `server.id`s are:

| Publisher (publisher ID)                                        | server.id               | What is needed                                                                                                                               |
|----------------------------------------------------------------|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Sonatype Central Portal (`sonatype-cp`)                        | `sonatype-cp`           | Obtain tokens for publishing by following [this documentation](https://central.sonatype.org/publish/generate-portal-token/).                 |
| Sonatype OSS on https://oss.sonatype.org/ (`sonatype-oss`)     | `sonatype-oss`          | Obtain tokens for publishing by following [this documentation](https://central.sonatype.org/publish/generate-token/) and using OSS instance. |
| Sonatype S01 on https://s01.oss.sonatype.org/ (`sonatype-s01`) | `sonatype-s01`          | As above but using S01 instance.                                                                                                             |
| Apache RAO on (`apache-rao`)                                   | `apache.releases.https` | As above but using RAO instance.                                                                                                             |

Make sure your `settings.xml` contains token associated with proper `server.id` corresponding to you publishing service you want to use.

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
