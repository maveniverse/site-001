---
title: Toolbox
description: Swiss knife in your pocket
categories: [Documentation]
tags: [docs]
projects: [ Toolbox ]
weight: 40
---

{{% pageinfo %}}
Toolbox was started as a "showcase" project of Maveniverse MIMA combined into plugin goals and CLI commands, that never stopped growing.
{{% /pageinfo %}}

Toolbox is a Maven plugin, a CLI (also runnable via JBang as `jbang toolbox@maveniverse`), a Maven 4 `mvnsh`
extension and an MCP server, all exposing the same set of commands. It started as a replacement for the MIMA CLI and
as a showcase of how MIMA lets the same Resolver code run inside Maven and standalone.

Commands cover resolving artifacts and classpaths, dependency trees, searching and listing versions, copying and
deploying artifacts, and more. It offers a similar subset of goals as `maven-dependency-plugin`. Toolbox also served
for experiments: the Resolver 2.x `ScopeManager` was born here, and Toolbox carries a Resolver 1.x workaround for
it, supporting Maven 3.6.3+. Requires Java 17+.

{{% pageinfo %}}

If you consider the Maven Plugin documentation below, you will notice there are two types of goals: those with `gav-`
prefix and those without it. The differences are:
* The `gav-` prefixed goals do **not require project** and same code is exposed via CLI as well. For example
  `mvn toolbox:gav-search` and `jbang toolbox@maveniverse search` runs essentially the same code.
* The `gav-` prefix-less goals **do require Maven project** and hence are not exposed via CLI.

{{% /pageinfo %}}

Sources: https://github.com/maveniverse/toolbox

[Maven generated plugin documentation](plugin-documentation/plugin-info.html)
