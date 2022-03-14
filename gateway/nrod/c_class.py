"""C-Class message models from NROD."""

from datetime import datetime
from typing import Optional
from enum import Enum
import pydantic


class MsgType(Enum):
    """Enumeration of valid C Class message types."""

    CA = 'CA'
    CB = 'CB'
    CC = 'CC'
    CT = 'CT'


class CClassMessage(pydantic.BaseModel):
    """Representation of a c-class message."""

    time: int = pydantic.Field(
        title='UNIX timestamp in milliseconds since the UNIX epoch'
    )

    td: str = pydantic.Field(
        title='Alphanumeric code representing the TD area that the message originates from',
        alias='area_id',
        max_len=2,
        min_len=2,
        regex='[A-Z0-9]{2}'
    )

    msg_type: MsgType = pydantic.Field(
        title='The message type'
    )

    from_berth: Optional[str] = pydantic.Field(
        title='From Berth',
        alias='from',
        max_len=4,
        min_len=4
    )

    to_berth: Optional[str] = pydantic.Field(
        title='To Berth',
        alias='to',
        max_len=4,
        min_len=4
    )

    descr: Optional[str] = pydantic.Field(
        title='The description',
        max_len=4,
        min_len=4
    )

    report_time: Optional[str] = pydantic.Field(
        title='TD Reported time'
    )

    @property
    def msg_time(self) -> datetime:
        """Return the msg timestamp as datetime."""
        return datetime.fromtimestamp(self.time / 1000)
