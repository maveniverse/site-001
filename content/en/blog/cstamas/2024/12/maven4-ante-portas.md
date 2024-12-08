---
title: "Maven4 ante portas! (Part 1)"
date: 2024-12-07T13:00:00+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - cling
projects:
  - Maven
  - Mvnd
---

Maven4 is coming, so it may be time to explain some of the changes it will bring on.
I'd like to start from "user facing" end, the `mvn` command and what has changed
(visible and invisible changes).

## How it was: Maven3

In short, Maven3 has a well known `mvn` (and `mvn.cmd` Windows counterpart) script in place
that users invoke. This script observed some of the environment variables (think `MAVEN_OPTS`
and others), observed `mavenrc` file, tried to find `.mvn` directory and also load `.mvn/jvm.config`
from it, if existed, and finally, it fired up Java calling 
[ClassWorlds launcher](https://codehaus-plexus.github.io/plexus-classworlds/launcher.html) 
class and setting the launcher configuration to `conf/m2.conf` file.

From this point on, the ClassWorlds launcher populated the classloader(s) following
the instructions in the configuration file, and finally invoked the "enhanced" `main` 
method of the configured main class, that was `maven-embedder:org.apache.maven.cli.MavenCli`.
This is how `MavenCli` received the (preconfigured) ClassWorld instance.

The `MavenCli` class then parsed arguments, collected Maven system and user properties, built
"effective" settings (from various user and installation `settings.xml` files), created
DI container, while loading any possible build extension from `.mvn/extensions.xml`, if present, 
then populating `MavenExecutionRequest`, looked up `Maven` component, and finally invoked it
with the populated request. And this is where "Maven as you know it" started.

The subproject `maven-embedder` is frozen and deprecated. It still works, but offers
"legacy" face (like no new Maven4 options support and alike).

## How it is: Maven4

We faced several problems with this setup. For start, there was a lot of scaffolding around to
invoke **just one executable: `mvn`**. The whole thing was not extensible, it had many things 
"bolted on" and finally it was not reusable. But let's start in order.

Maven3 introduced "password encryption" (that it had issues on its own, but that is another
story). The CLI options to handle those actions were in fact "bolted on" to `MavenCli`, that
"semi booted" Maven (kinda, but not fully), and all this only to perform those actions without
DI or anything helpful. This was akin (and comments in source were suggesting this as well)
for a separate tool to handle password encryption. We knew we need more "Maven tools", as 
`mvn` alone is not enough. The `mvnenc` tool handling password encryption in Maven4 is first
of these. One example of what Maven3 is unable to handle: Plexus Sec Dispatcher was always
"extensible" with regard of Ciphers. Idea was to add it as extension. But alas, to have that 
new Cipher picked up, you'd need DI (and load extensions), so without DI all this never worked. 

Moreover, the `MavenCli` was mish-mash of some static methods, making it not extensible nor reusable.
This was really evident and most painful bit in new Maven Daemon (and biggest obstacle to make it 
"keep up" with Maven) The Maven Daemon was **forced to copy-pasta** it, and then modify this class,
to make it work for mvnd use case. And as expected, this lead to ton of burden to maintain and "port" 
changes from Maven CLI to mvnd CLI. We knew this situation is bad, and we wanted to reuse most if not all
of Maven CLI related code in mvnd. Essentially, they both do the "same thing", just latter 
"daemonize" Maven.

There were the ITs as well: the Maven ITs were not able to test new Maven4 features (like new
CLI options) as ITs historically used Maven Verifier, that either executed Maven in forked 
process (read: was slow) or used "embedded" mode, that again **went directly into 
`MavenCli` "tricky method"**. It was not justified to fork any IT that wanted to use new 
Maven 4 CLI options.

Finally, the state of the `MavenCli` was quite horrible, frankly. Few of us dared to enter
that jungle. Was very-very easy to mess up things in there, and moreover, have those issues
become known only after release, as Verifier "trick method" did not catch it.

I don't want to go into details, so on high level these are the changes:
* `mvn` script got "parameterizable main class", and this made possible **simple** introduction
  of alternative scripts, like `mvnenc`, that simply sets alternate main class, while everything
  else remains same and everything else is reused.
* The ClassWorlds Launcher config `m2.conf` observes this "main class" and launches accordingly.
* And we got CLIng, a layered reusable (and intentionally blunt simple) module to launch Maven 
  (a replacement for `MavenCLI` class).

The CLIng module resides in `impl/maven-cli` and the idea is simple this:
* main method `String[] args` (and other sources) are parsed chosen by `Parser` into `InvokerRequest`
* the chosen `Invoker` executes the parsed `InvokerRequest`
* simplified: `Invoker#invoker(Parser#parse(args))`

That's really the high level picture. CLIng itself is "layered" in a sense of different
requirements per layer. Various `Parsers` support various CLI options, so parsers are layered
as:
* `BaseParser` parses ["common" Maven-tool options](https://github.com/apache/maven/blob/8d4f455ac9f29904bb2c86847d41c310782fbea6/api/maven-api-cli/src/main/java/org/apache/maven/api/cli/Options.java)
* `MavenParser` extends `BaseParser` and parses ["mvn" CLI options](https://github.com/apache/maven/blob/8d4f455ac9f29904bb2c86847d41c310782fbea6/api/maven-api-cli/src/main/java/org/apache/maven/api/cli/mvn/MavenOptions.java)
* of course, one can have other parsers as well, like ["mvnenc" CLI options parser](https://github.com/apache/maven/blob/8d4f455ac9f29904bb2c86847d41c310782fbea6/api/maven-api-cli/src/main/java/org/apache/maven/api/cli/mvnenc/EncryptOptions.java)

The idea is that all these "specialization" build upon previous layer, in this case
`BaseParser`, that is the common ground: options supported by all Maven CLI tools (not just `mvn`).

For execution, similar thing happen, it is layered as this:
* `LookupInvoker` - abstract, handles "base" things, like user and system properties, DI creation along with 
   extension loading and all. This is the common ground of new Maven CLI tools, gives out of the
   box properly configured logging, DI (with extensions loaded) and all the groundwork.
* `MavenInvoker` - abstract, extends `LookupInvoker` and does "`mvn` specific things"
* `EncryptInvoker` - extends `LookupInvoker` and does "`mvnenc` specific things"

In short: "lookup" provides the "base ground" (that `mvn` and other tools like `mvnenc`)
build upon. Again. goal is to have in all tools shared support for "common" features 
(think `-X` logging, or `-e` show stack traces, etc.). 

Furthermore, `MavenInvoker` (an abstract class) has two "specializations" that are non-abstract:

* `LocalMavenInvoker` - This invokes Maven "locally", expects to have all the Maven on classpath. This is  
  basically where you end up with command `mvn`. It does all the needed things as explained 
  above, just lookup `Maven` component and invoke it with pre-populated `MavenExecutionRequest`. 
  This invoker is "one off", in a sense, it creates DI and all the fluff, executes,
  and then tears everything down.
* `ResidentMavenInvoker` - A specialization that makes Maven "resident". On **first call**
  happens all the creation of DI and all the fluff, tear down is prevented at execution end, 
  and subsequent incoming `InvokerRequest` is executed by already created, "resident" Maven. 
  One important note: DI and extension loading happens only once (very first call), hence not 
  all "resident instances" are same! The logic of routing, which request may be executed 
  by which resident instance" is in fact implemented in Maven Daemon, as `mvnd` keeps a "pool" of
  Resident Maven processes. Also, Maven itself has a limitation that "one Maven instance may be 
  present in one single JVM" (due things like pushed System properties and others). 
  Resident Maven is cleaned up (properly shut down) when the resident invoker is closed.

With these things in Maven "proper" we were able to achieve substantial "diet" in Maven Daemon,
where [CLIng is really "just reused"](https://github.com/apache/maven-mvnd/pull/1158). From that
PR, release of Maven and Maven Daemon can really happen "in sync" as latest `rc-1` release 
proved. Also, we got first tool in Maven Tools suite, the `mvnenc`.

Finally, for integration tests, we introduced `impl/maven-executor` module with similar design
as CLIng has. It is a dependency-less library that is reusable and is amalgam of good old 
`maven-verifier` and `maven-invoker` but do the job less intrusive and in a future-proof way.
Maven Executor has 4 key bits:
* embedded executor - that invokes Maven installation in an isolated classloader 
  (a la Verifier "embedded" mode). Supports both Maven3 and Maven4.
* forked executor - a generic tool to invoke any executable (so not only `mvn`).
* helper - that offers "smart routing" between embedded and forked executor based 
  on execution request and preferences.
* tool - that exposes some queries from used Maven installation. Required for future,
  for example to be able to use "split local repository" and alike.

The Maven Integration Tests already contained own "extended Verifier" instance that extended
the old `maven-verifier` Verifier class. The redirection happened in `maven-it-helper` 
"extended Verifier", by dropping `maven-verifier` and `maven-shared-utils` dependencies,
and introducing `maven-executor` instead. Very few ITs were harmed in this process.