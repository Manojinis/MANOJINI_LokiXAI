"""Unit tests for tool allowlisting, argument schemas, and execution."""

import pytest
from src.lokixai.tools.registry import ToolRegistry
from src.lokixai.tools.app_tools import OpenAppTool, OpenWebsiteTool, LaunchWorkspaceTool
from src.lokixai.tools.system_tools import GetSystemMetricsTool, SetBrightnessTool, SetVolumeTool


def test_tool_registry_registration():
    reg = ToolRegistry()
    assert reg.get("get_system_metrics") is not None
    assert reg.get("set_screen_brightness") is not None
    assert reg.get("set_master_volume") is not None
    assert reg.get("open_application") is not None

    schemas = reg.get_openai_tools()
    assert len(schemas) >= 10
    assert any(s["function"]["name"] == "get_system_metrics" for s in schemas)


def test_open_app_allowlist():
    tool = OpenAppTool()
    # Not allowlisted
    bad_res = tool.execute(app_name="malicious_script.bat")
    assert bad_res.success is False
    assert bad_res.error == "AppNotAllowlisted"


def test_open_website_scheme_validation():
    tool = OpenWebsiteTool()
    bad_scheme = tool.execute(url="javascript:alert(1)")
    assert bad_scheme.success is False
    assert bad_scheme.error == "InvalidScheme"


def test_launch_workspace_presets():
    tool = LaunchWorkspaceTool()
    bad = tool.execute(workspace_name="NonExistentWorkspace")
    assert bad.success is False
    assert bad.error == "InvalidPreset"


def test_argument_validation_error():
    reg = ToolRegistry()
    # Level must be int between 0 and 100
    res = reg.execute("set_master_volume", {"level": 250})
    assert res.success is False
    assert res.error == "InvalidArguments"


def test_get_system_metrics():
    tool = GetSystemMetricsTool()
    res = tool.execute()
    assert res.success is True
    assert "cpu_percent" in res.data
    assert "ram_percent" in res.data
    assert "uptime_str" in res.data
