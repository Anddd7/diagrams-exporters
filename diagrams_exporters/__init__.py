import os
import re
import pydot

from diagrams_ext import (
    Diagram,
    Cluster,
    Edge,
    Node,
    setcluster,
    getcluster,
)

from diagrams_ext.custom import Custom
from diagrams_ext.k8s.podconfig import ConfigMap
from diagrams_ext.custom import Custom
from diagrams_ext.generic.blank import Blank
from diagrams_ext.programming.hashicorp import Terraform
from diagrams_ext.generic.compute import File
from diagrams_patterns import tocluster, fromcluster
import diagrams_exporters.aws


# variables
DEBUG = False
SHOW_PROVIDER = False


def printd(msg):
    if DEBUG:
        print(msg)


def enable_debug():
    global DEBUG
    DEBUG = True


class TerraformGraph:
    def __init__(
        self, filename, resources: dict[str, "Resource"], edge: dict[str, list[str]]
    ):
        self.filename = filename
        self.resources = resources
        self.edge = edge


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


# parset the dot file as a terraform graph, include resources and edges
def parse_dot(filename: str):
    graph = pydot.graph_from_dot_file(filename)[0]
    graph = graph.get_subgraphs()[0]

    resources = parse_resources(graph)
    edges = parse_edges(graph)
    return TerraformGraph(os.path.basename(filename), resources, edges)


# base on the label and name of the nodes to categorize the resources
def parse_resources(graph):
    root = Resource("root", "root", "root", "root")
    for node in graph.get_nodes():
        parent = root
        label = node.get_label().strip('"')
        names = label.split(".")
        while len(names) > 0:
            if names[0].startswith("provider"):
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
                    printd(f"Error: {label}, {names}")
                resource_name = names[1]

                names = names[2:]

            resource = Resource(label, type, resource_type, resource_name)
            if not label.endswith(resource_name):
                # remove the string after resource name
                resource.id = label[: label.rfind(resource_name) + len(resource_name)]

            if resource.get_name() not in parent.resources:
                # debug(f"add {resource.get_name()} into {parent.get_name()}")
                parent.add_resource(resource)
            parent = parent.resources[resource.get_name()]
    return root.resources


# parse the edges into a 1:n dict for lookup, with the same resource id
# Ignore: is_close, there are many inner edges inside module, which is not useful
def parse_edges(graph):
    edges = {}
    for edge in graph.get_edges():
        src, is_close = trim_edge(edge.get_source())
        dst, _ = trim_edge(edge.get_destination())
        if is_close:
            # debug(f"skip inner edge {src} -> {dst}")
            continue

        # debug(f"add edge {src} -> {dst}")

        if src in edges:
            edges[src].append(dst)
        else:
            edges[src] = [dst]
    return edges


def trim_edge(input: str):
    input = input.strip('"')
    input = trim_prefix(input, "[root] ")
    if input.endswith(" (expand)"):
        return trim_suffix(input, " (expand)"), False
    if input.endswith(" (close)"):
        return trim_suffix(input, " (close)"), True
    return input, False


def trim_prefix(input: str, prefix: str):
    if input.startswith(prefix):
        input = input[len(prefix) :]
    return input


def trim_suffix(input: str, suffix: str):
    if input.endswith(suffix):
        input = input[: -len(suffix)]
    return input


# convert to diagrams classes
# cache, is used to build the edge between nodes and clusters
def convert_to_diagrams(terraform_graph: TerraformGraph, filename):
    with Diagram(
        filename,
        show=False,
        direction="BT",
        graph_attr={
            "compound": "true",
            # "concentrate": "true",
            # "splines": "spline",
            "nodesep": "2",
        },
    ):
        cache = {}
        if SHOW_PROVIDER:
            cache["provider"] = Cluster("provider")
        convert_to_digrams_nodes(terraform_graph.resources, cache)
        convert_to_diagrams_edges(terraform_graph.edge, cache)


# map resource to Node or Cluster
# Ignore: data, just a input, no actual resource will be created
# Ignore: var, just a input
# Ignore: povider, TODO, not sure how to display the poviders
# Ignore: filter(), ignore useless resources
def convert_to_digrams_nodes(resources: dict[str, Resource], cache):
    for resource in resources.values():
        if resource.type == "data":
            continue
        if resource.type == "var":
            continue
        if not filter(resource.resource_type, resource.resource_name):
            continue

        if resource.type == "provider":
            if SHOW_PROVIDER:
                parent = getcluster()
                with cache["provider"]:
                    node = get_provider(resource)
                    cache[resource.id] = node
                setcluster(parent)
        elif resource.type == "module":
            with Cluster(f"{resource.id}") as cluster:
                # debug(f"add cluster {resource.id}, {resource.get_name()}")
                convert_to_digrams_nodes(resource.resources, cache)
                cache[resource.id] = cluster
                # add hidden point for cluster edge
                hp_id = f"{resource.id}_hp"
                cache[hp_id] = Node(
                    hp_id, shape="none", width="0", height="0", fontcolor="transparent"
                )
        else:
            # debug(f"add node {resource.id}, {resource.get_name()}")
            node = get_node(resource.resource_type, resource.resource_name)
            cache[resource.id] = node


# render provider as a custom node
def get_provider(resource):
    label = resource.id
    matches = re.match(r'provider\[\\"([^"]+)\\"\]\.?(\w+)?', resource.id)
    if matches:
        registry = matches.group(1)
        name = matches.group(2)
        if name is None:
            label = registry
        else:
            label = f"{registry}\n{name}"

    provider = Terraform(label)
    return provider


# map edges to Edge, with the help of cache
# Ignore: output, are only existing in edge, so it will be skipped since no node is created for them
# Ignore: local, are only existing in edge
def convert_to_diagrams_edges(edges: dict[str, list[str]], cache):
    for src, dsts in edges.items():
        source = cache.get(src)
        if source is None:
            # debug(f"Error: not found the node {src}")
            continue
        for dst in dsts:
            depend = cache.get(dst)
            if depend is None:
                # debug(f"Error: not found the node {dst}")
                continue
            if isinstance(source, Cluster) and isinstance(depend, Cluster):
                continue
            if isinstance(source, Cluster):
                source = cache.get(f"{source.label}_hp", source)
                depend = cache.get(f"{depend.label}_hp", depend)
                printd(f"add edge cluster {source.label} -> {depend.label}")
                fromcluster(
                    source,
                    depend,
                    forward=True,
                    penwidth="2",
                    color="red",
                    style="dashed",
                )
            elif isinstance(depend, Cluster):
                source = cache.get(f"{source.label}_hp", source)
                depend = cache.get(f"{depend.label}_hp", depend)
                printd(f"add edge cluster {source.label} -> {depend.label}")
                tocluster(
                    source,
                    depend,
                    forward=True,
                    penwidth="2",
                    color="red",
                    style="dashed",
                )
            else:
                source - Edge(forward=True, minlen="5") - depend


def filter(type, name):
    if type.startswith("aws"):
        return diagrams_exporters.aws.filter(type, name)
    return True


generic_mapping = {
    "kubernetes_config_map": ConfigMap,
    "local_file": File,
    "rancher2_cluster": "https://avatars.githubusercontent.com/u/9343010",
}


def get_node(type, name):
    if type.startswith("aws"):
        clazz = diagrams_exporters.aws.get_node_class(type, name)
    else:
        clazz = generic_mapping.get(type, Blank)

    if isinstance(clazz, str):
        return Custom(f"{type}\n{name}", clazz)
    return clazz(f"{type}\n{name}")
