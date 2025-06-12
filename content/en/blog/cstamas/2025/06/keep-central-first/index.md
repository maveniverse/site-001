---
title: "Keep Central first!"
date: 2025-06-12T12:20:23+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
projects:
  - Maven
---

Just an advice: when using Maven 3 (and 4) you do want to make sure Central is always first remote repository
Maven would "consult". Just add following snippet(s) to your user-wide `settings.xml`:

```xml
  <profiles>
    <profile>
      <id>oss-development</id>
      <repositories>
        <repository>
          <id>central</id>
          <url>https://repo.maven.apache.org/maven2/</url>
          <releases>
            <enabled>true</enabled>
            <updatePolicy>never</updatePolicy>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <id>central</id>
          <url>https://repo.maven.apache.org/maven2/</url>
          <releases>
            <enabled>true</enabled>
            <updatePolicy>never</updatePolicy>
          </releases>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </pluginRepository>
      </pluginRepositories>
    </profile>
  </profiles>

  <activeProfiles>
    <activeProfile>oss-development</activeProfile>
  </activeProfiles>
```

With this in your user with Maven settings, Maven will take care to keep Central first.

By default, Maven kees Remote Repositories ordered (like in a POM, it obeys the order), but globally, they are assembled
like this:
* settings/env
* project POM
* Maven defaults

This implies, that IF you are building a project whose POM contains even one repository stanza (and not having env like that
above) that is not Central, the POM defined repository will take precedence over Central. And many times, this is NOT what you want.

Things like [`itr` option](https://issues.apache.org/jira/browse/MNG-8030) or using [Maven RRF](https://maven.apache.org/resolver/remote-repository-filtering.html)
would be next things to consider.