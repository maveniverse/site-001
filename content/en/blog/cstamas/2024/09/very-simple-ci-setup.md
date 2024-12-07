---
title: "Very simple CI setup"
date: 2024-09-07T15:55:22+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://twitter.com/cstamas))
categories:
  - Blog
tags:
  - CI
  - github
projects:
  - Maven
---

I'd just like to throw in a short explanation how (IMHO) should organize CI jobs for simple Maven projects for 
better and faster turnaround. 

People usually "throw up a matrix" and just run `mvn verify -P run-its`. Sure, that is really the simplest.

But what if, our matrix is big? Or what if we want to utilize one of the Maven basics, the Local repository?

I wanted to mimic what I do locally: I usually build/install with **latest stable Maven** (3.9.9 currently) and 
**latest LTS Java** (21.0.4 currently), and then perform a series of ITs/test/assessments, to ensure the thing
I build covers all combos of Maven/Java/whatever.

First example is [Maveniverse/MIMA](https://github.com/maveniverse/mima): It is a Java 8 library, and covers 
compatibility of Java `[8,)` and Maven `[3.6.3,)`, hence it does have a 
[huge matrix](https://github.com/maveniverse/mima/actions/runs/10701424692).

![33 jobs Matrix](/very-simple-ci-setup-1.png)

But the build is organized in "two phases", like build once, and test built thing multiple times (instead to 
"rebuild it over and over again and run tests on rebuilt thing"). The first job builds and installs the library into local repository,
then matrix comes with **reused local repo cache**, hence what was built and installed in there, is available and 
resolvable for subsequent jobs, where the tests runs only.

Second example: [Maveniverse/Toolbox](https://github.com/maveniverse/toolbox): It is a Java 21 Maven 3 Plugin, 
covers compatibility of Java `[21,)` and Maven `[3.6.3,)`, a bit [smaller matrix](https://github.com/maveniverse/toolbox/actions/runs/10702513051).

![12 jobs Matrix](/very-simple-ci-setup-2.png)

Again, same story: first job builds and installs using Maven 3.9.9 + Java 21 LTS, then matrix comes to play to 
ensure Maven 3.6.3 - Maven 4.0.0 all works with it (and only one dimension for Java, the 21 LTS). For this to work, 
we'd never want to collocate plugin ITs (ie invoker) and plugin code itself in same subproject, but is better to 
keep them in separate subprojects (in my case is added with profile run-its).

All in all, build only ONCE and test what you BUILT many times! Enjoy.