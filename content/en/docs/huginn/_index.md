---
title: Huginn
description: Project-aware MCP server for Maven, for coding agents
categories: [Documentation]
tags: [docs]
projects: [ Huginn ]
weight: 200
---

{{% pageinfo %}}
Project-aware MCP server for Maven, for coding agents
{{% /pageinfo %}}

Huginn is an MCP server for coding agents that answers questions about the Maven build the agent is working on: the
reactor's effective models, the repositories in use, and the resolved dependency graph, including
`dependencyManagement`, BOMs, profiles and CI-friendly versions from `.mvn/maven.config`. Reactor modules that were
never installed are resolved from the working tree, the same way Maven does.

It provides seven read-only tools: `describe` (modules or a module's effective model), `dependencies` (resolved tree
with conflicts), `why` (every path bringing an artifact in), `versions` (upgrade candidates from the project's own
repositories), `search` (Maven Central), `sources` (sources of a dependency) and `extensions` (declared core
extensions, and which useful ones are missing). The number of tools is kept low on purpose, as each tool description
costs agent context. Running builds is left to Maven itself, together with Muninn.

Huginn is built on MIMA and MASE, requires Java 17, and is run via JBang (`jbang huginn-mcp@maveniverse`).

Sources: https://github.com/maveniverse/huginn
