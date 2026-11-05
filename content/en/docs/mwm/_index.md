---
title: MWM
description: Maven Workspace Manager
categories: [Documentation]
tags: [docs]
projects: [ MWM ]
weight: 180
---

{{% pageinfo %}}
Maven Workspace Manager
{{% /pageinfo %}}

MWM is a Maven 3.10+ core extension that makes Maven aware of "workspaces". It inspects the Git checkout (using Nisse
JGit support, but without requiring the Nisse extension), and derives a workspace ID from the remote, host, owner,
repository name and current branch. Project artifacts are then installed into a workspace specific directory (by
default `.mwm/$workspaceId` within the local repository), while the local repository itself is used as cache only.

As the workspace follows the current branch, switching branches or Git worktrees also switches the set of
locally installed artifacts. After the first full `mvn install` on a branch, one can move between branches and run
partial builds (using `-f` or `-rf`) without picking up artifacts built from another branch.

MWM steps aside if it detects advanced setups like a chained local repository. It works well combined with Mímir.
See the [introduction blog post](/blog/2026/08/22/meet-mwm/) for more.

Sources: https://github.com/maveniverse/mwm
