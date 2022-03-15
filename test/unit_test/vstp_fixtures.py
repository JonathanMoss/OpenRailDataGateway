"""Fixtures for VSTP unit tests."""

import pytest

SCHED = """\
{
    "VSTPCIFMsgV1": {
        "schemaLocation": "http://xml.networkrail.co.uk/ns/2008/Train itm_vstp_cif_messaging_v1.xsd",
        "classification": "industry",
        "timestamp": "1356697917000",
        "owner": "Network Rail",
        "originMsgId": "2012-12-28T12:31:57-00:00vstp.networkrail.co.uk",
        "Sender": {
            "organisation": "Network Rail",
            "application": "TOPS",
            "component": "VSTP"
        },
        "schedule": {
            "schedule_id": "",
            "transaction_type": "Create",
            "schedule_start_date": "2012-12-29",
            "schedule_end_date": "2012-12-29",
            "schedule_days_runs": "0000010",
            "applicable_timetable": "Y",
            "CIF_bank_holiday_running": " ",
            "CIF_train_uid": " 43876",
            "train_status": "1",
            "CIF_stp_indicator": "N",
            "schedule_segment": [{
                "signalling_id": "2C90",
                "uic_code": "",
                "atoc_code": "",
                "CIF_train_category": "OO",
                "CIF_headcode": "",
                "CIF_course_indicator": "",
                "CIF_train_service_code": "24672104",
                "CIF_business_sector": "",
                "CIF_power_type": "EMU",
                "CIF_timing_load": "",
                "CIF_speed": "",
                "CIF_operating_characteristics": "",
                "CIF_train_class": "",
                "CIF_sleepers": "",
                "CIF_reservations": "0",
                "CIF_connection_indicator": "",
                "CIF_catering_code": "",
                "CIF_service_branding": "",
                "CIF_traction_class": "",
                "schedule_location": [{
                    "scheduled_arrival_time": " ",
                    "scheduled_departure_time": "125100",
                    "scheduled_pass_time": " ",
                    "public_arrival_time": " ",
                    "public_departure_time": "125100",
                    "CIF_platform": "1",
                    "CIF_line": "",
                    "CIF_path": " ",
                    "CIF_activity": "TB",
                    "CIF_engineering_allowance": "",
                    "CIF_pathing_allowance": "",
                    "CIF_performance_allowance": "",
                    "location": {
                        "tiploc": {
                            "tiploc_id": "WOKNGHM"
                        }
                    }
                }, {
                    "scheduled_arrival_time": "125630",
                    "scheduled_departure_time": "125730",
                    "scheduled_pass_time": "      ",
                    "public_arrival_time": "      ",
                    "public_departure_time": "      ",
                    "CIF_platform": "1",
                    "CIF_line": "",
                    "CIF_path": "",
                    "CIF_activity": "",
                    "CIF_engineering_allowance": "",
                    "CIF_pathing_allowance": "",
                    "CIF_performance_allowance": "",
                    "location": {
                        "tiploc": {
                            "tiploc_id": "BRACKNL"
                        }
                    }
                }, {
                    "scheduled_arrival_time": "135800",
                    "scheduled_departure_time": " ",
                    "scheduled_pass_time": " ",
                    "public_arrival_time": "135800",
                    "public_departure_time": " ",
                    "CIF_platform": "19",
                    "CIF_line": " ",
                    "CIF_path": "",
                    "CIF_activity": "TF",
                    "CIF_engineering_allowance": " ",
                    "CIF_pathing_allowance": " ",
                    "CIF_performance_allowance": " ",
                    "location": {
                        "tiploc": {
                            "tiploc_id": "WATRLOO"
                        }
                    }
                }]
            }]
        }
    }
}
""".strip()


@pytest.fixture(scope='function')
def raw_vstp():
    return SCHED
