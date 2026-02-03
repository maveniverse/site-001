---
title: How to use it?
description: Filtering at next level!
categories: [Documentation]
tags: [docs]
projects: [ Heimdall ]
weight: 30
---

Simplest way to use Heimdall is using it as build extension: Just create a file `.mvn/extensions.xml` in your project
(or add it if you already have this file):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.heimdall</groupId>
        <artifactId>extension3</artifactId>
        <version>${heimdallVersion}</version>
    </extension>
</extensions>
```

With this one step, you are fully set up and protected from generating 404s on remote repositories if they publish
prefix files (those not publishing will be used "as before"). Now just go and fire up a Maven or Maven Daemon build.

When you added this extension, prefix filter will auto activate and pull/cache prefix files it founds, and will use
them (functionality from this point on is equal to the Apache Maven RRF, with difference that you do not have to
check in potentially huge prefixes file to your source).

## Prefix filtering

Prefix filtering does not require much user intervention: it makes use of remote repository published prefix files.

Examples of those are:
* Maven Central https://repo.maven.apache.org/maven2/.meta/prefixes.txt
* ASF RAO Snapshots https://repository.apache.org/content/repositories/snapshots/.meta/prefixes.txt
* Eclipse Tycho https://repo.eclipse.org/content/repositories/tycho/.meta/prefixes.txt

When Heimdall discovers these files, it will pull them and cache (applying all the Maven caching policies) and use them
for their origin repositories.

In short, "prefix file" contains path prefix entries per one line. Those are NOT Maven coordinates! Prefix files can
be 2, 3 or more path segments deep (usually are 2).

Maven will never ask a remote repository with prefix file for an artifact **known to not be there**.  

For example, take Eclipse Tycho repository above: its prefix file contains one notable entry: `org/eclipse`. This tells
Maven that the repo has artifacts which path starts with `org/eclipse/...`. Having this information, Maven will never
go and reach Tycho repository in relation of any `org.apache` artifact, for example.

> Prefix file is not about "it is 100% here" type of information, in fact, it is the opposite: it is telling 
> "it is 100% not here". By not having artifact layout path segments listed here, repository states 
> "do not bother coming to me".

## Maven groupId filtering

> If you're using other remote repositories, not only Maven Central, this may come very handy!

While prefix filtering is about _paths_, group ID filtering is about Maven group IDs.

You can "fine-tune" group filtering per project level, or globally (user wide). To tune group filtering on project
level, few steps more is needed. First, tell Heimdall where the group filter file configurations are:

Create `.mvn/maven.config` (or add to, if already exist) following entry:

```
-Dheimdall.groupId.basedir=${session.rootDirectory}/.mvn/rrf/
```

This will make Heimdall to look for group filter configurations in this repository (it is top level `.mvn/rrf`). Next,
create filter rules/configurations. You build may contain other remote repository definitions, or even more, your
dependency may pull in POM that defines one, making Maven "wander off". To figure out all remote repositories in
play on your build, run this command:

```
$ mvn toolbox:list-repositories
```

This will list all the repositories considered to pull dependencies. Now that you know the list of repositories,
you can simply prepare filters as well: each file has path like this:

```
.mvn/rrf/groupId-${repositoryId}.txt
```

If the file is matched with remote repository ID, it is loaded up and used. For repositories not having matched file,
no groupId filtering happens.

Contents of the file list Maven groupIDs with some extra information, examples below (numbering should NOT be in file,
is just for reference):

```
com.atlassian         (1)
=com.atlassian        (2)
!com.atlassian.foo    (3)
!=com.atlassian.foo   (4)
```
Legend:
* First line means: allow groupId `com.atlassian` and all below (so, `com.atlassian.foo` as well etc).
* Second line means: allow groupId`com.atlassian` **exactly and only** and nothing below.
* Third line means: disallow groupId `com.atlassian.foo` and all below.
* Fourth line means: disallow groupId `com.atlassian.foo` **exactly and only**. 
