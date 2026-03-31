---
title: Toolbox
description: Swiss knife in your pocket
categories: [Documentation]
tags: [docs]
projects: [ Toolbox ]
weight: 20
---

{{% pageinfo %}}
Toolbox was started as a "showcase" project of Maveniverse MIMA combined into plugin goals and CLI commands, that never stopped growing.
{{% /pageinfo %}}

A tool that gives you Swiss Knife for every situation. Toolbox is a Maven Plugin but also a CLI tool (and a Maven 4
`mvnsh` extension) that provides useful commands.

{{% pageinfo %}}

If you consider the Maven Plugin documentation below, you will notice there are two types of goals: those with `gav-`
prefix and those without it. The differences are:
* The `gav-` prefixed goals do **not require project** and same code is exposed via CLI as well. For example
  `mvn toolbox:gav-search` and `jbang toolbox@maveniverse search` runs essentially the same code.
* The `gav-` prefix-less goals **do require Maven project** and hence are not exposed via CLI.

{{% /pageinfo %}}


https://github.com/maveniverse/toolbox

[Maven generated plugin documentation](plugin-documentation/plugin-info.html)