---
title: What is it?
description: Publish where you want (and more)!
categories: [Njord, Documentation]
tags: [njord, docs]
weight: 10
---

Njord is a Maven 3 and Maven 4 extension that offers local staging, repository operations and repository publishing. 
More precisely, Njord is a Resolver 1.x and 2.x extension (is yet another [`RepositoryConnector`](https://github.com/apache/maven-resolver/blob/fb6e59027cfce9c9fce6f4e4f6d310c1a7ee906c/maven-resolver-spi/src/main/java/org/eclipse/aether/spi/connector/RepositoryConnector.java)) 
that is loaded via Maven extensions mechanism and extends Resolver. Njord does not mingle with your build at all.
