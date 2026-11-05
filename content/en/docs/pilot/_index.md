---
title: Pilot
description: The TUI for Maven
categories: [Documentation]
tags: [docs]
projects: [ Pilot ]
weight: 150
---

{{% pageinfo %}}
Interactive TUI for Maven -- search, browse, and manage dependencies from the terminal.
{{% /pageinfo %}}

Pilot is a Maven plugin and a standalone CLI providing interactive, keyboard-driven terminal UIs for working with
Maven projects. The `pilot:pilot` goal opens a shell with the reactor module tree and tabs for each tool, while
individual tools are also available as goals.

Tools include: Maven Central search, dependency tree browsing with conflict highlighting, raw and effective POM viewer
with origin tracking, bytecode-based analysis of used and unused dependencies, dependency and plugin update checks,
version conflict resolution, license and vulnerability audit (via OSV.dev), and alignment of dependency conventions
across POMs. Changes to POMs are made using DOMTrip, preserving formatting and comments.

Most goals also have non-interactive `report`, `check` and `fix` actions for use in CI. The standalone CLI (runnable
via JBang) embeds Maven 4 Resolver and does not need `mvn`. Requires Java 17+ and Maven 3.6.3+.

Sources: https://github.com/maveniverse/pilot
