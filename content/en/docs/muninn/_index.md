---
title: Muninn
description: Maven core extension producing compact JSON reports, for coding agents
categories: [Documentation]
tags: [docs]
projects: [ Muninn ]
weight: 190
---

{{% pageinfo %}}
Maven core extension producing compact JSON reports, for coding agents
{{% /pageinfo %}}

Muninn is a Maven core extension for coding agents: it replaces Maven console output with a single compact JSON report
at the end of the build. The full console log is still written to `target/muninn-output/build.log`, and the report
points to it. It is inactive unless switched on, by `-Dmuninn.output=json` (or `ndjson`), the `MUNINN_OUTPUT`
environment variable, or automatically when an agent environment is detected.

The report contains per-module results, and recognizes compile errors (with file, line and column), test failures
(from Surefire and Failsafe reports), dependency resolution failures (with the repositories tried and the reason),
Javadoc errors and POM problems. It also contains a `resume` command to continue the build from the failed module.
This typically reduces output size several times compared to console output.

Muninn works with Maven 3.9 and 3.10, has no dependencies, and is recommended to be installed as user-wide extension.

Sources: https://github.com/maveniverse/muninn
