import pydot

DEBUG = False


def debug(msg):
    if DEBUG:
        print(msg)


class TerraformGraph:
    def __init__(self, resources: dict):
        self.resources = resources


class Resource:
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name
        self.resources = {}

    def add_resource(self, resource: "Resource"):
        self.resources[resource.get_id()] = resource

    def get_id(self):
        if self.name == "":
            return self.type
        return f"{self.type}.{self.name}"


def parse_dot(filename: str):
    graph = pydot.graph_from_dot_file(filename)[0]
    graph = graph.get_subgraphs()[0]
    nodes = graph.get_nodes()

    root = Resource("root", "root")
    for node in nodes:
        names = node.get_label().strip('"').split(".")
        parent = root
        while len(names) > 0:
            if names[0] == "data":
                # data.aws_arn.assumerole
                type = f"{names[0]}.{names[1]}"
                name = names[2]

                names = names[3:]
            elif names[0].startswith("provider"):
                # provider[\"registry.terraform.io/hashicorp/aws\"]
                if names[-1].endswith("]"):
                    type = node.get_label()
                    name = ""
                else:
                    type = ".".join(names[:-1])
                    name = names[-1]
                break
            else:
                type = names[0]
                name = names[1]

                names = names[2:]

            id = f"{type}.{name}"
            if id not in parent.resources:
                debug(f"add {id} into {parent.get_id()}")
                parent.add_resource(Resource(type, name))
            parent = parent.resources[id]

    return TerraformGraph(root.resources)
