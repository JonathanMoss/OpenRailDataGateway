"""Parser and models for VSTP from NROD."""

from typing import Union, List, Optional
import re
import pydantic

REF = 'VSTPCIFMsgV1'
DT_REGEX = '[0-9]{4}-[0-9]{2}-[0-9]{2}'


class ScheduleRow(pydantic.BaseModel):
    """Representation of a schedule row."""

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True

    wta: Union[str, None] = pydantic.Field(
        title='Working Time Arrival',
        alias='scheduled_arrival_time',
        default=None
    )

    wtp: Union[str, None] = pydantic.Field(
        title='Working Time Pass',
        alias='scheduled_pass_time',
        default=None
    )

    wtd: Union[str, None] = pydantic.Field(
        title='Working Time Departure',
        alias='scheduled_departure_time',
        default=None
    )

    pta: Union[str, None] = pydantic.Field(
        title='Public Time Arrival',
        alias='public_arrival_time',
        default=None
    )

    ptd: Union[str, None] = pydantic.Field(
        title='Public Time Departure',
        alias='public_departure_time',
        default=None
    )

    path: Union[str, None] = pydantic.Field(
        title='Path (IN)',
        alias='CIF_path',
        default=None
    )

    platform: Union[str, None] = pydantic.Field(
        title='Platform',
        alias='CIF_platform',
        default=None
    )

    line: Union[str, None] = pydantic.Field(
        title='Line (OUT)',
        alias='CIF_line',
        default=None
    )

    activity: Union[str, None] = pydantic.Field(
        title='Activity code',
        alias='CIF_activity',
        default=None
    )

    eng_all: Union[str, None] = pydantic.Field(
        title='Engineering allowance',
        alias='CIF_engineering_allowance',
        default=None
    )

    path_all: Union[str, None] = pydantic.Field(
        title='Pathing allowance',
        alias='CIF_pathing_allowance',
        default=None
    )

    perf_all: Union[str, None] = pydantic.Field(
        title='Performance allowance',
        alias='CIF_performance_allowance',
        default=None
    )

    tiploc: Union[str, None] = pydantic.Field(
        title='TIPLOC',
        alias='tiploc_id'
    )

    @pydantic.validator('*', pre=True)
    @classmethod
    def validate_entry(cls, value) -> Union[str, None]:
        """Validate the entry."""
        if not value or not value.strip():
            return None
        return value.strip()

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, schedule_row: dict) -> object:
        """Creates a ScheduleRow object from an nrod vstp schedule row."""
        sched = schedule_row
        tiploc = sched['location']['tiploc']
        return cls(**sched, **tiploc)


class LocationOrigin(ScheduleRow):
    """Representation of an LO record."""


class LocationIntermediate(ScheduleRow):
    """Representation of an LI record."""


class LocationTerminating(ScheduleRow):
    """Representation of an LT record."""


class BasicScheduleExtra(pydantic.BaseModel):
    """Representation of a VSTP BX record."""

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True

    traction_class: Union[None, str] = pydantic.Field(
        title='Traction Class (not used)',
        default=None
    )

    uic_code: str = pydantic.Field(
        title='UIC code',
        default=None
    )

    atoc_code: str = pydantic.Field(
        title='ATOC code',
        default=None
    )

    applicable_timetable_code: str = pydantic.Field(
        title='Applicable for delay monitoring',
        alias='applicable_timetable',
        default=None
    )

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, schedule: dict) -> object:
        """Creates a BasicScheduleExtra object from an nrod vstp schedule."""
        sched = schedule[REF]['schedule']
        seg = schedule[REF]['schedule']['schedule_segment'][0]
        if not seg:
            return cls(**sched)
        return cls(**sched, **seg)


