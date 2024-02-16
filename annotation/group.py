from enum import Enum
from .resource import AwsResource
# Grouping Resource into more generalized name
class ComponentGroup(set, Enum):
    MACHINE             = {AwsResource.EC2}
    SERVERLESS_FUNCTION = {AwsResource.LAMBDA}
    WEBAPP              = {AwsResource.AMPLIFY}
    AUTHENTICATOR       = {AwsResource.COGNITO}

class BoundaryGroup(set, Enum):
    VIRTUAL_NETWORK     = {AwsResource.VPC}
    VIRTUAL_FIREWALL    = {AwsResource.SECURITY_GROUP}
    SUBNET              = {AwsResource.SUBNET}
    IAM                 = {AwsResource.IAM}

class DataStoreGroup(set, Enum):
    FILE_STORAGE        = {AwsResource.S3}
    DATABASE            = {AwsResource.DYNAMODB}