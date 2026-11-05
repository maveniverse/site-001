---
title: Scalpel
description: Surgical tool to speed up builds
categories: [Documentation]
tags: [docs]
projects: [ Scalpel ]
weight: 140
---

{{% pageinfo %}}
Maven extension that detects which modules in a multi-module reactor are affected by a git changeset. Analyzes POM changes semantically — tracking property indirection, managed dependencies, plugins, and resource filtering — to avoid unnecessary rebuilds.
{{% /pageinfo %}}

Scalpel is a Maven 3.9+ core extension that, given a Git changeset, determines which modules of a multi-module reactor
are affected. It finds the merge base against a base branch, maps changed files to modules, and analyzes POM changes
semantically, following property indirection, managed dependencies, plugins, import-scoped BOMs and resource
filtering, instead of treating any POM change as a change to everything.

The result is applied according to the mode: `trim` (default) builds only the affected modules and their upstream and
downstream dependencies, `skip-tests` builds everything but runs tests only in affected modules, and `report` writes
a JSON report for CI scripts without changing the build. The `shadow` mode runs a full build and records what
trimming would have done, to evaluate it on a given project before adopting it.

Scalpel works on CI (including shallow clones) and locally, and has a migration guide for users of
gitflow-incremental-builder.

Sources: https://github.com/maveniverse/scalpel
