---
title: DOMTrip
description: The lossless XML editing library for Java
categories: [Documentation]
tags: [docs]
projects: [ DOMTrip ]
weight: 100
---

{{% pageinfo %}}
Round-trip editing is a programmatic changing/editing an XML document, like for example a Maven POM is, while 
preserving all the formatting of the original document.
{{% /pageinfo %}}

DOMTrip is a Java 8+ library for lossless XML editing. A document parsed with DOMTrip and written back out is
identical to the input: comments, whitespace, entity encoding, attribute order and quote styles are all preserved.
When the document is modified, only the changed parts are reformatted, following the style of the surrounding
content.

The API offers fluent builders, stream-based navigation, namespace support, a built-in mini XPath (full XPath 1.0 via
the `domtrip-jaxen` module), an XML-aware structural diff, and SAX output for interoperation with JAXP. The
`domtrip-maven` module adds utilities specific to editing Maven POMs.

Typical use is tooling that changes human-maintained XML files, like POMs or other configuration files, where
reformatting the whole file is not acceptable. Other Maveniverse projects, like Pilot, use it for POM editing.

Sources: https://github.com/maveniverse/domtrip

Site: https://maveniverse.github.io/domtrip/
