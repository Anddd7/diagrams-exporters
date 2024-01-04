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
from diagrams_ext.generic.network import Subnet as Route

KeyPair = IdentityAndAccessManagementIamDataEncryptionKey


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


mapping = {
    "aws_autoscaling_attachment": EC2AutoScaling,
    "aws_autoscaling_group": EC2AutoScaling,
    "aws_cloudwatch_log_group": Cloudwatch,
    "aws_customer_gateway": VPCCustomerGateway,
    "aws_default_network_acl": Nacl,
    "aws_default_route_table": RouteTable,
    "aws_default_vpc": VPC,
    "aws_ec2_transit_gateway_peering_attachment_accepter": TransitGatewayAttachment,
    "aws_ec2_transit_gateway_peering_attachment": TransitGatewayAttachment,
    "aws_ec2_transit_gateway_prefix_list_reference": EC2ElasticIpAddress,
    "aws_ec2_transit_gateway_route": TransitGatewayRouteTable,
    "aws_ec2_transit_gateway_vpc_attachment": TransitGatewayAttachment,
    "aws_ec2_transit_gateway": TransitGateway,
    "aws_egress_only_internet_gateway": InternetGateway,
    "aws_eip": EC2ElasticIpAddress,
    "aws_flow_log": VPCFlowLogs,
    "aws_iam_policy": IAMPermissions,
    "aws_iam_role_policy_attachment": IAMPermissions,
    "aws_iam_role": IAMRole,
    "aws_internet_gateway": InternetGateway,
    "aws_key_pair": KeyPair,
    "aws_kms_key": KMS,
    "aws_nat_gateway": NATGateway,
    "aws_network_acl": Nacl,
    "aws_ram_resource_share": "https://img.icons8.com/ios-filled/50/share-3.png",
    "aws_route_table": RouteTable,
    "aws_route": Route,
    "aws_network_acl_rule": Route,
    "aws_route53_record": Route53,
    "aws_route53_resolver_endpoint": Route53Resolver,
    "aws_route53_resolver_rule": Route53ResolverRule,
    "aws_route53_zone": Route53HostedZone,
    "aws_default_security_group": GenericFirewall,
    "aws_security_group": GenericFirewall,
    "aws_subnet": PublicSubnet,
    "aws_vpc_endpoint_service": Privatelink,
    "aws_vpc_endpoint": Endpoint,
    "aws_vpc": VPC,
    "aws_vpn_gateway_attachment": VpnConnection,
    "aws_vpn_gateway": VpnGateway,
    "aws_lb": ELB,
    "aws_eks_cluster": EKS,
    "aws_launch_template": EC2Instance,
    "aws_lb_target_group": EC2Instances,
}


def get_node_class(type, name):
    return mapping.get(type, General)
