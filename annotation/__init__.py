from enum import Enum
from typing import TypeVar
from .resource import AwsResource  # noqa: F401
from .group import BoundaryGroup, ComponentGroup, DataStoreGroup  # noqa: F401
from .block_type import BlockType  # noqa: F401

ResourceName    = TypeVar("ResourceName", bound=Enum)
GroupName       = TypeVar("GroupName", bound=Enum)