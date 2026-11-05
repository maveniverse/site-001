---
title: Nisse
description: Inject properties to your build
categories: [Documentation]
tags: [docs]
projects: [ Nisse ]
weight: 30
---

{{% pageinfo %}}
Nisse was a response to "finish" CI Friendly implementation in Maven 3, but turned out to be more.
{{% /pageinfo %}}

Nisse is a suite of a core extension and a plugin for Maven 3 and Maven 4 (and a Gradle plugin) that collects
properties from "property sources" and publishes them to the build. Sources available out of the box are: properties
files, Git data via Eclipse JGit, Maven version, and OS information; new sources can be added. Property keys can be
renamed when published, for example to `revision`.

In Maven 3 it also fixes CI Friendly versions, which by default can result in deploying POMs with unresolved version
expressions. Combined with the JGit source, the project version can be derived from Git tags and history, removing
hardcoded versions from POMs.

Nisse can also replace the discontinued OS Detector plugin: with `-Dnisse.compat.osDetector` it emits the same
properties. To see what Nisse injects, use `mvn validate -N -Dnisse.dump`.

Sources: https://github.com/maveniverse/nisse
