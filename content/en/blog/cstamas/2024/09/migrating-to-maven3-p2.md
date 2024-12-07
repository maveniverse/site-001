---
title: "Migrating to Maven 3, part 2"
date: 2024-09-07T20:55:22+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://twitter.com/cstamas))
categories:
  - Blog
tags:
  - plexus
  - sisu
  - jsr330
projects:
  - Maven

---

A small fable for myself and others...

The Takari [Polyglot Maven 0.7.1](https://github.com/takari/polyglot-maven/releases/tag/polyglot-0.7.1) was released not
so long ago, and it contained one trivial change, this [pull request](https://github.com/takari/polyglot-maven/pull/319).
The goal was to fix following issue: JRuby folks had some problem, that could be solved among other ways, by creating a 
"custom JRuby Polyglot Maven distribution" (see related [pull request](https://github.com/takari/polyglot-maven/pull/323)).

But, while testing this, I came to strange conclusion: the Polyglot extension **did work** when loaded up through
`.mvn/extensions.xml`, but **did not work** when loaded up from core (when it was added to `lib/ext` of custom
Maven distribution). [Fix](https://github.com/takari/polyglot-maven/pull/319) seemed simple, raised the priority of `TeslaModelProcessor` and done. Polyglot started
working when in `lib/ext`, so I released 0.7.1.

But then, as you can see from [first PR long comment thread](https://github.com/takari/polyglot-maven/pull/319), a bug report flew in from none else 
then [Eclipse Tycho](https://github.com/takari/polyglot-maven/issues/321).

So what happened? And how comes Plexus in the story?

## The Plexus "way" (of components)

Historically, Plexus DI addresses components by `role` and `roleHint`. Originally, and this is important bit, both,
the `role` and `roleHint` were plain string labels: 

```java
  Object lookup(String role);
  Object lookup(String role, String roleHint);
```

Later, when Java 1.5 came with generics, Plexus got the handy new method:

```java
  <T> T lookup(Class<T> klazz);
  <T> T lookup(Class<T> klazz, String roleHint);
```

And it made things great, no need to cast! But under the hood, labels were still only labels. You made them explicit either
via `components.xml` that accepted the `role` and `roleHint` or via annotations like this

```java
@Component(role=Component.class, roleHint="my")
public class MyComponent implements Component {}
```

You explicitly stated here: "class ComponentImpl is keyed by role=`Component.class` and roleHint=`'my'`". One thing
you could not do in Plexus, is to reach for implementation directly: there was no role `MyComponent.class`!

```java
@Requirement
private MyComponent component;
```

## Sisu enters the chat

So far good. But in Eclipse Sisu on other hand things are **slightly different** and many times overlooked. Sisu uses Guice
[JIT/implicit bindings](https://github.com/google/guice/wiki/JustInTimeBindings) generated on the fly. This means that Sisu
can infer many of these things by just doing this:

```java
@Singleton
@Named("my")
public class MyComponent implements Component {}
```

And this component can be injected into series of places: those wanting `Component` but also those wanting `MyComponent`.
So **Sisu can do, wile Plexus DI cannot**, is to make injection happen like this:

```java
@Inject
private MyComponent component;
```

Why is that? As Sisu figures out _effective type of injection point_ and then matches the published ones with it.
But this has also some drawbacks as well... especially if you cannot keep things simple. And how comes Polyglot here?
Well, Maven Core, for sure is not kept simple. The original problem was this implementation:

```java
@Singleton
@Named
public class TeslaModelProcessor implements ModelProcessor {}
```

But wait a second, how does `ModelProcessor` look like? Oh, it looks like this:

```java
public interface ModelProcessor extends ModelLocator, ModelReader {}
```

And there **are components** published implementing [`ModelLocator`](https://github.com/apache/maven/blob/4c059c401ca95cee8c63b3737223ade1dbe9f934/maven-model-builder/src/main/java/org/apache/maven/model/locator/DefaultModelLocator.java) and 
[`ModelReader`](https://github.com/apache/maven/blob/4c059c401ca95cee8c63b3737223ade1dbe9f934/maven-model-builder/src/main/java/org/apache/maven/model/io/DefaultModelReader.java) as well! Basically, `ModelProcessor` 
implementation **can be injected** into spots needing `ModelLocator` or `ModelReader` as well (as they are type 
compatible)!

And the fix? Well, as one can assume, to ["restrict" the type of the component](https://github.com/takari/polyglot-maven/pull/326).
But, the `@Typed` annotation comes with some implications as well...

Great "literature" to skim over:
* [Many times overlooked Eclipse Sisu website](https://eclipse-sisu.github.io/sisu-project/).
* [Javadoc of DefaultModelProcessor](https://github.com/apache/maven/blob/4c059c401ca95cee8c63b3737223ade1dbe9f934/maven-model-builder/src/main/java/org/apache/maven/model/building/DefaultModelProcessor.java#L36-L60)

Remember: you are completely fine as long you keep things simple. The fact **you see one interface does not mean
you have one role**! You need to look into hierarchy as well. While moving from Plexus DI to JSR330, this is one
of the keystones to keep in mind.

Enjoy!
