"""Models for train movement messages."""

# pylint: disable=E1101
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


class ChangeOfLocation(pydantic.BaseModel):
    """Representation of an NROD COL message."""

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

    original_loc_timestamp: Union[str, None] = pydantic.Field(
        title='The planned time associated with the original location'
    )

    current_train_id: Union[str, None] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    dep_timestamp: Union[str, None] = pydantic.Field(
        title='The departure time at the location the train is COL'
    )

    loc_stanox: Union[str, None] = pydantic.Field(
        title='New origin STANOX',
        max_length=5
    )

    train_id: Union[str, None] = pydantic.Field(
        title='TRUST ID'
    )

    original_loc_stanox: Union[str, None] = pydantic.Field(
        title='	If the location has been revised, the original STANOX'
    )

    event_timestamp: Union[str, None] = pydantic.Field(
        title='The timestamp of the COO transaction'
    )

    @pydantic.validator('original_loc_stanox', 'loc_stanox')
    @classmethod
    def validate_stanox(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the stanox."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not re.match('[0-9]{5}', val):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {val}'
            )
        return val

    @pydantic.validator('current_train_id', 'train_id')
    @classmethod
    def validate_train_id(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if len(val) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {val}'
            )
        return val

    @pydantic.validator('original_loc_timestamp', 'dep_timestamp', 'event_timestamp')
    @classmethod
    def validate_timestamp(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate a timestamp."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not val.isdecimal():
            raise pydantic.ValidationError(
                f'Not a valid timestamp: {val}'
            )
        return val

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a ChangeOfLocation object from an NROD COL msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


class ChangeOfIdentity(pydantic.BaseModel):
    """Representation of an NROD COI message."""

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

    current_train_id: Union[str, None] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    revised_train_id: Union[str, None] = pydantic.Field(
        title='The new TRUST ID'
    )

    train_id: Union[str, None] = pydantic.Field(
        title='The TRUST ID at activation time'
    )

    event_timestamp: Union[str, None] = pydantic.Field(
        title='The timestamp of the COI transaction'
    )

    @pydantic.validator('event_timestamp')
    @classmethod
    def validate_timestamp(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate a timestamp."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not val.isdecimal():
            raise pydantic.ValidationError(
                f'Not a valid timestamp: {val}'
            )
        return val

    @pydantic.validator('revised_train_id', 'train_id')
    @classmethod
    def validate_train_id(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if len(val) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {val}'
            )
        return val

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a ChangeOfIdentity object from an NROD COI msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


class ChangeOfOrigin(pydantic.BaseModel):
    """Representation of an NRDO COO message."""

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

    reason_code: str = pydantic.Field(
        title='The reason code for the COO',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    current_train_id: Union[str, None] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    original_loc_timestamp: Union[str, None] = pydantic.Field(
        title='The planned time associated with the original location'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    dep_timestamp: Union[str, None] = pydantic.Field(
        title='The departure time at the location the train is COO'
    )

    coo_timestamp: Union[str, None] = pydantic.Field(
        title='The timestamp of the COO transaction'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    loc_stanox: Union[str, None] = pydantic.Field(
        title='New origin STANOX',
        max_length=5
    )

    train_id: Union[str, None] = pydantic.Field(
        title='TRUST ID'
    )

    original_loc_stanox: Union[str, None] = pydantic.Field(
        title='	If the location has been revised, the original STANOX'
    )

    @pydantic.validator('original_loc_stanox', 'loc_stanox')
    @classmethod
    def validate_stanox(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the stanox."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not re.match('[0-9]{5}', val):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {val}'
            )
        return val

    @pydantic.validator('original_loc_timestamp', 'dep_timestamp', 'coo_timestamp')
    @classmethod
    def validate_timestamp(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate a timestamp."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not val.isdecimal():
            raise pydantic.ValidationError(
                f'Not a valid timestamp: {val}'
            )
        return val

    @pydantic.validator('current_train_id', 'train_id')
    @classmethod
    def validate_train_id(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if len(val) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {val}'
            )
        return val

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a ChangeOfOrigin object from an NROD COO msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


class Reinstatement(pydantic.BaseModel):
    """Representation of an NRDO reinstatement message."""

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

    train_id: Union[str, None] = pydantic.Field(
        title='TRUST ID'
    )

    current_train_id: Union[str, None] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    original_loc_timestamp: Union[str, None] = pydantic.Field(
        title='The planned time associated with the original location'
    )

    dep_timestamp: Union[str, None] = pydantic.Field(
        title='The departure time at the location the train is reinstated'
    )

    loc_stanox: Union[str, None] = pydantic.Field(
        title='STANOX where the train is reinstated',
        max_length=5
    )

    original_loc_stanox: Union[str, None] = pydantic.Field(
        title='	If the location has been revised, the original STANOX'
    )

    reinstatement_timestamp: Union[str, None] = pydantic.Field(
        title='The time of the reinstatement transaction'
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    train_file_address: Optional[str] = pydantic.Field(
        title='TOPS train file address, if applicable'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    @pydantic.validator('current_train_id', 'train_id')
    @classmethod
    def validate_train_id(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if len(val) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {val}'
            )
        return val

    @pydantic.validator('original_loc_timestamp', 'dep_timestamp', 'reinstatement_timestamp')
    @classmethod
    def validate_timestamp(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate a timestamp."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not val.isdecimal():
            raise pydantic.ValidationError(
                f'Not a valid timestamp: {val}'
            )
        return val

    @pydantic.validator('original_loc_stanox', 'loc_stanox')
    @classmethod
    def validate_stanox(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the stanox."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not re.match('[0-9]{5}', val):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {val}'
            )
        return val

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, element: dict) -> object:
        """Return a Reinstatement object from an NROD reinstatement msg."""
        kwargs = {**element['body'], **element['header']}
        return cls(**kwargs)


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

    gbtt_timestamp: Union[str, None] = pydantic.Field(
        title='Planned (passenger) event date and time'
    )

    original_loc_stanox: Union[str, None] = pydantic.Field(
        title='	If the location has been revised, the original STANOX'
    )

    planned_timestamp: Union[str, None] = pydantic.Field(
        title='Planned event timestamp'
    )

    timetable_variation: int = pydantic.Field(
        title='minutes variation from the scheduled time at this location'
    )

    original_loc_timestamp: Union[str, None] = pydantic.Field(
        title='The planned time associated with the original location'
    )

    current_train_id: Union[str, None] = pydantic.Field(
        title='If the TRUST ID has been changed, this is the current one'
    )

    delay_monitoring_point: Union[str, bool] = pydantic.Field(
        title='Is this location a delay monitoring point?'
    )

    next_report_run_time: Union[str, None] = pydantic.Field(
        title='Running time (minutes) to the next location'
    )

    reporting_stanox: Union[str, None] = pydantic.Field(
        title='The reporting stanox'
    )

    actual_timestamp: str = pydantic.Field(
        title='The actual reported event time'
    )

    correction_ind: Union[str, bool] = pydantic.Field(
        title='Is this report a correction?'
    )

    event_source: EventSource = pydantic.Field(
        title='Is this an AUTOMATIC, or MANUAL report?'
    )

    train_file_address: Union[str, None] = pydantic.Field(
        title='train file address'
    )

    platform: Union[str, None] = pydantic.Field(
        title='If relevant, platform identity.'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    train_terminated: Union[str, bool] = pydantic.Field(
        title='Has the train terminated?'
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_length=10,
        max_length=10
    )

    offroute_ind: Union[str, bool] = pydantic.Field(
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
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    loc_stanox: Union[str, None] = pydantic.Field(
        title='STANOX where the movement takes place',
        max_length=5
    )

    auto_expected: Union[str, bool] = pydantic.Field(
        title='Set to "true" if an automatic report is expected'
    )

    direction_ind: Union[str, None] = pydantic.Field(
        title='The direction of movement into this report'
    )

    route: Union[str, None] = pydantic.Field(
        title='The route number associated with this movement.'
    )

    planned_event_type: PlannedEventType = pydantic.Field(
        title='The planned type of event'
    )

    next_report_stanox: Union[str, None] = pydantic.Field(
        title='The next planned stanox'
    )

    line_ind: Union[str, None] = pydantic.Field(
        title='If relevant, line identity.'
    )

    @pydantic.validator(
        'auto_expected', 'delay_monitoring_point',
        'correction_ind', 'train_terminated', 'offroute_ind')
    @classmethod
    def validate_bool(cls, value: Union[str, bool]) -> bool:
        """Validate boolean values passed as string."""
        if isinstance(value, bool):
            return value
        if value.strip() == 'true':
            return True
        return False

    @pydantic.validator('next_report_run_time')
    @classmethod
    def validate_run_time(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate next reported run time."""
        if not value or not value.strip():
            return None
        return value.strip()

    @pydantic.validator('route')
    @classmethod
    def validate_route(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate route."""
        if not value or not value.strip():
            return None

        return value.strip()

    @pydantic.validator('direction_ind')
    @classmethod
    def validate_dir(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate direction."""
        if not value or not value.strip():
            return None
        if value.strip() not in ['UP', 'DOWN']:
            raise pydantic.ValidationError(f'Invalid Direction: {value}')
        return value.strip()

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
    def validate_platform_line(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate platform."""
        if not value or not value.strip():
            return None
        return value.strip()

    @pydantic.validator('train_file_address')
    @classmethod
    def validate_train_file_address(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train file address."""
        if not value or not value.strip():
            return None
        return value.strip()

    @pydantic.validator('current_train_id')
    @classmethod
    def validate_train_id(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the train id."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if len(val) != 10:
            raise pydantic.ValidationError(
                f'Invalid TRUST ID: {val}'
            )
        return val

    @pydantic.validator(
        'original_loc_stanox', 'reporting_stanox',
        'next_report_stanox', 'loc_stanox')
    @classmethod
    def validate_stanox(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate the stanox."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not re.match('[0-9]{5}', val):
            raise pydantic.ValidationError(
                f'Invalid STANOX: {val}'
            )
        return val

    @pydantic.validator(
        'gbtt_timestamp', 'planned_timestamp',
        'original_loc_timestamp', 'actual_timestamp')
    @classmethod
    def validate_timestamp(cls, value: Union[str, None]) -> Union[str, None]:
        """Validate a timestamp."""
        if not value or not value.strip():
            return None
        val = value.strip()
        if not val.isdecimal():
            raise pydantic.ValidationError(
                f'Not a valid timestamp: {val}'
            )
        return val

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
        max_length=5
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    dep_timestamp: int = pydantic.Field(
        title='The departure time at the location that the train is cancelled'
    )

    division_code: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    loc_stanox: str = pydantic.Field(
        title='STANOX where the train is being cancelled from',
        max_length=5
    )

    canx_timestamp: int = pydantic.Field(
        title='The departure time at the location that the train is cancelled'
    )

    canx_reason_code: str = pydantic.Field(
        title='The reason code for the cancellation',
        min_length=2,
        max_length=2,
        regex='[0-9A-Z]{2}'
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_length=10,
        max_length=10
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
        min_length=10,
        max_length=10
    )

    train_id: str = pydantic.Field(
        title='TRUST ID',
        min_length=10,
        max_length=10
    )

    tp_origin_timestamp: str = pydantic.Field(
        title='The date the train runs',
        regex='[0-9]{4}-[0-9]{2}-[0-9]{2}',
        min_length=10,
        max_length=10
    )

    creation_timestamp: int = pydantic.Field(
        title='When the service was called in TRUST'
    )

    tp_origin_stanox: Optional[str] = pydantic.Field(
        title='The STANOX for departure of the service',
        max_length=5
    )

    origin_dep_timestamp: int = pydantic.Field(
        title='Timestamp when the train departs its point of origin'
    )

    train_service_code: str = pydantic.Field(
        title='The train service code'
    )

    toc_id: str = pydantic.Field(
        title='The TOC ID, or ZZ',
        min_length=2,
        max_length=2,
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
        min_length=5,
        max_length=6,
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
        max_length=5
    )

    schedule_wtt_id: str = pydantic.Field(
        title='Headcode and speed class',
        min_length=5,
        max_length=5
    )

    schedule_start_date: str = pydantic.Field(
        title='Schedule start date (runs from)',
        regex='[0-9]{4}-[0-9]{2}-[0-9]{2}',
        min_length=10,
        max_length=10

    )

    @pydantic.validator('train_uid')
    @classmethod
    def strip_uid(cls, value: str) -> str:
        """Strip spaces from the UID."""
        return value.strip()

    @pydantic.validator('schedule_source')
    @classmethod
    def validate_sched_source(cls, value: str) -> str:
        """Validate the schedule source."""
        if value.strip() in ('C', 'V'):
            return value.strip()
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
