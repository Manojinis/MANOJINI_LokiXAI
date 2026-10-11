"""System hardware control tools: brightness, volume, audio, battery."""

from __future__ import annotations

import logging
from typing import Optional
from pydantic import BaseModel, Field

from src.lokixai.security.permissions import PermissionLevel
from src.lokixai.monitoring.system_monitor import get_system_monitor
from .base import BaseTool, ToolResult

logger = logging.getLogger("lokixai.tools.system")


# --- Schemas ---

class BrightnessArgs(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Target brightness percentage (0-100)")


class VolumeArgs(BaseModel):
    level: int = Field(..., ge=0, le=100, description="Target volume percentage (0-100)")


class MuteArgs(BaseModel):
    mute: bool = Field(..., description="True to mute master audio, False to unmute")


# --- Tools ---

class GetSystemMetricsTool(BaseTool):
    name = "get_system_metrics"
    description = "Retrieve current laptop telemetry: CPU, RAM, Disk, Battery, Network, and Uptime."
    permission_level = PermissionLevel.SAFE_READ_ONLY

    def execute(self, **kwargs) -> ToolResult:
        try:
            metrics = get_system_monitor().get_current_metrics()
            return ToolResult(
                success=True,
                data=metrics.model_dump(),
                message=f"CPU: {metrics.cpu_percent}%, RAM: {metrics.ram_percent}%, Battery: {metrics.battery_percent}%",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message="Failed to collect system metrics")


class GetBrightnessTool(BaseTool):
    name = "get_screen_brightness"
    description = "Retrieve current laptop screen brightness percentage."
    permission_level = PermissionLevel.SAFE_READ_ONLY

    def execute(self, **kwargs) -> ToolResult:
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()
            val = current[0] if isinstance(current, list) and current else current
            return ToolResult(
                success=True,
                data={"brightness": val},
                message=f"Current display brightness is {val}%",
            )
        except Exception as e:
            logger.warning(f"Hardware brightness query failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message="Brightness query not supported on this display hardware.",
            )


class SetBrightnessTool(BaseTool):
    name = "set_screen_brightness"
    description = "Set laptop screen brightness to a percentage between 0 and 100."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = BrightnessArgs

    def execute(self, level: int, **kwargs) -> ToolResult:
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            # Verify new brightness
            actual = sbc.get_brightness()
            val = actual[0] if isinstance(actual, list) and actual else actual
            return ToolResult(
                success=True,
                data={"brightness": val},
                message=f"Screen brightness successfully set to {val}%.",
            )
        except Exception as e:
            logger.warning(f"Hardware brightness adjustment failed: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Could not adjust brightness: {e}. Note: external monitors or some GPUs do not support DDC/CI.",
            )


class GetVolumeTool(BaseTool):
    name = "get_master_volume"
    description = "Retrieve the current master audio volume percentage and mute status."
    permission_level = PermissionLevel.SAFE_READ_ONLY

    def execute(self, **kwargs) -> ToolResult:
        try:
            import comtypes
            comtypes.CoInitialize()
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = round(volume.GetMasterVolumeLevelScalar() * 100)
            is_muted = bool(volume.GetMute())
            return ToolResult(
                success=True,
                data={"volume": current, "is_muted": is_muted},
                message=f"Master volume is {current}% (Muted: {is_muted})",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Could not read master volume: {e}",
            )


class SetVolumeTool(BaseTool):
    name = "set_master_volume"
    description = "Set master audio volume percentage (0-100)."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = VolumeArgs

    def execute(self, level: int, **kwargs) -> ToolResult:
        try:
            import comtypes
            comtypes.CoInitialize()
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            target_scalar = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(target_scalar, None)
            
            # Unmute automatically if user increases volume above 0
            if level > 0 and volume.GetMute():
                volume.SetMute(0, None)

            actual = round(volume.GetMasterVolumeLevelScalar() * 100)
            return ToolResult(
                success=True,
                data={"volume": actual},
                message=f"Master volume set to {actual}%.",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to adjust audio volume: {e}",
            )


class SetMuteTool(BaseTool):
    name = "set_audio_mute"
    description = "Mute or unmute the system master audio."
    permission_level = PermissionLevel.LOW_RISK_ACTION
    args_schema = MuteArgs

    def execute(self, mute: bool, **kwargs) -> ToolResult:
        try:
            import comtypes
            comtypes.CoInitialize()
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            from ctypes import cast, POINTER

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, comtypes.CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMute(1 if mute else 0, None)
            return ToolResult(
                success=True,
                data={"is_muted": mute},
                message="Master audio muted." if mute else "Master audio unmuted.",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message=f"Failed to toggle audio mute: {e}",
            )


class GetBatteryInfoTool(BaseTool):
    name = "get_battery_status"
    description = "Check the laptop battery percentage, charger status, and estimated remaining time."
    permission_level = PermissionLevel.SAFE_READ_ONLY

    def execute(self, **kwargs) -> ToolResult:
        try:
            import psutil
            bat = psutil.sensors_battery()
            if bat is None:
                return ToolResult(
                    success=True,
                    data={"has_battery": False},
                    message="No battery detected (Desktop PC or AC power source).",
                )
            return ToolResult(
                success=True,
                data={
                    "percent": bat.percent,
                    "plugged": bat.power_plugged,
                    "seconds_left": bat.secsleft,
                },
                message=f"Battery is at {bat.percent}%, Plugged in: {bat.power_plugged}.",
            )
        except Exception as e:
            return ToolResult(success=False, error=str(e), message="Unable to query battery status.")
