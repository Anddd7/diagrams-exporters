# simplify the resources, merge the resources with same type and name
# e.g. aws_ec2_transit_gateway_peering_attachment -> aws_ec2_transit_gateway

# map the resource type to icon node

from diagrams_ext import (
    Diagram,
    Cluster,
    Edge,
    Node,
)
from diagrams_ext.aws.network import *
from diagrams_ext.aws.security import *
from diagrams_ext.aws.management import *
from diagrams_ext.aws.database import *
from diagrams_ext.aws.compute import *
from diagrams_ext.aws.general import *
from diagrams_patterns.aws import VPCCluster


def filter(type, name):
    # if type.endswith("subnet_group"):
    #     return False
    # if type in [
    #     "aws_vpc_dhcp_options",
    #     "aws_vpc_dhcp_options_association",
    #     "aws_vpc_ipv4_cidr_block_association",
    #     "aws_vpn_gateway_route_propagation",
    # ]:
    #     return False
    return True


icon_mapping = {
    "aws_cloudwatch_log_group": Cloudwatch,
    "aws_customer_gateway": VPCCustomerGateway,
    "aws_default_network_acl": Nacl,
    "aws_default_route_table": RouteTable,
    "aws_default_vpc": VPC,
    "aws_ec2_transit_gateway": TransitGateway,
    "aws_ec2_transit_gateway_peering_attachment": TransitGatewayAttachment,
    "aws_ec2_transit_gateway_peering_attachment_accepter": TransitGatewayAttachment,
    "aws_ec2_transit_gateway_prefix_list_reference": EC2ElasticIpAddress,
    "aws_ec2_transit_gateway_route": TransitGatewayRouteTable,
    "aws_ec2_transit_gateway_vpc_attachment": TransitGatewayAttachment,
    "aws_egress_only_internet_gateway": InternetGateway,
    "aws_eip": EC2ElasticIpAddress,
    "aws_flow_log": VPCFlowLogs,
    "aws_iam_policy": IAMPermissions,
    "aws_iam_role": IAMRole,
    "aws_iam_role_policy_attachment": IAMPermissions,
    "aws_internet_gateway": InternetGateway,
    "aws_nat_gateway": NATGateway,
    "aws_network_acl": Nacl,
    "aws_ram_principal_association": IAM,
    "aws_ram_resource_association": IAM,
    "aws_ram_resource_share": IAM,
    "aws_route": RouteTable,
    "aws_route53_resolver_endpoint": Route53Resolver,
    "aws_route53_resolver_rule": Route53ResolverRule,
    "aws_route_table": RouteTable,
    "aws_route_table_association": RouteTable,
    "aws_subnet": PublicSubnet,
    "aws_vpc": VPC,
    "aws_vpn_gateway": VpnGateway,
    "aws_vpn_gateway_attachment": VpnConnection,
}


def get_node(type, name):
    return icon_mapping.get(type, General)(f"{type}\n{name}")
