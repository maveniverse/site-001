---
title: MIMA
description: Use Resolver everywhere!
categories: [Documentation]
tags: [docs]
projects: [ MIMA ]
weight: 10
---

{{% pageinfo %}}
Maveniverse MIMA is very first project of ours.
{{% /pageinfo %}}

MIMA ("MIni MAven") is a Java 8 library that makes it easy to use Maven Resolver as a library, both inside and outside
of Maven. Resolver alone is incomplete: model classes and several components are provided by Maven, and outside of
Maven one also needs to apply user configuration like `settings.xml`. MIMA provides all this, and lets the same
code run unchanged in a Maven plugin or in a standalone application.

Code is written against the MIMA `context` artifact, and at runtime one or more runtimes are provided: `embedded-maven`
(when running inside Maven, it reuses the repository system and session Maven already set up), `standalone-sisu`
(boots Eclipse Sisu, so Resolver can be extended with components from the classpath) or `standalone-static` (no DI,
manual wiring). Standalone runtimes are also available as "uber" JARs.

In every case the context supports all recent Resolver features and configuration properties, like split local
repository, extensible checksums, transport configuration, repository filtering and locking. Many other Maveniverse
projects, like Toolbox and Huginn, are built on MIMA.

Sources: https://github.com/maveniverse/mima
