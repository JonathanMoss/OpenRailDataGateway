"""Fixtures for train movement unit tests."""

import pytest

COL = """
{
    "header": {
        "msg_type": "0008",
        "source_dev_id": "VNHY",
        "user_id": "#PEE0031",
        "original_data_source": "TOPS",
        "msg_queue_timestamp": "1511532209000",
        "source_system_id": "TRUST"
    },
    "body": {
        "original_loc_timestamp": "1511528640000",
        "current_train_id": "",
        "train_file_address": "BDI",
        "train_service_code": "56461882",
        "dep_timestamp": "1511528640000",
        "loc_stanox": "36108",
        "train_id": "174M37CF24",
        "original_loc_stanox": "36169",
        "event_timestamp": "1511532180000"
    }
}
""".strip()

COI = """
{
    "header": {
        "msg_type": "0007",
        "source_dev_id": "V2WX",
        "user_id": "#WAELKNK",
        "original_data_source": "SDR",
        "msg_queue_timestamp": "1511531881000",
        "source_system_id": "TRUST"
    },
    "body": {
        "current_train_id": "",
        "train_file_address": "BAX",
        "train_service_code": "56609010",
        "revised_train_id": "86417G1J24",
        "train_id": "86678V1J24",
        "event_timestamp": "1511531880000"
    }
}
""".strip()

COO = """
{
    "header": {
        "msg_type": "0006",
        "source_dev_id": "V3HS",
        "user_id": "#QRP0059",
        "original_data_source": "SDR",
        "msg_queue_timestamp": "1511528282000",
        "source_system_id": "TRUST"
    },
    "body": {
        "reason_code": "TH",
        "current_train_id": "",
        "original_loc_timestamp": "",
        "train_file_address": null,
        "train_service_code": "21734000",
        "toc_id": "20",
        "dep_timestamp": "1511540100000",
        "coo_timestamp": "1511528280000",
        "division_code": "20",
        "loc_stanox": "16416",
        "train_id": "321P42MP24",
        "original_loc_stanox": ""
    }
}
""".strip()

REINSTATEMENT = """
{
    "header": {
        "msg_type": "0005",
        "source_dev_id": "LYUD",
        "user_id": "#QRP0059",
        "original_data_source": "TRUST DA",
        "msg_queue_timestamp": "1511528258000",
        "source_system_id": "TRUST"
    },
    "body": {
        "current_train_id": "",
        "original_loc_timestamp": "",
        "train_file_address": null,
        "train_service_code": "21734000",
        "toc_id": "20",
        "dep_timestamp": "1511533980000",
        "division_code": "20",
        "loc_stanox": "32530",
        "train_id": "321P42MP24",
        "original_loc_stanox": "",
        "reinstatement_timestamp": "1511528220000"
    }
}
""".strip()

MOVEMENT = """
{
    "header": {
    "msg_type": "0003",
    "source_dev_id": "VLA5",
    "user_id": "#QHPA026",
    "original_data_source": "SDR",
    "msg_queue_timestamp": "1511528232000",
    "source_system_id": "TRUST"
},
    "body": {
        "event_type": "DEPARTURE",
        "gbtt_timestamp": "",
        "original_loc_stanox": "",
        "planned_timestamp": "1511524620000",
        "timetable_variation": "0",
        "original_loc_timestamp": "",
        "current_train_id": "",
        "delay_monitoring_point": "true",
        "next_report_run_time": "9",
        "reporting_stanox": "52701",
        "actual_timestamp": "1511524620000",
        "correction_ind": "false",
        "event_source": "MANUAL",
        "train_file_address": null,
        "platform": "",
        "division_code": "79",
        "train_terminated": "false",
        "train_id": "515G531I24",
        "offroute_ind": "false",
        "variation_status": "ON TIME",
        "train_service_code": "25936005",
        "toc_id": "79",
        "loc_stanox": "52701",
        "auto_expected": "true",
        "direction_ind": "",
        "route": "",
        "planned_event_type": "DEPARTURE",
        "next_report_stanox": "52226",
        "line_ind": ""
    }
}
""".strip()

CANCELLATION = """
{
    "header": {
        "msg_type": "0002",
        "source_dev_id": "",
        "user_id": "",
        "original_data_source": "SDR",
        "msg_queue_timestamp": "1511528427000",
        "source_system_id": "TRUST"
    },
    "body": {
        "train_file_address": null,
        "train_service_code": "22721000",
        "orig_loc_stanox": "",
        "toc_id": "88",
        "dep_timestamp": "1511527680000",
        "division_code": "88",
        "loc_stanox": "87701",
        "canx_timestamp": "1511528400000",
        "canx_reason_code": "YI",
        "train_id": "871B26MK24",
        "orig_loc_timestamp": "",
        "canx_type": "EN ROUTE"
    }
}
""".strip()

ACTIVATION = """
{
    "header": {
        "msg_type": "0001",
        "source_dev_id": "",
        "user_id": "",
        "original_data_source": "TSIA",
        "msg_queue_timestamp": "1511528234000",
        "source_system_id": "TRUST"
    },
    "body": {
        "schedule_source": "C",
        "train_file_address": null,
        "schedule_end_date": "2017-12-08",
        "train_id": "775F25MP24",
        "tp_origin_timestamp": "2017-11-24",
        "creation_timestamp": "1511528234000",
        "tp_origin_stanox": "",
        "origin_dep_timestamp": "1511535420000",
        "train_service_code": "25470001",
        "toc_id": "25",
        "d1266_record_number": "00000",
        "train_call_type": "AUTOMATIC",
        "train_uid": "C21373",
        "train_call_mode": "NORMAL",
        "schedule_type": "O",
        "sched_origin_stanox": "77301",
        "schedule_wtt_id": "5F25M",
        "schedule_start_date": "2016-12-12"
    }
}
""".strip()


@pytest.fixture(scope='function')
def raw_activation():
    return ACTIVATION


@pytest.fixture(scope='function')
def raw_cancellation():
    return CANCELLATION


@pytest.fixture(scope='function')
def raw_movement():
    return MOVEMENT


@pytest.fixture(scope='function')
def raw_col():
    return COL


@pytest.fixture(scope='function')
def raw_coi():
    return COI


@pytest.fixture(scope='function')
def raw_coo():
    return COO


@pytest.fixture(scope='function')
def raw_reinstatement():
    return REINSTATEMENT
