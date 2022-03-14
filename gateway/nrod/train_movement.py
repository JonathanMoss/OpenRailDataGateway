"""Models for train movement messages."""
import re
from typing import Optional, Union
from enum import Enum
import pydantic

DT_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}'
VALID_CANX = [
    'ON CALL', 'AT ORIGIN', 'EN ROUTE', 'OUT OF PLAN'
]

VALID_VAR_STATUS = [
    'EARLY', 'ON TIME', 'LATE', 'OFF ROUTE'
]


class PlannedEventType(Enum):
    """Enumeration of a valid planned event type."""
    DEPARTURE = 'DEPARTURE'
    ARRIVAL = 'ARRIVAL'
    DESTINATION = 'DESTINATION'


class EventSource(Enum):
    """Enumeration of a valid movement event source."""
    MANUAL = 'MANUAL'
    AUTOMATIC = 'AUTOMATIC'


class CallType(Enum):
    """Enumeration of valid call types."""
    AUTOMATIC = 'AUTOMATIC'
    MANUAL = 'MANUAL'


class CallMode(Enum):
    """Enumeration of valid call mode."""
    NORMAL = 'NORMAL'
    OVERNIGHT = 'OVERNIGHT'


class MovementEventType(Enum):
    """Enumeration of valid movement event types."""
    ARRIVAL = 'ARRIVAL'
    DEPARTURE = 'DEPARTURE'


