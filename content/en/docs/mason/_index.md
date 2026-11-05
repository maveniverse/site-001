---
title: Mason
description: If you dislike XML
categories: [Documentation]
tags: [docs]
projects: [ Mason ]
weight: 70
---

{{% pageinfo %}}
A new project that makes POMs written in YAML, JSON, HOCON and TOML possible with all the whistle and bells.
{{% /pageinfo %}}

Mason is a Maven 4 core extension that provides alternative model readers, making it possible to write POMs in YAML,
JSON5, TOML or HOCON instead of XML. It requires Maven 4.0.0-rc-3 or later and Java 17; it does not work with Maven 3.

To use it, register the extension in the project root `.mvn/extensions.xml` and replace `pom.xml` with a `pom.yaml`,
`pom.json`, `pom.toml` or `pom.conf` file; child modules inherit the extension. Besides the format, the model can be
written in a more compact form, for example coordinates as single `groupId:artifactId:version` strings and dependency
scope given as a suffix (`@test`).

YAML and JSON are fully supported. TOML and HOCON support is limited: HOCON substitutions, includes and object merging
are not supported, and TOML files do not report line numbers in errors.

Sources: https://github.com/maveniverse/mason
