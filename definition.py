from enum import Enum
from typing import TypeVar

ResourceName = TypeVar("ResourceName", bound=Enum)

class AwsResource(Enum):
    VPC                 = "aws_vpc"
    SUBNET              = "aws_subnet"
    SECURITY_GROUP      = "aws_security_group"
    ROUTE_TABLE         = "aws_route_table"
    ROUTE_TABLE_ASSOC   = "aws_route_table_association"
    NAT_GATEWAY         = "aws_nat_gateway"
    EC2                 = "aws_instance"
    S3                  = "aws_s3_bucket"
    LAMBDA              = "aws_lambda_function"
    AMPLIFY             = "aws_amplify_app"
    API_GATEWAY         = "aws_api_gateway_rest_api"
    COGNITO             = "aws_cognito_user_pool"
    DYNAMODB            = "aws_dynamodb_table"

# Grouping Resource into more generalized name
class ComponentGroup(set, Enum):
    MACHINE             = {AwsResource.EC2}
    FILE_STORAGE        = {AwsResource.S3}
    SERVERLESS_FUNCTION = {AwsResource.LAMBDA}
    WEBAPP              = {AwsResource.AMPLIFY}
    AUTHENTICATOR       = {AwsResource.COGNITO}
    DATABASE            = {AwsResource.DYNAMODB}

class BoundaryGroup(set, Enum):
    VIRTUAL_NETWORK     = {AwsResource.VPC}
    VIRTUAL_FIREWALL    = {AwsResource.SECURITY_GROUP}
    SUBNET              = {AwsResource.SUBNET}

class Type(Enum):
    RESOURCE    = "resource"
    OUTPUT      = "output"
    VARIABLE    = "var"
    MODULE      = "module"
    PROVIDER    = "provider" 
    LOCAL       = "local"
    DATA        = "data"