class BasicSchedule(pydantic.BaseModel):
    """Representation of a VSTP BS record."""

    class Config:
        """Pydantic configuration."""

        allow_population_by_field_name = True

    transaction_type: str = pydantic.Field(
        title='The type of transaction, usually CREATE'
    )

    train_uid: str = pydantic.Field(
        title='The UID of the service',
        alias='CIF_train_uid',
        min_length=5,
        max_length=6
    )

    date_runs_from: str = pydantic.Field(
        title='Schedule start date',
        alias='schedule_start_date',
        regex=DT_REGEX
    )

    date_runs_to: str = pydantic.Field(
        title='Schedule end date',
        alias='schedule_end_date',
        regex=DT_REGEX
    )

    days_run: str = pydantic.Field(
        title='Schedule days run',
        alias='schedule_days_runs',
        regex='[10]{7}'
    )

    bank_holiday_running: Optional[str] = pydantic.Field(
        title='CIF Bank holiday running?',
        alias='CIF_bank_holiday_running',
    )

    train_status: Optional[str] = pydantic.Field(
        title='The status code of the service',
    )

    train_category: Optional[str] = pydantic.Field(
        title='Service category code',
        alias='CIF_train_category',
    )

    train_identity: Optional[str] = pydantic.Field(
        title='The headcode of the service',
        alias='signalling_id',
    )

    course_indicator: Optional[str] = pydantic.Field(
        title='The course indicator',
        alias='CIF_course_indicator'
    )

    train_service_code: Optional[str] = pydantic.Field(
        title='The train service code',
        alias='CIF_train_service_code'
    )

    portion_id: Optional[str] = pydantic.Field(
        title='Portion ID BUSSEC',
        default='X'
    )

    power_type: Optional[str] = pydantic.Field(
        title='The service planned power type',
        alias='CIF_power_type'
    )

    timing_load: Optional[str] = pydantic.Field(
        title='The service timing load',
        alias='CIF_timing_load'
    )

    speed: Optional[str] = pydantic.Field(
        title='The planned service speed value',
        alias='CIF_speed'
    )

    operating_characteristics: Optional[str] = pydantic.Field(
        title='Operating characteristics for the service.',
        alias='CIF_operating_characteristics'
    )

    seating_class: Optional[str] = pydantic.Field(
        title='Planned accomodation code',
        alias='CIF_train_class'
    )

    sleepers: Optional[str] = pydantic.Field(
        title='Sleeper service code',
        alias='CIF_sleepers'
    )

    reservations: Optional[str] = pydantic.Field(
        title='Service reservations code',
        alias='CIF_reservations'
    )

    connection_indicator: Optional[str] = pydantic.Field(
        title='The service connection indicator',
        alias='CIF_connection_indicator'
    )

    catering_code: Optional[str] = pydantic.Field(
        title='Catering code',
        alias='CIF_catering_code'
    )

    service_branding: Optional[str] = pydantic.Field(
        title='Service branding code',
        alias='CIF_service_branding'
    )

    stp_indicator: str = pydantic.Field(
        title='The CIF stp indicator the for the schedule',
        alias='CIF_stp_indicator',
        regex='[NCOP]{1}'
    )

    @pydantic.validator
    @classmethod
    def val_uid(cls, value: str) -> str:
        """Validate uid."""
        val = value.strip()
        if not re.match('[A-Z0-9]{5,6}', val):
            raise pydantic.ValidationError(
                f'Invalid UID: {val}'
            )
        return val

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, schedule: dict) -> object:
        """Creates a BasicSchedule object from an nrod vstp schedule."""
        sched = schedule[REF]['schedule']
        seg = schedule[REF]['schedule']['schedule_segment'][0]
        if not seg:
            return cls(**sched)

        return cls(**sched, **seg)


class MessageDetails(pydantic.BaseModel):
    """Representation of VSTP message details."""

    organisation: str = pydantic.Field(
        title='The sender organisation'
    )

    application: str = pydantic.Field(
        title='The sending application'
    )

    component: str = pydantic.Field(
        title='The component used to create the schedule'
    )

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, schedule: dict) -> object:
        """Creates a MessageDetails object from an nrod vstp schedule."""
        kwargs = schedule[REF]['Sender']
        return cls(**kwargs)


class VSTPSchedule(pydantic.BaseModel):
    """Representation of a VSTP Schedule."""

    class Config:
        """Configure pydantic."""
        pass

    message_details: MessageDetails = pydantic.Field(
        title='Details of the message'
    )

    basic_schedule: BasicSchedule = pydantic.Field(
        title='The basic schedule (BS) record'
    )

    basic_schedule_extra: Optional[BasicScheduleExtra] = pydantic.Field(
        title='The BX record'
    )

    lo_record: Optional[LocationOrigin] = pydantic.Field(
        title='The LO Record'
    )

    li_records: Optional[List[LocationIntermediate]] = pydantic.Field(
        title='LI records'
    )

    lt_record: Optional[LocationTerminating] = pydantic.Field(
        title='The LT Record.'
    )

    @staticmethod
    @pydantic.validate_arguments
    def get_intermediate_rows(schedule_rows: list) -> List[LocationIntermediate]:
        """Return a list of LI objects."""
        schedule_rows = schedule_rows[1:]
        schedule_rows = schedule_rows[:-1]
        return [LocationIntermediate.nrod_factory(row) for row in schedule_rows]

    @classmethod
    @pydantic.validate_arguments
    def nrod_factory(cls, schedule: dict) -> object:
        """Create a VSTP schedule object from an NROD VSTP record."""
        kwargs = {
            'message_details': MessageDetails.nrod_factory(schedule),
            'basic_schedule': BasicSchedule.nrod_factory(schedule)
        }

        rows = schedule[REF]['schedule']['schedule_segment'][0]
        if not rows:
            return cls(**kwargs)

        kwargs['basic_schedule_extra'] = BasicScheduleExtra.nrod_factory(schedule)
        rows = rows['schedule_location']
        kwargs['lo_record'] = LocationOrigin.nrod_factory(rows[0])
        kwargs['lt_record'] = LocationTerminating.nrod_factory(rows[-1])
        kwargs['li_records'] = VSTPSchedule.get_intermediate_rows(rows)
        return cls(**kwargs)
