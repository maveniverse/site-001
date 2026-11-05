---
title: Maven BOMs
description: Generating the missing BOMs
categories: [Documentation]
tags: [docs]
projects: [ Maven BOMs ]
weight: 120
---

{{% pageinfo %}}
Generating the missing BOMs for Maven versions.
{{% /pageinfo %}}

Apache Maven does not publish BOMs for its own artifacts, which makes aligning versions harder when building plugins,
extensions or other tools against a given Maven version. Maven BOMs generates and publishes them, per Maven version.

Three BOMs are generated for each Maven version: "skinny" (the Maven core artifacts only), "fat" (everything the
Maven distribution contains, including transitive dependencies), and "plugin" (meant for plugin development, with
artifacts that should not be used by plugins excluded). The BOMs are produced with BOM Builder Maven Plugin, and the
build uses Nisse to drive versions from a single file containing the target Maven version.

Sources: https://github.com/maveniverse/maven-boms
