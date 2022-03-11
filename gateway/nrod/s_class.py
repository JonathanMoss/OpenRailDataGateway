"""S-Class message models from NROD."""

from datetime import datetime
from enum import Enum
import pydantic


class MsgType(Enum):
    """Enumeration of valid S Class message types."""
    SF = 'SF'
    SG = 'SG'
    SH = 'SH'


class SClassMessage(pydantic.BaseModel):
    """Representation of an s-class message."""

    time: int = pydantic.Field(
        title='The timestamp of the message'
    )

    td: str = pydantic.Field(
        title='The TD reference, or name',
        alias='area_id',
        max_len=2,
        min_len=2,
        regex='[A-Z0-9]{2}'
    )

    address: str = pydantic.Field(
        title='The address (hex)',
        max_len=2,
        min_len=2,
        regex='[A-Z0-9]{2}'
    )

    msg_type: MsgType = pydantic.Field(
        title='The message type'
    )

    data: str = pydantic.Field(
        title='The Signalling Data (hex)',
        max_len=2,
        min_len=2,
        regex='[A-Z0-9]{2}'
    )

    @property
    def msg_time(self) -> datetime:
        """Return the msg timestamp as datetime."""
        return datetime.fromtimestamp(self.time / 1000)

    @property
    def address_dec(self) -> int:
        """Return the address as decimal."""
        return int(self.address, 16)

    @property
    def lsb_first(self) -> str:
        """Return a binary representation of the data, LSB FIRST."""
        return bin(int(self.data, 16))[2:].zfill(8)

    @property
    def msb_first(self) -> str:
        """Return a binary representation of the data, MSB FIRST."""
        lsb = self.lsb_first
        return lsb[::-1]
