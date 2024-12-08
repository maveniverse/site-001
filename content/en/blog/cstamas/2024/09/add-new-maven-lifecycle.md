---
title: "How to add new Maven lifecycle mapping"
date: 2024-09-07T14:55:22+01:00
draft: false
authors: cstamas
author: cstamas ([@cstamas](https://bsky.app/profile/cstamas.bsky.social))
categories:
  - Blog
tags:
  - lifecycle
  - packaging
projects:
  - Maven
---

Ever repeating question from plugin/extension developers is "how to add new packaging" (in a "modern way"). 
For ages we did it by manually crafting `plexus.xml` in the plugin or extension JAR, that was not only error-prone 
but also tedious. But, indeed it had a great value as one could easily filter the XML (ie filtering plugin versions). 
But, plexus XML is plexus XML... yuck. So what now?

Here is an example from Eclipse Tycho: The `tycho-maven-plugin` originally defined this Plexus XML (and yes, it did 
filter for versions as well):

```xml
<component-set>
  <components>
    <component>
      <role>org.apache.maven.lifecycle.mapping.LifecycleMapping</role>
      <role-hint>p2-installable-unit</role-hint>
      <implementation>
        org.apache.maven.lifecycle.mapping.DefaultLifecycleMapping
      </implementation>
      <configuration>
        <lifecycles>
          <lifecycle>
            <id>default</id>
            <phases>
              <validate>
                org.eclipse.tycho:tycho-packaging-plugin:${project.version}:build-qualifier,
                org.eclipse.tycho:tycho-packaging-plugin:${project.version}:validate-id,
                org.eclipse.tycho:tycho-packaging-plugin:${project.version}:validate-version
              </validate>
              <initialize>
                org.eclipse.tycho:target-platform-configuration:${project.version}:target-platform
              </initialize>
              <process-resources>
                org.apache.maven.plugins:maven-resources-plugin:${resources-plugin.version}:resources
              </process-resources>
              <package>
                org.eclipse.tycho:tycho-packaging-plugin:${project.version}:package-iu,
                org.eclipse.tycho:tycho-p2-plugin:${project.version}:p2-metadata-default
              </package>
              <install>
                org.apache.maven.plugins:maven-install-plugin:${install-plugin.version}:install,
                org.eclipse.tycho:tycho-p2-plugin:${project.version}:update-local-index
              </install>
              <deploy>
                org.apache.maven.plugins:maven-deploy-plugin:${deploy-plugin.version}:deploy
              </deploy>
            </phases>
          </lifecycle>
        </lifecycles>
      </configuration>
    </component>
  </components>
</component-set>
```

So, how to migrate this off plexus XML? 

We know Plexus XML "defines" components, managed by Plexus DI (and based by not so friendly Maven internal classes).
Our goal would be then to create a JSR330 component. So, let's create a "support class" first:

```java
package org.eclipse.tycho.maven.lifecycle;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

import org.apache.maven.lifecycle.mapping.Lifecycle;
import org.apache.maven.lifecycle.mapping.LifecycleMapping;
import org.apache.maven.lifecycle.mapping.LifecyclePhase;

import javax.inject.Provider;

public abstract class LifecycleMappingProviderSupport implements Provider<LifecycleMapping> {

    private static final String DEFAULT_LIFECYCLE_KEY = "default";

    private final Lifecycle defaultLifecycle;
    private final LifecycleMapping lifecycleMapping;

    public LifecycleMappingProviderSupport() {
        this.defaultLifecycle = new Lifecycle();
        this.defaultLifecycle.setId(DEFAULT_LIFECYCLE_KEY);
        this.defaultLifecycle.setLifecyclePhases(loadMapping());

        this.lifecycleMapping = new LifecycleMapping() {
            @Override
            public Map<String, Lifecycle> getLifecycles() {
                return Collections.singletonMap(DEFAULT_LIFECYCLE_KEY, defaultLifecycle);
            }

            @Override
            public List<String> getOptionalMojos(String lifecycle) {
                return null;
            }

            @Override
            public Map<String, String> getPhases(String lifecycle) {
                if (DEFAULT_LIFECYCLE_KEY.equals(lifecycle)) {
                    return defaultLifecycle.getPhases();
                } else {
                    return null;
                }
            }
        };
    }

    private Map<String, LifecyclePhase> loadMapping() {
        Properties properties = new Properties();
        try (InputStream inputStream = getClass().getResourceAsStream(getClass().getSimpleName() + ".properties")) {
            properties.load(inputStream);
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
        HashMap<String, LifecyclePhase> result = new HashMap<>();
        for (String phase : properties.stringPropertyNames()) {
            result.put(phase, new LifecyclePhase(properties.getProperty(phase)));
        }
        return result;
    }

    @Override
    public LifecycleMapping get() {
        return lifecycleMapping;
    }
}
```

Using this support class, our actual mapping becomes "just" a simple empty class, that maps the component name (that
is mapping name) onto data:

```java
package org.eclipse.tycho.maven.plugin;

import org.eclipse.tycho.maven.lifecycle.LifecycleMappingProviderSupport;

import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
@Named("p2-installable-unit")
public class P2InstallableUnitLifecycleMappingProvider extends LifecycleMappingProviderSupport {}
```

And we add the following Java Properties file to the same package where class above is. The "binary name" of 
the properties file should be `org/eclipse/tycho/maven/plugin/P2InstallableUnitLifecycleMappingProvider.properties`:

```properties
validate=org.eclipse.tycho:tycho-packaging-plugin:${project.version}:build-qualifier,\
  org.eclipse.tycho:tycho-packaging-plugin:${project.version}:validate-id,\
  org.eclipse.tycho:tycho-packaging-plugin:${project.version}:validate-version
initialize=org.eclipse.tycho:target-platform-configuration:${project.version}:target-platform
process-resources=org.apache.maven.plugins:maven-resources-plugin:${resources-plugin.version}:resources
package=org.eclipse.tycho:tycho-packaging-plugin:${project.version}:package-iu,\
  org.eclipse.tycho:tycho-p2-plugin:${project.version}:p2-metadata-default
install=org.apache.maven.plugins:maven-install-plugin:${install-plugin.version}:install,\
  org.eclipse.tycho:tycho-p2-plugin:${project.version}:update-local-index
deploy=org.apache.maven.plugins:maven-deploy-plugin:${deploy-plugin.version}:deploy
```

And finally, all we need to do is to enable filtering on resources. And we have the very same effect as with huge
Plexus XML.

To verify ourselves, just add a  small UT, just to check the things:

```java
package org.eclipse.tycho.maven.plugin;

import org.apache.maven.lifecycle.mapping.LifecycleMapping;
import org.apache.maven.lifecycle.mapping.LifecycleMojo;
import org.apache.maven.lifecycle.mapping.LifecyclePhase;
import org.eclipse.sisu.launch.Main;
import org.junit.jupiter.api.Test;

import javax.inject.Inject;
import javax.inject.Named;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;

@Named
public class LifecycleMappingTest {
    @Inject
    private Map<String, LifecycleMapping> lifecycleMappings;

    @Test
    void smoke() {
        LifecycleMappingTest self = Main.boot(LifecycleMappingTest.class);
        assertEquals(7, self.lifecycleMappings.size());
        System.out.println("All mappings defined in this plugin:");
        for (Map.Entry<String, LifecycleMapping> mapping : self.lifecycleMappings.entrySet()) {
            System.out.println("* " + mapping.getKey());
            for (Map.Entry<String, LifecyclePhase> phases : mapping.getValue().getLifecycles().get("default").getLifecyclePhases().entrySet()) {
                System.out.println("  " + phases.getKey());
                for (LifecycleMojo mojo : phases.getValue().getMojos()) {
                    System.out.println("   -> " + mojo.getGoal());
                }
            }
        }
    }
}
```

Enjoy!