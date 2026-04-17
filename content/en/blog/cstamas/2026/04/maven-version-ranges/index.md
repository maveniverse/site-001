---
title: "Taming Maven Version Ranges"
date: 2026-04-17T10:07:53+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - maven
  - resolver
  - version-range
projects:
  - Maven
---

Maven ranges are very controversial topic. If you ask anyone, the response most often is "do not use them". 
And while there are good reasons for that, there are also some use cases where they can be useful. 
So lets see how can Maven 3.10.x help with them.

## Problems

Biggest issue with ranges, is that when they are collected by resolver, following steps are applied:
* current POM processed dependency contains a version range, for example `[1.0,2.0)`
* resolver collects all versions of the dependency, for example `1.0`, `1.1`, `1.2` etc up to `2.0` (including alphas, snapshots... if such artifacts are in scope, for example snapshot repository is used for resolution)
* dirty graph gets nodes created for each version and builds subtree for each (given dependencies may differ across versions)
* finally, conflict resolver "choose" the winner node (version) and eliminates the rest.

From these, one can immediately notice several problems:
* potentially many downloads, this is the **"ranges slow down the build"** argument. This clearly happens, when the range
  resolves to many versions (as it is huge range, or project emits many versions or an old project with many range included releases).
* build reproducibility, as the range may resolve to different versions at different times, and thus, build may be 
  different at different times. This is the **"builds with ranges are not reproducible"** argument.

## Maven 3.10.x enters the dojo

With Maven 3.10.x, that brings in Resolver 2.x, things change. One of the new Resolver 2 features are version range filters.
In Maven 3.10.x, they will be exposed somewhat along these lines:
* user property, so they can be specified via CLI, or in `.mvn/maven.config` even
* filters can be defined as "list of expressions"

The expressions (this is still a PR so consider it WIP) are along these lines:

```java
    /**
     * User property for version filter expression used in session, applied to resolving ranges: a semicolon separated
     * list of filters to apply. By default, no version filter is applied (like in Maven 3).
     * <br/>
     * Supported filters:
     * <ul>
     *     <li>{@code "h"} or {@code "h(num)"} - highest version or top list of highest ones filter</li>
     *     <li>{@code "l"} or {@code "l(num)"} - lowest version or bottom list of lowest ones filter</li>
     *     <li>{@code "s"} - contextual snapshot filter</li>
     *     <li>{@code "ns"} - unconditional snapshot filter (no snapshots selected from ranges)</li>
     *     <li>{@code "np"} - unconditional preview filter (no previews selected from ranges)</li>
     *     <li>{@code "e(V)"} - predicate filter (excludes V from range, if hit, V can be version constraint)</li>
     *     <li>{@code "i(V)"} - predicate filter (includes V from range, if hit, V can be version constraint)</li>
     * </ul>
     * Every filter expression may have "scope" applied, in form of {@code @G[:A]}. Presence of "scope" narrows the
     * application of filter to given G or G:A.
     * <p>
     * In case of multiple "similar" rule scopes, user should enlist rules from "most specific" to "least specific".
     * <p>
     * Example filter expression: <code>"h(5);s;e(1)@org.foo:bar</code> will cause:
     * <ul>
     *     <li>ranges are filtered for "top 5" (instead of full range)</li>
     *     <li>snapshots are banned if root project is not a snapshot</li>
     *     <li>if range for <code>org.foo:bar</code> is being processed, version 1 is omitted</li>
     * </ul>
     * Values in this property builds <code>org.eclipse.aether.collection.VersionFilter</code> instance.
     *
     * @since 3.10.0
     */
    private static final String MAVEN_VERSION_FILTER = "maven.session.versionFilter";
```

In essence, filters are defined as semicolon separated string list of rules in form of `expression[;expression]*`, 
where expression consist of `filter[@scope]`. Filters are applied in left to right order, and if there are multiple filters with same 
scope, they should be ordered from "most specific" to "least specific".

Example filter expression: `h(5);s;e(1)@org.foo:bar` results in following behavior:
* ranges are globally filtered for "top 5" (instead of full range); so if there are 10 versions in range, only 5 highest will be considered for further processing
* snapshots are banned if root project is not a snapshot
* if range for `org.foo:bar` is being processed, version "1" is omitted

