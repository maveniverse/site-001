---
title: Njord (Njörðr)
description: Local staging, Artifact publishing and more!
categories: [Documentation]
tags: [docs]
projects: [ Njord ]
weight: 80
---

{{% pageinfo %}}
Njord is an attempt to bring simple "publishing" (new term, is **not** "deploying with a twist") to Maven 3 and Maven 4
with some extras like "local staging".
{{% /pageinfo %}}

Where and how artifacts are published changes over time, and publishing services often require project changes like
extra profiles or their own plugins. Njord is a Maven 3.9+/4 extension and plugin that separates publishing from the
build: the project is deployed as usual, into a local "staging" store, and the store is then published to the chosen
service, without changes to the POMs.

Supported publishers include Sonatype Central Portal, Apache RAO, generic Sonatype Nexus 2 and 3 instances, plain
install and deploy, and JReleaser. Staged content can be listed, inspected and validated before publishing. As
publisher and authentication are configured in `settings.xml`, one needs only one server entry per publishing service,
instead of one per project.

Njord is used by Maveniverse itself and by other projects like MojoHaus, Codehaus Plexus and Quarkus.

Sources: https://github.com/maveniverse/njord

[Maven generated plugin documentation](plugin-documentation/plugin-info.html)
