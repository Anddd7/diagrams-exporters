import pydot
from diagrams_patterns import (
    Diagram,
    Cluster,
    Edge,
    Node,
)
from diagrams_patterns.aws import VPCCluster

DEBUG = True


def debug(msg):
    if DEBUG:
        print(msg)


class TerraformGraph:
    def __init__(self, resources: dict[str, "Resource"]):
        self.resources = resources


class Resource:
    def __init__(self, id: str, type: str, resource_type: str, resource_name: str):
        self.id = id
        self.type = type
        self.resource_type = resource_type
        self.resource_name = resource_name
        self.resources = {}

    def add_resource(self, resource: "Resource"):
        self.resources[resource.get_name()] = resource
        resource.parent = self

    def get_name(self):
        if self.resource_name == "":
            return self.resource_type
        return f"{self.resource_type}.{self.resource_name}"


def parse_dot(filename: str):
    graph = pydot.graph_from_dot_file(filename)[0]
    graph = graph.get_subgraphs()[0]

    root = Resource("root", "root", "root", "root")
    for node in graph.get_nodes():
        parent = root
        label = node.get_label().strip('"')
        names = label.split(".")
        while len(names) > 0:
            if label.startswith("provider"):
                type = "provider"
                if names[-1].endswith("]"):
                    resource_type = label
                    resource_name = ""
                else:
                    resource_type = ".".join(names[:-1])
                    resource_name = names[-1]

                names = []
            elif names[0] == "data":
                type = "data"
                resource_type = f"{names[0]}.{names[1]}"
                resource_name = names[2]

                names = names[3:]
            else:
                type = names[0]  # include module & var
                resource_type = names[0]
                if len(names) == 1:
                    debug(f"Error: {label}")
                resource_name = names[1]

                names = names[2:]

            resource = Resource(label, type, resource_type, resource_name)

            if resource.get_name() not in parent.resources:
                debug(f"add {resource.get_name()} into {parent.get_name()}")
                parent.add_resource(resource)
            parent = parent.resources[resource.get_name()]

    return TerraformGraph(root.resources)


def convert_to_digrams(terraform_graph: TerraformGraph):
    with Diagram("dist/terraform", show=False, graph_attr={"compound": "true"}):
        cache = {}
        convert_to_digrams_rec(terraform_graph.resources, cache)


def convert_to_digrams_rec(resources: dict[str, Resource], cache):
    for resource in resources.values():
        if resource.type == "provider":
            continue
        if resource.type == "data":
            continue
        if resource.type == "var":
            continue

        if resource.type == "module":
            with Cluster(resource.get_name()) as cluster:
                convert_to_digrams_rec(resource.resources, cache)
                cache[resource.id] = cluster
        else:
            node = convert_to_node(resource)
            cache[resource.id] = node


def convert_to_node(resource: Resource):
    return Node(resource.get_name())