## Filter kinds

Rules helps you to more expressively define your range filters, instead of "keep tuning" you range, as new and 
new version appears, you can say "consider latest 5" (based on version comparison).

The `h` and `l` rules basically selects `highest N` and `lowest N` versions from the ordered versions discovered that fit
the range in question.

For example
* given the range `[1,2)`
* and discovered versions (`1.0`, `1.1`, `1.2`) (this part is changing as time passes, new and new releases are done)
* the `h(1)` would narrow the discovered versions to (`1.2`) while `l(1)` to (`1.0`).

The `s`, `ns` and `np` rules are related to snapshot and preview versions. The `s` rule is contextual, it bans snapshots 
if root project is not a snapshot, while allows them if root project is a snapshot. The `ns` rule is unconditional, 
it bans snapshots from ranges, no matter what the root project is. And finally, the `np` rule is also unconditional, 
but it bans preview versions ("alpha", "beta" and "milestone") from ranges.

For example
* given the range `[1,2)`
* and discovered versions (`1.0`, `1.1`, `1.2`, `2.0-alpha-1`, `2.0-SNAPSHOT`) (this part is changing as time passes, new and new releases are done)
* the `ns;np` would narrow the discovered versions to (`1.0`, `1.1`, `1.2`), as the two eliminates SNAPSHOT and preview versions.

The `e` and `i` rules are predicate filters, they exclude or include version from dependency constraint, if hit. 
The dependency constraint in these rules is applied to discovered versions that fit the range in question, and are 
excluded or included if they match the constraint.

For example
* given the range `[1,2)`
* and discovered versions (`1.0`, `1.1`, `1.2`, `1.3`, `1.4`) (this part is changing as time passes, new and new releases are done)
* the `e(1.1)` would narrow the discovered versions to (`1.0`, `1.2`, `1.3`, `1.4`), while `i([1,1.2),[1.3,2))` basically
  modifies original range to always leave out `1.2`.

## Filter scopes

Each filter can be appended by scope, in form of `@G[:A]`. Presence of scope **narrows** the application of filter to given 
`G` or `G:A`. If scope is not present, filter is applied globally.

Rule scoping allows you to target given range more narrowly, useful for `e` and `i` rules mostly, but they can
come handy for other rules as well.

## Example use case No1: Reproducible builds

So far, builds with ranges were deemed non-reproducible, as in the moment a new version popped up in some range 
was deployed, the build could resolve to different version, and thus, be different.

