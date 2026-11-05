---
title: BOM Builder Maven Plugin
description: A tool for generating BOMs
categories: [Documentation]
tags: [docs]
projects: [ BomBuilder ]
weight: 50
---

{{% pageinfo %}}
A Maven Plugin for BOMs to build according to your own taste.
{{% /pageinfo %}}

BOM Builder is a Maven 3 plugin that generates a dependency management POM (a "BOM", bill of materials) from the
dependencies of the current project. The generated POM contains a `dependencyManagement` section listing the
configured set of artifacts: only the modules of the reactor, or the full stack including transitive dependencies.

The plugin does not take a stance on what a BOM should contain. Maven team calls the reactor-only kind "skinny" and
the full-stack kind "fat"; both are possible, and the content can be tuned with exclusions, dependency exclusions
(with wildcards) and the option to express versions via properties. The BOM can be attached with a classifier
(consumable by Maven 4 only), or it can replace the `pom.xml` of a dedicated `pom` packaging module, which makes it
consumable by Maven 3 as well.

Sources: https://github.com/maveniverse/bom-builder-maven-plugin

[Maven generated plugin documentation](plugin-documentation/plugin-info.html)
