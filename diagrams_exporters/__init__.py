import pydot
from diagrams_patterns import (
    Diagram,
    Cluster,
    Edge,
    Node,
)
from diagrams_patterns.aws import VPCCluster

DEBUG = False


def debug(msg):
    if DEBUG:
        print(msg)


class TerraformGraph:
    def __init__(self, resources: dict[str, "Resource"]):
        self.resources = resources


class Resource:
    def __init__(self, keyword: str, type: str, name: str):
        self.keyword = keyword
        self.type = type
        self.name = name
        self.resources = {}

    def add_resource(self, resource: "Resource"):
        self.resources[resource.get_id()] = resource
        resource.parent = self

    def get_id(self):
        if self.name == "":
            return self.type
        return f"{self.type}.{self.name}"


def parse_dot(filename: str):
    graph = pydot.graph_from_dot_file(filename)[0]
    graph = graph.get_subgraphs()[0]

    root = Resource("root", "root", "root")
    for node in graph.get_nodes():
        names = node.get_label().strip('"').split(".")
        parent = root
        while len(names) > 0:
            if names[0] == "data":
                keyword = "data"
                # data.aws_arn.assumerole
                type = f"{names[0]}.{names[1]}"
                name = names[2]

                names = names[3:]
            elif names[0].startswith("provider"):
                # provider[\"registry.terraform.io/hashicorp/aws\"]
                keyword = "provider"
                if names[-1].endswith("]"):
                    type = node.get_label()
                    name = ""
                else:
                    type = ".".join(names[:-1])
                    name = names[-1]
                break
            else:
                keyword = names[0]
                type = names[0]
                name = names[1]

                names = names[2:]

            id = f"{type}.{name}"
            if id not in parent.resources:
                debug(f"add {id} into {parent.get_id()}")
                parent.add_resource(Resource(keyword, type, name))
            parent = parent.resources[id]

    return TerraformGraph(root.resources)


def convert_to_digrams(terraform_graph: TerraformGraph):
    with Diagram("dist/terraform", show=False, graph_attr={"compound": "true"}):
        convert_to_digrams_rec(terraform_graph.resources)


def convert_to_digrams_rec(resources: dict[str, Resource]):
    for resource in resources.values():
        if resource.keyword == "provider":
            continue
        if resource.keyword == "data":
            continue
        if resource.keyword == "var":
            continue

        if resource.keyword == "module":
            with Cluster(resource.get_id()) as cluster:
                convert_to_digrams_rec(resource.resources)
        else:
            node = convert_to_node(resource)


def convert_to_node(resource: Resource):
    return Node(resource.get_id())