One example is this kind of build is **Cucumber 38.0.0** as can be [seen here; is marked as non reproducible](https://github.com/jvm-repo-rebuild/reproducible-central/blob/master/content/io/cucumber/gherkin/README.md).

Problem is [use of range](https://github.com/cucumber/gherkin/blob/v38.0.0/java/pom.xml#L57-L61) in the project POM for 
dependency `io.cucumber:messages`, and what happened was that when RB check was triggered, there was already a new 
version of `io.cucumber:messages` deployed to Central, and hence, the RB build picked it up.

By using Maven 3.10.x and doing "just a vanilla" build, we get the same result ([full log](https://gist.github.com/cstamas/23f44fc82ed8e58bc1ab1bf92b9046a0b)): failure

```
$ mvn -V -Dmaven.repo.local=../local package artifact:compare
Apache Maven 3.10.0-SNAPSHOT (a6b4930483fbaeb7508cd22faedfeebb6e020778)
Maven home: /home/cstamas/.sdkman/candidates/maven/latest-3
Java version: 21.0.10, vendor: Eclipse Adoptium, runtime: /home/cstamas/.sdkman/candidates/java/21.0.10-tem
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "6.19.12-200.fc43.x86_64", arch: "amd64", family: "unix"
[INFO] Scanning for projects...
[INFO] Loaded 22557 auto-discovered prefixes for remote repository central (prefixes-central.txt)
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
[INFO] Inspecting build with total of 1 modules
[INFO] Installing Central Publishing features
[INFO] 
[INFO] ------------------------< io.cucumber:gherkin >-------------------------
[INFO] Building Gherkin 38.0.0
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
...
[INFO] --- artifact:3.6.1:compare (default-cli) @ gherkin ---
[INFO] Saved info on build to /home/cstamas/tmp/gherkin/gherkin/java/target/gherkin-38.0.0.buildinfo
[INFO] Checking against reference build from central...
[INFO] Reference buildinfo file not found: it will be generated from downloaded reference artifacts
[INFO] Reference build java.version: 21 (from MANIFEST.MF Build-Jdk-Spec)
[INFO] Reference build os.name: Unix (from pom.properties newline)
[INFO] Minimal buildinfo generated from downloaded artifacts: /home/cstamas/tmp/gherkin/gherkin/java/target/reference/gherkin-38.0.0.buildinfo
[ERROR] size mismatch gherkin-38.0.0.jar: investigate with diffoscope target/reference/io.cucumber/gherkin-38.0.0.jar target/gherkin-38.0.0.jar
[ERROR] [Reproducible Builds] rebuild comparison result: 1 files match, 1 differ
[ERROR]                                                  saved to target/gherkin-38.0.0.buildcompare
[ERROR] [Reproducible Builds] to analyze the differences, see diffoscope instructions in target/gherkin-38.0.0.buildcompare
[ERROR]                       see also https://maven.apache.org/guides/mini/guide-reproducible-builds.html
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  7.098 s
[INFO] Finished at: 2026-04-17T11:16:07+02:00
[INFO] ------------------------------------------------------------------------
```
As obviously, we also are tripped on same "new" version as RB did. But, given **we know** what the issue is, we can easily fix
it by applying filter to the range `i(32.0.0)@io.cucumber:messages`:

```
[cstamas@angeleyes java ((go/v38.0.0) %)]$ mvn -V -Dmaven.repo.local=../local package artifact:compare -Dmaven.session.versionFilter="i(32.0.0)@io.cucumber:messages"
Apache Maven 3.10.0-SNAPSHOT (a6b4930483fbaeb7508cd22faedfeebb6e020778)
Maven home: /home/cstamas/.sdkman/candidates/maven/latest-3
Java version: 21.0.10, vendor: Eclipse Adoptium, runtime: /home/cstamas/.sdkman/candidates/java/21.0.10-tem
Default locale: en_US, platform encoding: UTF-8
OS name: "linux", version: "6.19.12-200.fc43.x86_64", arch: "amd64", family: "unix"
[INFO] Scanning for projects...
[INFO] Loaded 22557 auto-discovered prefixes for remote repository central (prefixes-central.txt)
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
[INFO] Inspecting build with total of 1 modules
[INFO] Installing Central Publishing features
[INFO] 
[INFO] ------------------------< io.cucumber:gherkin >-------------------------
[INFO] Building Gherkin 38.0.0
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
...
[INFO] --- artifact:3.6.1:compare (default-cli) @ gherkin ---
[INFO] Saved info on build to /home/cstamas/tmp/gherkin/gherkin/java/target/gherkin-38.0.0.buildinfo
[INFO] Checking against reference build from central...
[INFO] Reference buildinfo file not found: it will be generated from downloaded reference artifacts
[INFO] Reference build java.version: 21 (from MANIFEST.MF Build-Jdk-Spec)
[INFO] Reference build os.name: Unix (from pom.properties newline)
[INFO] Minimal buildinfo generated from downloaded artifacts: /home/cstamas/tmp/gherkin/gherkin/java/target/reference/gherkin-38.0.0.buildinfo
[INFO] [Reproducible Builds] rebuild comparison result: 2 files match
[INFO]                                                  saved to target/gherkin-38.0.0.buildcompare
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  7.287 s
[INFO] Finished at: 2026-04-17T11:15:08+02:00
[INFO] ------------------------------------------------------------------------
```

And we get the same build as deployed on Central. Hence, the **build is in fact reproducible**.

## Example use case No2: Speeding things up

Consider following trivial POM just for demo purposes:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://maven.apache.org/POM/4.0.0"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>org.cstamas</groupId>
  <artifactId>mtm-test</artifactId>
  <version>1.0.0-SNAPSHOT</version>
  <packaging>jar</packaging>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <project.build.outputTimestamp>2026-03-25T16:24:02Z</project.build.outputTimestamp>
    <maven.compiler.release>8</maven.compiler.release>

    <version.slf4j>[1.7.30,2)</version.slf4j>
  </properties>

  <dependencies>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>${version.slf4j}</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-simple</artifactId>
      <version>${version.slf4j}</version>
    </dependency>
  </dependencies>
</project>
```

In essence, we depend on range of `[1.7.30,2)` for both, `slf4j-api` and `slf4j-simple`. Given there are many 
versions of `slf4j` in that range, the resolver will have to work hard.

{{% pageinfo %}}

Note: between each execution we nuke the `org.slf4j` from local repository, to make obvious what Maven is tinkering to resolve.

{{% /pageinfo %}}


First, a "vanilla" build:

```
[cstamas@angeleyes mtm]$ rm -R local/org/slf4j/
[cstamas@angeleyes mtm]$ mvn verify -e -Dmaven.repo.local=local
[INFO] Error stacktraces are turned on.
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< org.cstamas:mtm-test >------------------------
[INFO] Building mtm-test 1.0.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] Loaded 22552 auto-discovered prefixes for remote repository central (prefixes-central.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml (4.1 kB at 22 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml (3.8 kB at 20 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta0/slf4j-api-2.0.0-beta0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha5/slf4j-simple-2.0.0-alpha5.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha1/slf4j-simple-1.8.0-alpha1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha3/slf4j-simple-2.0.0-alpha3.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha1/slf4j-api-1.8.0-alpha1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha3/slf4j-api-2.0.0-alpha3.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha0/slf4j-api-2.0.0-alpha0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta4/slf4j-simple-1.8.0-beta4.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha5/slf4j-api-2.0.0-alpha5.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha4/slf4j-simple-2.0.0-alpha4.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha0/slf4j-simple-2.0.0-alpha0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta4/slf4j-api-1.8.0-beta4.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha6/slf4j-api-2.0.0-alpha6.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta1/slf4j-simple-2.0.0-beta1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha7/slf4j-api-2.0.0-alpha7.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha2/slf4j-simple-2.0.0-alpha2.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha1/slf4j-api-2.0.0-alpha1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha2/slf4j-api-2.0.0-alpha2.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha6/slf4j-simple-2.0.0-alpha6.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta1/slf4j-api-2.0.0-beta1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta0/slf4j-simple-2.0.0-beta0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha4/slf4j-api-2.0.0-alpha4.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta2/slf4j-api-1.8.0-beta2.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta2/slf4j-simple-1.8.0-beta2.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha5/slf4j-simple-2.0.0-alpha5.pom (1.1 kB at 28 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha5/slf4j-parent-2.0.0-alpha5.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha3/slf4j-simple-2.0.0-alpha3.pom (1.1 kB at 26 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha3/slf4j-parent-2.0.0-alpha3.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha5/slf4j-parent-2.0.0-alpha5.pom (17 kB at 438 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha7/slf4j-simple-2.0.0-alpha7.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha1/slf4j-api-1.8.0-alpha1.pom (1.6 kB at 19 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha3/slf4j-parent-2.0.0-alpha3.pom (16 kB at 409 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha1/slf4j-parent-1.8.0-alpha1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha1/slf4j-simple-2.0.0-alpha1.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha3/slf4j-api-2.0.0-alpha3.pom (1.6 kB at 18 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta0/slf4j-api-1.8.0-beta0.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha2/slf4j-simple-2.0.0-alpha2.pom (1.1 kB at 11 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha2/slf4j-parent-2.0.0-alpha2.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha6/slf4j-api-2.0.0-alpha6.pom (1.7 kB at 16 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha0/slf4j-simple-2.0.0-alpha0.pom (1.1 kB at 10 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha2/slf4j-api-2.0.0-alpha2.pom (1.6 kB at 15 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta4/slf4j-simple-1.8.0-beta4.pom (1.1 kB at 10.0 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta2/slf4j-api-1.8.0-beta2.pom (1.6 kB at 15 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha6/slf4j-simple-2.0.0-alpha6.pom (1.1 kB at 10 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta4/slf4j-api-1.8.0-beta4.pom (1.7 kB at 15 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta2/slf4j-parent-1.8.0-beta2.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta4/slf4j-parent-1.8.0-beta4.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha7/slf4j-api-2.0.0-alpha7.pom (1.6 kB at 15 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha0/slf4j-parent-2.0.0-alpha0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha6/slf4j-parent-2.0.0-alpha6.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha1/slf4j-simple-1.8.0-alpha1.pom (1.0 kB at 8.7 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha0/slf4j-api-2.0.0-alpha0.pom (1.7 kB at 14 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta1/slf4j-simple-2.0.0-beta1.pom (1.1 kB at 9.7 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha7/slf4j-simple-2.0.0-alpha7.pom (1.1 kB at 32 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta2/slf4j-simple-1.8.0-beta2.pom (1.0 kB at 9.6 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.pom (3.8 kB at 34 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha7/slf4j-parent-2.0.0-alpha7.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta1/slf4j-api-2.0.0-beta1.pom (1.6 kB at 15 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha1/slf4j-api-2.0.0-alpha1.pom (1.7 kB at 15 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha5/slf4j-api-2.0.0-alpha5.pom (1.6 kB at 14 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.32/slf4j-parent-1.7.32.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-alpha4/slf4j-api-2.0.0-alpha4.pom (1.6 kB at 15 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-beta1/slf4j-parent-2.0.0-beta1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha1/slf4j-parent-2.0.0-alpha1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha4/slf4j-parent-2.0.0-alpha4.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta0/slf4j-api-2.0.0-beta0.pom (1.6 kB at 13 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.34/slf4j-api-1.7.34.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-beta0/slf4j-parent-2.0.0-beta0.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha4/slf4j-simple-2.0.0-alpha4.pom (1.1 kB at 8.9 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta0/slf4j-simple-2.0.0-beta0.pom (1.1 kB at 8.9 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-alpha1/slf4j-simple-2.0.0-alpha1.pom (1.1 kB at 23 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha1/slf4j-parent-1.8.0-alpha1.pom (15 kB at 298 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta0/slf4j-api-1.8.0-beta0.pom (1.6 kB at 36 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta0/slf4j-parent-1.8.0-beta0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha2/slf4j-parent-2.0.0-alpha2.pom (17 kB at 459 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.32/slf4j-simple-1.7.32.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta4/slf4j-parent-1.8.0-beta4.pom (17 kB at 447 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha0/slf4j-parent-2.0.0-alpha0.pom (16 kB at 423 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta2/slf4j-parent-1.8.0-beta2.pom (16 kB at 420 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha0/slf4j-api-1.8.0-alpha0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.34/slf4j-simple-1.7.34.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.30/slf4j-simple-1.7.30.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-beta1/slf4j-parent-2.0.0-beta1.pom (16 kB at 425 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.34/slf4j-api-1.7.34.pom (3.8 kB at 107 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha7/slf4j-parent-2.0.0-alpha7.pom (16 kB at 406 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.35/slf4j-api-1.7.35.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.34/slf4j-parent-1.7.34.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.35/slf4j-simple-1.7.35.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.32/slf4j-parent-1.7.32.pom (14 kB at 321 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha6/slf4j-parent-2.0.0-alpha6.pom (17 kB at 353 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha4/slf4j-parent-2.0.0-alpha4.pom (17 kB at 406 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-alpha1/slf4j-parent-2.0.0-alpha1.pom (16 kB at 374 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.33/slf4j-api-1.7.33.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.33/slf4j-simple-1.7.33.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta0/slf4j-simple-1.8.0-beta0.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/2.0.0-beta0/slf4j-parent-2.0.0-beta0.pom (16 kB at 329 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta0/slf4j-parent-1.8.0-beta0.pom (15 kB at 475 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta1/slf4j-api-1.8.0-beta1.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha2/slf4j-api-1.8.0-alpha2.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.32/slf4j-simple-1.7.32.pom (1.0 kB at 35 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom (2.7 kB at 70 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.30/slf4j-simple-1.7.30.pom (1.0 kB at 32 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha0/slf4j-api-1.8.0-alpha0.pom (1.6 kB at 48 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.30/slf4j-parent-1.7.30.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.34/slf4j-simple-1.7.34.pom (1.0 kB at 30 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha0/slf4j-parent-1.8.0-alpha0.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.35/slf4j-api-1.7.35.pom (3.8 kB at 116 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.35/slf4j-parent-1.7.35.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.33/slf4j-api-1.7.33.pom (3.8 kB at 128 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.pom (3.8 kB at 120 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.33/slf4j-parent-1.7.33.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.34/slf4j-parent-1.7.34.pom (14 kB at 367 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.33/slf4j-simple-1.7.33.pom (1.0 kB at 32 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.35/slf4j-simple-1.7.35.pom (1.0 kB at 27 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta0/slf4j-simple-1.8.0-beta0.pom (1.0 kB at 28 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha2/slf4j-simple-1.8.0-alpha2.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-beta1/slf4j-api-1.8.0-beta1.pom (1.6 kB at 45 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta1/slf4j-parent-1.8.0-beta1.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom (1.0 kB at 30 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom (14 kB at 440 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha0/slf4j-simple-1.8.0-alpha0.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta1/slf4j-simple-1.8.0-beta1.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.8.0-alpha2/slf4j-api-1.8.0-alpha2.pom (1.6 kB at 34 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha0/slf4j-parent-1.8.0-alpha0.pom (15 kB at 458 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.30/slf4j-parent-1.7.30.pom (14 kB at 394 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha2/slf4j-parent-1.8.0-alpha2.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.35/slf4j-parent-1.7.35.pom (14 kB at 399 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.33/slf4j-parent-1.7.33.pom (14 kB at 402 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom (3.8 kB at 120 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha2/slf4j-simple-1.8.0-alpha2.pom (1.0 kB at 32 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom (1.0 kB at 33 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-beta1/slf4j-parent-1.8.0-beta1.pom (16 kB at 456 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-alpha0/slf4j-simple-1.8.0-alpha0.pom (1.0 kB at 32 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.8.0-beta1/slf4j-simple-1.8.0-beta1.pom (1.0 kB at 24 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.8.0-alpha2/slf4j-parent-1.8.0-alpha2.pom (15 kB at 354 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom (14 kB at 345 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta1/slf4j-api-2.0.0-beta1.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/2.0.0-beta1/slf4j-api-2.0.0-beta1.jar (61 kB at 1.3 MB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta1/slf4j-simple-2.0.0-beta1.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/2.0.0-beta1/slf4j-simple-2.0.0-beta1.jar (15 kB at 415 kB/s)
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ mtm-test ---
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar (41 kB at 1.0 MB/s)
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/main/resources
[INFO] 
[INFO] --- compiler:3.14.1:compile (default-compile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-testResources) @ mtm-test ---
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/test/resources
[INFO] 
[INFO] --- compiler:3.14.1:testCompile (default-testCompile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- surefire:3.5.4:test (default-test) @ mtm-test ---
[INFO] No tests to run.
[INFO] 
[INFO] --- jar:3.5.0:jar (default-jar) @ mtm-test ---
[WARNING] JAR will be empty - no content was marked for inclusion!
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.228 s
[INFO] Finished at: 2026-04-16T19:05:59+02:00
[INFO] ------------------------------------------------------------------------
```

A lot! Also, there are some alpha and beta versions of SLF4J I am not interested in. So lets get rid of them!

The `alpha`, `beta` and `milestone` versions are called "preview" versions. And, Maven 3.10.x has the `np` "no preview" filter.
(We have `s` and `ns` filter as well, so bye-bye snapshots in ranges!)

So lets remove all these unwanted versions with "no preview" filter in `org.slf4j` group!

```
[cstamas@angeleyes mtm]$ rm -R local/org/slf4j/
[cstamas@angeleyes mtm]$ mvn verify -e -Dmaven.repo.local=local -Dmaven.session.versionFilter=np@org.slf4j
[INFO] Error stacktraces are turned on.
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< org.cstamas:mtm-test >------------------------
[INFO] Building mtm-test 1.0.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] Loaded 22552 auto-discovered prefixes for remote repository central (prefixes-central.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml (3.8 kB at 23 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml (4.1 kB at 25 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.33/slf4j-api-1.7.33.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.33/slf4j-simple-1.7.33.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.34/slf4j-api-1.7.34.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.32/slf4j-simple-1.7.32.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.34/slf4j-simple-1.7.34.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.35/slf4j-api-1.7.35.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.35/slf4j-simple-1.7.35.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.30/slf4j-simple-1.7.30.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom (1.0 kB at 28 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom (2.7 kB at 76 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom (14 kB at 403 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.33/slf4j-api-1.7.33.pom (3.8 kB at 44 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.33/slf4j-parent-1.7.33.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.34/slf4j-api-1.7.34.pom (3.8 kB at 43 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.34/slf4j-parent-1.7.34.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom (3.8 kB at 39 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom (1.0 kB at 10 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.35/slf4j-api-1.7.35.pom (3.8 kB at 36 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.32/slf4j-simple-1.7.32.pom (1.0 kB at 9.5 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.33/slf4j-simple-1.7.33.pom (1.0 kB at 9.5 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.34/slf4j-simple-1.7.34.pom (1.0 kB at 9.4 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.35/slf4j-simple-1.7.35.pom (1.0 kB at 9.4 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.30/slf4j-api-1.7.30.pom (3.8 kB at 35 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.32/slf4j-api-1.7.32.pom (3.8 kB at 36 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.35/slf4j-parent-1.7.35.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.32/slf4j-parent-1.7.32.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.30/slf4j-parent-1.7.30.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.30/slf4j-simple-1.7.30.pom (1.0 kB at 9.1 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.33/slf4j-parent-1.7.33.pom (14 kB at 402 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.34/slf4j-parent-1.7.34.pom (14 kB at 399 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom (14 kB at 363 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.35/slf4j-parent-1.7.35.pom (14 kB at 436 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.32/slf4j-parent-1.7.32.pom (14 kB at 418 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.30/slf4j-parent-1.7.30.pom (14 kB at 337 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar (41 kB at 914 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.jar (15 kB at 383 kB/s)
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ mtm-test ---
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/main/resources
[INFO] 
[INFO] --- compiler:3.14.1:compile (default-compile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-testResources) @ mtm-test ---
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/test/resources
[INFO] 
[INFO] --- compiler:3.14.1:testCompile (default-testCompile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- surefire:3.5.4:test (default-test) @ mtm-test ---
[INFO] No tests to run.
[INFO] 
[INFO] --- jar:3.5.0:jar (default-jar) @ mtm-test ---
[WARNING] JAR will be empty - no content was marked for inclusion!
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.023 s
[INFO] Finished at: 2026-04-16T19:06:13+02:00
[INFO] ------------------------------------------------------------------------
```

Much better, is it? But let's assume we want exactly `1.7.36` version to be selected, but in this demo we are NOT allowed
or we cannot modify the POM, just the command line. We can use `i` (include) filter for that:

```
[cstamas@angeleyes mtm]$ rm -R local/org/slf4j/
[cstamas@angeleyes mtm]$ mvn verify -e -Dmaven.repo.local=local -Dmaven.session.versionFilter="i(1.7.36)@org.slf4j"
[INFO] Error stacktraces are turned on.
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< org.cstamas:mtm-test >------------------------
[INFO] Building mtm-test 1.0.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] Loaded 22552 auto-discovered prefixes for remote repository central (prefixes-central.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml (4.1 kB at 21 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml (3.8 kB at 19 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.pom (1.0 kB at 29 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom (2.7 kB at 76 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom (14 kB at 391 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar (41 kB at 1.1 MB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.36/slf4j-simple-1.7.36.jar (15 kB at 529 kB/s)
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ mtm-test ---
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/main/resources
[INFO] 
[INFO] --- compiler:3.14.1:compile (default-compile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-testResources) @ mtm-test ---
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/test/resources
[INFO] 
[INFO] --- compiler:3.14.1:testCompile (default-testCompile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- surefire:3.5.4:test (default-test) @ mtm-test ---
[INFO] No tests to run.
[INFO] 
[INFO] --- jar:3.5.0:jar (default-jar) @ mtm-test ---
[WARNING] JAR will be empty - no content was marked for inclusion!
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  0.968 s
[INFO] Finished at: 2026-04-16T19:06:20+02:00
[INFO] ------------------------------------------------------------------------
[cstamas@angeleyes mtm]$ 
```

This basically **limited the range** to `1.7.36`.

Oh, and the version in `i` and `e` filters is dependency version constraint, so it can contain comma separated ranges 
(whatever real dependency in POM can).

What if for some weird reason we want to force different versions to `slf4j-api` and `slf4j-simple`? No problem! 
List the rules from "most specific" to "least specific":

```
[cstamas@angeleyes mtm]$ rm -R local/org/slf4j/
[cstamas@angeleyes mtm]$ mvn verify -e -Dmaven.repo.local=local -Dmaven.session.versionFilter="i(1.7.31)@org.slf4j:slf4j-simple;i(1.7.31)@org.slf4j"
[INFO] Error stacktraces are turned on.
[INFO] Scanning for projects...
[INFO] 
[INFO] ------------------------< org.cstamas:mtm-test >------------------------
[INFO] Building mtm-test 1.0.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] Loaded 22552 auto-discovered prefixes for remote repository central (prefixes-central.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/maven-metadata.xml (3.8 kB at 22 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/maven-metadata.xml (4.1 kB at 22 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.pom (3.8 kB at 104 kB/s)
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.pom (1.0 kB at 30 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.31/slf4j-parent-1.7.31.pom (14 kB at 406 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.31/slf4j-api-1.7.31.jar (41 kB at 943 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-simple/1.7.31/slf4j-simple-1.7.31.jar (15 kB at 401 kB/s)
[INFO] 
[INFO] --- resources:3.4.0:resources (default-resources) @ mtm-test ---
[INFO] Loaded 74 auto-discovered prefixes for remote repository apache.snapshots (prefixes-apache.snapshots.txt)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.pom (2.7 kB at 81 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-parent/1.7.36/slf4j-parent-1.7.36.pom (14 kB at 391 kB/s)
Downloading from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar
Downloaded from central: https://repo.maven.apache.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar (41 kB at 894 kB/s)
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/main/resources
[INFO] 
[INFO] --- compiler:3.14.1:compile (default-compile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- resources:3.4.0:testResources (default-testResources) @ mtm-test ---
[INFO] skip non existing resourceDirectory /home/cstamas/tmp/mtm/src/test/resources
[INFO] 
[INFO] --- compiler:3.14.1:testCompile (default-testCompile) @ mtm-test ---
[INFO] No sources to compile
[INFO] 
[INFO] --- surefire:3.5.4:test (default-test) @ mtm-test ---
[INFO] No tests to run.
[INFO] 
[INFO] --- jar:3.5.0:jar (default-jar) @ mtm-test ---
[WARNING] JAR will be empty - no content was marked for inclusion!
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.061 s
[INFO] Finished at: 2026-04-16T21:10:31+02:00
[INFO] ------------------------------------------------------------------------
[cstamas@angeleyes mtm]$ 
```

This made our POM above to resolve dependency `slf4j-api` to `1.7.36` and `slf4j-simple` to `1.7.31`.

{{% pageinfo %}}

The last one is not a valid thing to do, because these two artifacts are released together, so they have the same version. 
This example is merely done to show the power of version filters in Maven 3.10.x.

{{% /pageinfo %}}
