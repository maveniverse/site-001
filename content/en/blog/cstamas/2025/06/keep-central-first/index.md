---
title: "Keep Central first!"
date: 2025-06-12T14:20:23+01:00
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

Things like [`itr` option](https://issues.apache.org/jira/browse/MNG-8030) or using [Maven RRF](https://maven.apache.org/resolver/remote-repository-filtering.html)
would be next things to consider.