class Movement(pydantic.BaseModel):
    """Representation of an NROD movement message."""

    source_id: str = pydantic.Field(
        title='The source device ID',
        alias='source_dev_id'
    )

    data_source: str = pydantic.Field(
        title='The original data source',
        alias='original_data_source'
    )

    source_system: str = pydantic.Field(
        title='Source system ID',
        alias='source_system_id'
    )

    event_type: MovementEventType = pydantic.Field(
        title='ARRIVAL or DEPARTURE'
    )

    gbtt_timestamp: str = pydantic.Field(
        title='Planned (passenger) event date and time'
    )

    original_loc_stanox: str = pydantic.Field(
        title='	If the location has been revised, the original STANOX'
    )

    planned_timestamp: Union[str, None] = pydantic.Field(
        title='Planned event date and time'
    )

    timetable_variation: int = pydantic.Field(
        title='minutes variation from the scheduled time at this location'
    )

    original_loc_timestamp: Union[str, None] = pydantic.Field(
        title='The planned time associated with the original location'
    )

    current_train_id: Optional[str] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    delay_monitoring_point: bool = pydantic.Field(
        title='Is this location a delay monitoring point?'
    )

    next_report_run_time: Union[str, int] = pydantic.Field(
        title='Running time (minutes) to the next location'
    )

    reporting_stanox: Optional[Union[str, None]] = pydantic.Field(
        title='The reporting stanox'
    )

    actual_timestamp: str = pydantic.Field(
        title='The actual reported event time'
    )

    correction_ind: bool = pydantic.Field(
        title='Is this report a correction?'
    )

    event_source: EventSource = pydantic.Field(
        title='Is this an AUTOMATIC, or MANUAL report?'
    )

    train_file_address: Optional[Union[str, None]] = pydantic.Field(
        title='train file address'
    )

    platform: Optional[Union[str, None]] = pydantic.Field(
        title='If relevant, platform identity.'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    train_terminated: bool = pydantic.Field(
        title='Has the train terminated?'
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_len=10,
        max_len=10
    )

    offroute_ind: bool = pydantic.Field(
        title='is the service off-route?'
    )

    variation_status: str = pydantic.Field(
        title='The variation status detail'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    loc_stanox: str = pydantic.Field(
        title='STANOX where the train is being cancelled from',
        max_len=5
    )

    auto_expected: Union[str, bool] = pydantic.Field(
        title='Set to "true" if an automatic report is expected'
    )

    direction_indicator: Optional[Union[str, None]] = pydantic.Field(
        'The direction of movement into this report'
    )

    route: Optional[Union[str, None]] = pydantic.Field(
        'The route number associated with this movement.'
    )

    planned_event_type: PlannedEventType = pydantic.Field(
        'The planned type of event'
    )

    next_report_stanox: Optional[Union[str, None]] = pydantic.Field(
        title='The next planned stanox'
    )

    line_ind: Optional[Union[str, None]] = pydantic.Field(
        title='If relevant, line identity.'
    )

    @pydantic.validator('next_report_run_time')
    @classmethod
    def validate_run_time(cls, value: str) -> Union[None, int]:
        """Validate next reported run time."""
        if not value or not value.strip():
            return None

        return int(value.strip())

    @pydantic.validator('auto_expected')
    @classmethod
    def validate_auto_exp(cls, value: str) -> bool:
        """Validate auto expected."""
        if value == 'true':
            return True
        return False

    @pydantic.validator('route')
    @classmethod
    def validate_route(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate route."""
        if not value or not value.strip():
            return None

        return value.strip()

    @pydantic.validator('direction_indicator')
    @classmethod
    def validate_dir(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate direction."""
        if not value:
            return None

        if value not in ['UP', 'DOWN']:
            raise pydantic.ValidationError(f'Invalid Direction: {value}')

    @pydantic.validator('variation_status')
    @classmethod
    def validate_var_status(cls, value: str) -> str:
        """Validate the variation status."""
        if value not in VALID_VAR_STATUS:
            raise pydantic.ValidationError(
                f'Invalid variation status: {value}'
            )
        return value

    @pydantic.validator('platform', 'line_ind')
    @classmethod
    def validate_platform_line(cls, value: str) -> Union[str, None]:
        """Validate platform."""
        if not value or not value.strip():
            return None

        return value.strip()

    @pydantic.validator('train_file_address')
    @classmethod
    def validate_train_file_address(cls, value: str) -> Union[str, None]:
        """Validate the train file address."""
        if not value or not value.strip():
            return None

        return value

    @pydantic.validator('current_train_id')
    @classmethod
    def validate_train_id(cls, value: str) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        if len(value) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {value}'
            )
        return value

    @pydantic.validator('original_loc_stanox', 'reporting_stanox', 'next_report_stanox')
    @classmethod
    def validate_stanox(cls, value: str) -> Union[str, None]:
        """Validate the stanox."""
        if not value or not value.strip():
            return None
        if not re.match('[0-9]{5}', value):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {value}'
            )
        return value

    @pydantic.validator(
        'gbtt_timestamp', 'planned_timestamp',
        'original_loc_timestamp', 'actual_timestamp')
    @classmethod
    def validate_timestamp(cls, value: str) -> Union[str, None]:
        """Validate a timestamp."""
        val = value.strip()
        if not val:
            return None

        return int(val)

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a Movement object from an NROD movement msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


class Cancellation(pydantic.BaseModel):
    """Representation of an NROD cancellation message."""

    source_id: str = pydantic.Field(
        title='The source device ID',
        alias='source_dev_id'
    )

    data_source: str = pydantic.Field(
        title='The original data source',
        alias='original_data_source'
    )

    source_system: str = pydantic.Field(
        title='Source system ID',
        alias='source_system_id'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    orig_loc_stanox: str = pydantic.Field(
        title='OOP Cancellations, where the service should have been',
        max_len=5
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    dep_timestamp: int = pydantic.Field(
        title='The departure time at the location that the train is cancelled'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    loc_stanox: str = pydantic.Field(
        title='STANOX where the train is being cancelled from',
        max_len=5
    )

    canx_timestamp: int = pydantic.Field(
        title='The departure time at the location that the train is cancelled'
    )

    canx_reason_code: str = pydantic.Field(
        title='The reason code for the cancellation',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_len=10,
        max_len=10
    )

    orig_loc_timestamp: Union[int, str] = pydantic.Field(
        title='OOP Cancellations, dep time where the train should have been'
    )

    canx_type: str = pydantic.Field(
        title='The type of cancellation'
    )

    @pydantic.validator('orig_loc_timestamp')
    @classmethod
    def validate_timestamp(cls, value) -> Union[int, None]:
        """Validate orig_loc_timestamp."""
        if not value:
            return None
        return int(value)

    @pydantic.validator('canx_type')
    @classmethod
    def validate_canx_type(cls, value: str) -> str:
        """Validate the cancellation type."""
        if value not in VALID_CANX:
            raise pydantic.ValidationError(
                f'Invalid cancellation type: {value}'
            )
        return value

    @pydantic.validator('orig_loc_stanox', 'loc_stanox')
    @classmethod
    def validate_stanox(cls, value: str) -> Union[str, None]:
        """Validate the stanox."""
        if not value:
            return None
        if not re.match('[0-9]{5}', value):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {value}'
            )
        return value

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a Cancellation object from an NROD activation msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


class Activation(pydantic.BaseModel):
    """Representation of an NROD activation message."""

    source_id: str = pydantic.Field(
        title='The source device ID',
        alias='source_dev_id'
    )

    data_source: str = pydantic.Field(
        title='The original data source',
        alias='original_data_source'
    )

    source_system: str = pydantic.Field(
        title='Source system ID',
        alias='source_system_id'
    )

    schedule_source: str = pydantic.Field(
        title='The schedule source'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    schedule_end_date: str = pydantic.Field(
        title='End date of the schedule (runs to)',
        regex='[0-9]{4}-[0-9]{2}-[0-9]{2}',
        min_len=10,
        max_len=10
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_len=10,
        max_len=10
    )

    tp_origin_timestamp: str = pydantic.Field(
        title='The date the train runs',
        regex='[0-9]{4}-[0-9]{2}-[0-9]{2}',
        min_len=10,
        max_len=10
    )

    creation_timestamp: int = pydantic.Field(
        title='When the service was called in TRUST'
    )

    tp_origin_stanox: Optional[str] = pydantic.Field(
        title='The STANOX for departure of the service',
        max_len=5
    )

    origin_dep_timestamp: int = pydantic.Field(
        title='Timestamp when the train departs its point of origin'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_len=2,
        max_len=2,
        regex='[0-9A-Z]{2}'
    )

    d1266_record_number: str = pydantic.Field(
        title='TOPS unique ID, or 00000'
    )

    train_call_type: CallType = pydantic.Field(
        title='The activation(call) type - AUTOMATIC or MANUAL'
    )

    train_uid: str = pydantic.Field(
        title='Unique [sic] ID of the service',
        min_len=5,
        max_len=6,
        regex='[ A-Z0-9]{5,6}'
    )

    train_call_mode: CallMode = pydantic.Field(
        title='The call mode - NORMAL or OVERNIGHT'
    )

    schedule_type: str = pydantic.Field(
        title='CIF Schedule type',
        regex='[CNOP]{1}'
    )

    sched_origin_stanox: str = pydantic.Field(
        title='Origin STANOX',
        max_len=5
    )

    schedule_wtt_id: str = pydantic.Field(
        title='Headcode and speed class',
        min_len=5,
        max_len=5
    )

    schedule_start_date: str = pydantic.Field(
        title='Schedule start date (runs from)',
        regex='[0-9]{4}-[0-9]{2}-[0-9]{2}',
        min_len=10,
        max_len=10

    )

    @pydantic.validator('train_uid')
    @classmethod
    def strip_uid(cls, value: str) -> str:
        return value.strip()

    @pydantic.validator('schedule_source')
    @classmethod
    def validate_sched_source(cls, value: str) -> str:
        """Validate the schedule source."""
        if value == 'C' or value == 'V':
            return value

        return 'V'

    @pydantic.validator('tp_origin_stanox', 'sched_origin_stanox')
    @classmethod
    def validate_stanox(cls, value: str) -> Union[str, None]:
        """Validate the stanox."""
        if not value:
            return None
        if not re.match('[0-9]{5}', value):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {value}'
            )
        return value

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return an Activation object from an NROD activation msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)
