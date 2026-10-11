"""Real-time system health and hardware telemetry monitor."""

from __future__ import annotations

import datetime
import os
import threading
import time
from typing import Callable, List, Optional
from pydantic import BaseModel, Field
import psutil


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float


class SystemMetrics(BaseModel):
    """Snapshot of laptop hardware telemetry."""
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    cpu_percent: float = 0.0
    cpu_count: int = 1
    cpu_freq_mhz: Optional[float] = None
    ram_total_gb: float = 0.0
    ram_used_gb: float = 0.0
    ram_available_gb: float = 0.0
    ram_percent: float = 0.0
    disk_total_gb: float = 0.0
    disk_used_gb: float = 0.0
    disk_free_gb: float = 0.0
    disk_percent: float = 0.0
    battery_percent: Optional[float] = None
    battery_plugged: Optional[bool] = None
    battery_time_left_str: Optional[str] = None
    net_sent_speed_kbps: float = 0.0
    net_recv_speed_kbps: float = 0.0
    uptime_str: str = "0h 0m"
    top_processes: List[ProcessInfo] = Field(default_factory=list)


class SystemMonitor:
    """Collects real-time system metrics using background worker."""

    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._listeners: List[Callable[[SystemMetrics], None]] = []
        self._last_net_bytes_sent = 0
        self._last_net_bytes_recv = 0
        self._last_net_time = time.time()
        self._latest_metrics: SystemMetrics = self.get_current_metrics()

    def add_listener(self, callback: Callable[[SystemMetrics], None]) -> None:
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[SystemMetrics], None]) -> None:
        if callback in self._listeners:
            self._listeners.remove(callback)

    def get_latest(self) -> SystemMetrics:
        return self._latest_metrics

    def get_current_metrics(self) -> SystemMetrics:
        """Capture an immediate telemetry snapshot."""
        now = time.time()
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count(logical=True) or 1
        freq = psutil.cpu_freq()
        cpu_freq_mhz = freq.current if freq else None

        # Memory
        mem = psutil.virtual_memory()
        ram_total = round(mem.total / (1024 ** 3), 2)
        ram_used = round(mem.used / (1024 ** 3), 2)
        ram_avail = round(mem.available / (1024 ** 3), 2)
        ram_percent = mem.percent

        # Disk (Primary drive)
        root_path = os.getenv("SystemDrive", "C:") + "\\"
        try:
            disk = psutil.disk_usage(root_path)
            disk_total = round(disk.total / (1024 ** 3), 2)
            disk_used = round(disk.used / (1024 ** 3), 2)
            disk_free = round(disk.free / (1024 ** 3), 2)
            disk_percent = disk.percent
        except Exception:
            disk_total = disk_used = disk_free = disk_percent = 0.0

        # Battery
        battery = psutil.sensors_battery()
        bat_percent = None
        bat_plugged = None
        bat_left_str = None
        if battery is not None:
            bat_percent = round(battery.percent, 1)
            bat_plugged = battery.power_plugged
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED and battery.secsleft > 0:
                hours = battery.secsleft // 3600
                mins = (battery.secsleft % 3600) // 60
                bat_left_str = f"{hours}h {mins}m remaining"
            elif bat_plugged:
                bat_left_str = "Plugged In"
            else:
                bat_left_str = "Calculating..."

        # Network speed
        net = psutil.net_io_counters()
        dt = max(now - self._last_net_time, 0.001)
        if self._last_net_bytes_sent > 0:
            net_sent_kbps = max(0.0, round(((net.bytes_sent - self._last_net_bytes_sent) / dt) / 1024, 1))
            net_recv_kbps = max(0.0, round(((net.bytes_recv - self._last_net_bytes_recv) / dt) / 1024, 1))
        else:
            net_sent_kbps = 0.0
            net_recv_kbps = 0.0

        self._last_net_bytes_sent = net.bytes_sent
        self._last_net_bytes_recv = net.bytes_recv
        self._last_net_time = now

        # Uptime
        boot_time = psutil.boot_time()
        uptime_secs = int(now - boot_time)
        up_days = uptime_secs // 86400
        up_hours = (uptime_secs % 86400) // 3600
        up_mins = (uptime_secs % 3600) // 60
        uptime_str = f"{up_days}d {up_hours}h {up_mins}m" if up_days > 0 else f"{up_hours}h {up_mins}m"

        # Top processes by memory
        procs: List[ProcessInfo] = []
        try:
            for p in sorted(
                psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']),
                key=lambda x: x.info['memory_info'].rss if x.info.get('memory_info') else 0,
                reverse=True
            )[:6]:
                try:
                    info = p.info
                    name = info.get('name') or 'unknown'
                    mem_rss = info['memory_info'].rss / (1024 * 1024) if info.get('memory_info') else 0
                    procs.append(ProcessInfo(
                        pid=info.get('pid') or 0,
                        name=name,
                        cpu_percent=round(info.get('cpu_percent') or 0.0, 1),
                        memory_mb=round(mem_rss, 1)
                    ))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        metrics = SystemMetrics(
            cpu_percent=round(cpu_percent, 1),
            cpu_count=cpu_count,
            cpu_freq_mhz=round(cpu_freq_mhz, 0) if cpu_freq_mhz else None,
            ram_total_gb=ram_total,
            ram_used_gb=ram_used,
            ram_available_gb=ram_avail,
            ram_percent=round(ram_percent, 1),
            disk_total_gb=disk_total,
            disk_used_gb=disk_used,
            disk_free_gb=disk_free,
            disk_percent=round(disk_percent, 1),
            battery_percent=bat_percent,
            battery_plugged=bat_plugged,
            battery_time_left_str=bat_left_str,
            net_sent_speed_kbps=net_sent_kbps,
            net_recv_speed_kbps=net_recv_kbps,
            uptime_str=uptime_str,
            top_processes=procs,
        )
        self._latest_metrics = metrics
        return metrics

    def start(self) -> None:
        """Start the background monitoring thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True, name="LokiSystemMonitor")
        self._thread.start()

    def stop(self) -> None:
        """Stop background monitoring."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _monitor_loop(self) -> None:
        while self._running:
            try:
                metrics = self.get_current_metrics()
                for listener in list(self._listeners):
                    try:
                        listener(metrics)
                    except Exception:
                        pass
            except Exception:
                pass
            time.sleep(self.interval)


_global_monitor: Optional[SystemMonitor] = None


def get_system_monitor(interval: float = 2.0) -> SystemMonitor:
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = SystemMonitor(interval=interval)
        _global_monitor.start()
    return _global_monitor
