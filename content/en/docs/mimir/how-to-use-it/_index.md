---
title: How to use it?
description: The Maven workstation and LAN cache
categories: [Mimir, Documentation]
tags: [mimir, docs]
weight: 30
---

Simplest way to use Mímir is with Maven 4, it supports **user wide extensions**. Just create `~/.m2/extensions.xml` 
with following content (adjust Mímir version as needed):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.mimir</groupId>
        <artifactId>extension</artifactId>
        <version>0.4.1</version>
    </extension>
</extensions>
```

Using it with Maven 3 is also possible and completely fine and compatible, but there you will need to set up
per-project extensions in `.mvn/extensions.xml` file instead of one user-wide one.

One extra step is needed, in case you have non-trivial networking (like Docker, Tailscale or alike): you need 
to "help" a bit to JGroups, to figure out which networking interface belongs to your LAN. To achieve that,
you need to create `~/.mimir/daemon.properties` file with following content (use your LAN IP address):

```properties
mimir.jgroups.interface=match-address\:192.168.1.*
```

This will help JGroups to properly bind to interface that is used on your LAN.

Nothing more is needed.