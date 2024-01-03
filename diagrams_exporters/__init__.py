import pydot

from diagrams_ext import (
    Diagram,
    Cluster,
    Edge,
    Node,
)

from diagrams_exporters.aws import (
    filter,
    get_node,
)

# variables
DEBUG = False


def debug(msg):
    if DEBUG:
        print(msg)


class TerraformGraph:
    def __init__(self, resources: dict[str, "Resource"], edge: dict[str, list[str]]):
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
            if not label.endswith(resource_name):
                # remove the string after resource name
                resource.id = label[: label.rfind(resource_name) + len(resource_name)]

            if resource.get_name() not in parent.resources:
                # debug(f"add {resource.get_name()} into {parent.get_name()}")
                parent.add_resource(resource)
            parent = parent.resources[resource.get_name()]

    edges = {}
    for edge in graph.get_edges():
        src = trim_edge(edge.get_source())
        dst = trim_edge(edge.get_destination())

        # debug(f"add edge {src} -> {dst}")

        if src in edges:
            edges[src].append(dst)
        else:
            edges[src] = [dst]

    return TerraformGraph(root.resources, edges)


def trim_edge(input: str):
    return trim_prefix(
        trim_suffix(
            trim_suffix(
                input.strip('"'),
                " (expand)",
            ),
            " (close)",
        ),
        "[root] ",
    )


def trim_prefix(input: str, prefix: str):
    if input.startswith(prefix):
        input = input[len(prefix) :]
    return input


def trim_suffix(input: str, suffix: str):
    if input.endswith(suffix):
        input = input[: -len(suffix)]
    return input


def convert_to_digrams(terraform_graph: TerraformGraph):
    with Diagram(
        "dist/terraform",
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
        convert_to_digrams_nodes(terraform_graph.resources, cache)
        convert_to_diagrams_edges(terraform_graph.edge, cache)


def convert_to_digrams_nodes(resources: dict[str, Resource], cache):
    for resource in resources.values():
        if resource.type == "provider":
            # Node(resource.id)
            continue
        if resource.type == "data":
            continue
        if resource.type == "var":
            continue
        if not filter(resource.resource_type, resource.resource_name):
            continue

        if resource.type == "module":
            with Cluster(
                f"{resource.resource_type}\n{resource.resource_name}"
            ) as cluster:
                # debug(f"add cluster {resource.id}, {resource.get_name()}")
                convert_to_digrams_nodes(resource.resources, cache)
                cache[resource.id] = cluster
        else:
            # debug(f"add node {resource.id}, {resource.get_name()}")
            node = convert_to_node(resource)
            cache[resource.id] = node


def convert_to_node(resource: Resource):
    return get_node(resource.resource_type, resource.resource_name)


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
            if isinstance(source, Cluster):
                debug(f"add edge cluster {source.label} -> {depend.label}")
                continue
            if isinstance(depend, Cluster):
                debug(f"add edge {source.label} -> cluster {depend.label}")
                continue
            source - Edge(forward=True, minlen="5") - depend
