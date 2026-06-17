import importlib

import pandas as pd

from audit.module_audit import MODULE_AUDIT_COLUMNS, run_module_audit


def test_audit_modules_importable():
    assert importlib.import_module("audit")
    assert importlib.import_module("audit.module_audit")
    assert importlib.import_module("audit.system_audit")
    assert importlib.import_module("audit.ui_audit")
    assert importlib.import_module("audit.release_report")


def test_module_audit_output_fields_complete_on_empty_frame():
    result = run_module_audit(pd.DataFrame())

    assert list(result.columns) == MODULE_AUDIT_COLUMNS
    assert not result.empty
    assert set(result["status"]).issubset({"PASS", "WARN", "FAIL"})


def test_module_audit_warns_when_runtime_fields_missing():
    result = run_module_audit(pd.DataFrame({"ticker": ["000001"]}))

    realtime = result[result["module_name"].eq("Realtime Layer")].iloc[0]
    assert realtime["status"] == "WARN"
    assert bool(realtime["is_importable"]) is True
    assert bool(realtime["is_callable"]) is True
    assert bool(realtime["required_fields_present"]) is False
