# diagrams-exporters

- in additional to the design phase, diagrams can aslo be used for analysis and monitoring the current architecture.
- to do that, we need to export the 'metadata' from other sources, e.g. terraform, aws cli, etc. then generate the diagrams.

**diagrams-exporters** export the metadata from existing tools, and generate the diagrams.

## Features

- [ ] terraform graph
- [ ] awscli scan
  - depends on the patterns in diagrams-patterns (e.g. vpc with igw, subnet and nat)

## Reference

- [ ] <https://github.com/terrastruct/d2?tab=readme-ov-file#community-aplugins>

- [ ] read tfstate and generate graph
  - <https://github.com/cycloidio/inframap>
  - <https://github.com/28mm/blast-radius>

- [ ] read aws cli and generate graph
  - <https://github.com/Cloud-Architects/cloudiscovery>

- [ ] other terraform interesting tools
  - <https://github.com/cycloidio/terracost>
  - <https://pypi.org/project/python-hcl2/>
