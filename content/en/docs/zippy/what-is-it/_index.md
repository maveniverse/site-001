---
title: What is it?
description: Embrace ZIPs
categories: [Zippy, Documentation]
tags: [zippy, docs]
weight: 10
---

By Java spec, classpath may contain JARs, ZIPs and directories (with `.class` files). Maven is "not conformant" in
this respect, as while it adds JAR dependencies to classpath, ZIPs are not added.

Zippy helps here.

Zippy extension provides:
* Dependency type `zip-classpath`, similar to `type=zip`, but ZIP declared with this type is added to classpath.
* Dependency type `zip`, that by default makes Maven behave same as before. But, IF you define Java System Property `maveniverse.zippy.zip.classpath=true`, then all dependencies of `type=zip` will be added to classpath. Not recommended for new projects, this is more like a hack.
* Packaging `zip`, where one can create POM with `<packaging>zip</packaging>` and unfiltered (and filtered if configured as usual) resources from project will be just zipped up as main artifact.

To use it, just add following bits to your project `.mvn/extensions.xml`:
```
<?xml version="1.0" encoding="UTF-8"?>
<extensions>
    <extension>
        <groupId>eu.maveniverse.maven.zippy</groupId>
        <artifactId>extension3</artifactId>
        <version>${version.zippy}</version>
    </extension>
</extensions>
```

Naturally, this extension applies locally to project only, so it will modify ZIP file handling **in situ** only.

You can still produce libraries and JARs for downstream consumption that expect same behaviour, but then **your consumers must use Zippy as well**.