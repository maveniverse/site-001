---
title: "Migrating to Maven 3, part 3"
date: 2024-09-09T19:16:22+02:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://twitter.com/cstamas))
categories:
  - Blog
tags:
  - plexus
  - sisu
  - jsr330
projects:
  - Maven

---

From Maven perspective, whether a component is defined as Plexus component (via Plexus XML, crafted manually or during build 
with `plexus-component-metadata` Maven Plugin) or JSR330 component, does not matter.

But there is a subtle difference.

Plexus components store their "definition" in XML that is usually embedded in JAR, so Plexus DI has not much to do
aside to parse the XML and use Java usual means to instantiate it, populates/wires up requirements and publish it.

Very similar thing happens with JSR330 defined components, but with one **important difference**: JSR330
components are discovered via "sisu index" (there are other means as well like classpath scanning, but for performance
reasons in Maven only the "sisu index" is used), a file usually embedded in JAR at `META-INF/sisu/javax.inject.Named` file.
The index file contains FQCN of component classes. So to say, "data contents" of Sisu index is way less than that of Plexus
XML. Hence, Sisu at runtime has to gather some intel about the component.

To achieve that, Sisu uses [ASM](https://asm.ow2.io/) library to "lightly introspect" the component, and once all the 
intel collected, it instantiates it, populates/wires up requirements and publishes it.

But the use of ASM has a huge implication: the components bytecode. While in case of "Plexus defined" components
all the "intel" is in XML, and the component bytecode needs to be supported only by the JVM component is about to reside,
in case of Sisu, things are a bit different: to _successfully introspect it_, the component bytecode has to be 
supported by ASM library used by Sisu (also, Guice uses ASM as well).

Table of Maven baseline versions and related upper boundaries of supported Java bytecodes.

| Maven baseline | Java baseline | org.eclipse.sisu version | ASM version                     | Java bytecode supported by ASM |
|----------------|---------------|---------------------------------------------|---------------------------------|--------------------------------|
| 3.6.x          | 7             | 0.3.3                                       | 5.x (shaded)                    | Java 8 (52)                    |
| 3.8.x          | 7             | 0.3.3                                       | 5.x (shaded)                    | Java 8 (52)                    |
| 3.9.x          | 8             | 0.3.5                                       | modded 5.x for Java 14 (shaded) | Java 14 (58)                   |
| 3.9.6          | 8             | 0.9.0.M2                                    | 9.4 (shaded) (*)                | Java 20 (64)                   |
| 3.9.8          | 8             | 0.9.0.M3                                    | 9.7 (shaded)                    | Java 23 (67)                   |
| 4.0.x          | 17            | 0.9.0.M3                                    | 9.7 (not shaded) (**)           | Java 23 (67)                   |

(*) - recent versions of Guice (since 4.0) and Sisu (since 0.9.0.M2) releases offer "no asm" artifacts as well, along with those that still shade ASM in.  
(**) - Maven 4 uses "no asm" artifacts of Guice and Sisu and itself controls the ASM version included in Maven Core, to be used by these libraries.
Maven3 on the other hand, continues to use shaded one, as before.

This has the following implications: if you develop Maven Plugin, Maven Extension, and your project contains JSR330
components, and you claim support for:
* Maven 3.6.x and 3.8.x, components can be compiled up to Java 8 (52) bytecode
* Maven 3.9.x, components can be compiled up to Java 14 (58) bytecode
* Maven 3.9.6, components can be compiled up to Java 20 (64) bytecode
* Maven 3.9.8 and/or 4.0.x components can be compiled up to Java 23 (67) bytecode

The problem is, that Sisu will silently swallow issues related to "not able to glean" the component (due unsupported
bytecode version). To see these, you can use `-Dsisu.debug`.

Hence, the ideal thing you can do, if you develop Plugins or Extensions that declare "minimum supported Maven version"
is to also compile to that bytecode level as well. Otherwise, you must pay attention and follow this table.

On related node, recent Sisu versions introduced this flag: https://github.com/eclipse-sisu/sisu-project/pull/98
Also, latest Maven 4.0.x comes with this flag enabled.

PS: Just to be clear, do NOT go back to Plexus XML. Plexus allows only default constructor for start (hence, have much
simpler job to do). Sisu "introspection" is really minimal, is figuring out which constructor needs to be bound, 
and if one still uses field injection, which those fields are.

PPS: This above is true only for "pure JSR330" components, it does **not** stand for Maven Plugins.

Enjoy!
