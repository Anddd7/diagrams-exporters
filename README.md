# diagrams-exporters

- in additional to the design phase, diagrams can aslo be used for analysis and monitoring the current architecture.
- to do that, we need to export the 'metadata' from other sources, e.g. terraform, aws cli, etc. then generate the diagrams.

**diagrams-exporters** export the metadata from existing tools, and generate the diagrams.

## Features

- [ ] terraform graph
  - [x] parse & generate nodes
  - [ ] tidy the edges
- [ ] awscli scan
  - depends on the patterns in diagrams-patterns (e.g. vpc with igw, subnet and nat)

## Roadmap

Currently, the **diagrams-patterns** and diagrams-exporters are built as 'diagrams'-extensions. But since the diagrams is inactive, introducing new tools is a necessary step, e.g. d2.

At that time, the **diagrams-patterns** should be a standalone tool, which provide a standard DSL to describe the common patterns in cloud architecture (or other kinds of diagrams). Then, you can translate the DSL to different tools, e.g. diagrams, d2, etc.

The **diagrams-exporters** plays another role to facilitate with productive tools, e.g. terraform, aws cli, etc. It read the metadata, convert to DSL, then generate the diagrams.

A possible structure is:

```mermaid
flowchart BT
  subgraph diagram-exporters
    terraform-exporter
    awscli-exporter
    kubectl-exporter
  end

  subgraph diagrams-patterns
    subgraph common-patterns
      c4-pattern
      layer-arch-pattern    
    end

    subgraph cloud-patterns
      aws-pattern
      azure-pattern
    end

    subgraph dsl
      dsl-parser

      dsl-to-diagrams
      dsl-to-d2
      dsl-to-mermaid
    end
  end

  diagrams-patterns --> diagram-exporters
  diagrams --> diagrams-patterns
  d2 --> diagrams-patterns
  plantuml --> diagrams-patterns
  
  graphviz --> diagrams
  graphviz --> d2

  plantuml
```

## Reference

- graphviz & dot
  - <https://github.com/pydot/pydot>

- d2
  - <https://github.com/terrastruct/d2>
  - <https://github.com/MrBlenny/py-d2>

- read tfstate and generate graph
  - <https://github.com/cycloidio/inframap>
  - <https://github.com/28mm/blast-radius>

- read aws cli and generate graph
  - <https://github.com/Cloud-Architects/cloudiscovery>

- other terraform interesting tools
  - <https://github.com/cycloidio/terracost>
  - <https://pypi.org/project/python-hcl2/>
