# This file was auto-generated by Fern from our API Definition.

import datetime as dt
import typing

from ..core.datetime_utils import serialize_datetime

try:
    import pydantic.v1 as pydantic  # type: ignore
except ImportError:
    import pydantic  # type: ignore


class SessionCreatedResponseData(pydantic.BaseModel):
    status: str = pydantic.Field(description="The current status of the session.")
    message: str = pydantic.Field(description="A message providing more details about the session status.")
    session_id: str = pydantic.Field(description="The unique identifier for the session.")
    url: str = pydantic.Field(description="The URL associated with the session.")
    screenshot: str = pydantic.Field(description="A base64 encoded string of the screenshot, empty if not available.")

    def json(self, **kwargs: typing.Any) -> str:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().json(**kwargs_with_defaults)

    def dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        kwargs_with_defaults: typing.Any = {"by_alias": True, "exclude_unset": True, **kwargs}
        return super().dict(**kwargs_with_defaults)

    class Config:
        frozen = True
        smart_union = True
        json_encoders = {dt.datetime: serialize_datetime}
