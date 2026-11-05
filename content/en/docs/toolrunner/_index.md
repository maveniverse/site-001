---
title: Toolrunner
description: Toolrunner
categories: [Documentation]
tags: [docs]
projects: [ Toolrunner ]
weight: 160
---

{{% pageinfo %}}
Provides means to detect, provision and execute (via own or Java ToolProvider SPI) various tools.
{{% /pageinfo %}}

Toolrunner is a library and a Maven plugin for running CLI tools as part of a build, optionally provisioning them
first. Supported tools are Ant, Cosign, Gradle, isx, JBang, Maven, Minisign and the tools of the running JDK.

The core library is built on MIMA and provides a `ToolManager` to discover, provision and invoke tools. Tools are
implemented as `ToolProvider`s and discovered using the Java `ServiceLoader`. The Maven plugin itself is minimal: the
tools needed are added as plugin dependencies, and are discovered dynamically.

Requires Java 8+ and, for the plugin, Maven 3.6+.

Sources: https://github.com/maveniverse/toolrunner
