---
title: Zippy
description: Small extension for ZIP files
categories: [Documentation]
tags: [docs]
projects: [ Zippy ]
weight: 90
---

{{% pageinfo %}}
Zippy is small extension for simpler working with ZIP files.
{{% /pageinfo %}}

Zippy is a Maven 3.9+ extension and plugin suite for working with ZIP files as dependencies and as build output.

It provides a `zip-classpath` artifact handler, so dependencies of `type=zip-classpath` are added to the classpath.
It also provides a `zip` handler that behaves like plain Maven (not adding ZIPs to classpath), unless the
`maveniverse.zippy.zip.classpath=true` system property is set; for new projects the explicit `zip-classpath` type is
recommended. Finally, it provides a `zip` packaging that produces a ZIP file from (optionally filtered) resources,
based on `maven-jar-plugin` and accepting mostly the same options.

Sources: https://github.com/maveniverse/zippy
