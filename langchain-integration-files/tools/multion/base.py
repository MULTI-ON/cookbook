"""Base class for Gmail tools."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import Field

from langchain.tools.base import BaseTool
from langchain.tools.gmail.utils import build_resource_service




class MultionBaseTool(BaseTool):
    """Base class for MultiOn tools."""
    pass
