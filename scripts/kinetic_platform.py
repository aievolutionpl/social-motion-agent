"""Small platform helpers copied into a Kinetic Film job's private runtime."""
import os
import subprocess
import sys


def memory_gib():
    if sys.platform == "win32":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
                (name, ctypes.c_ulonglong) for name in
                ("total_phys", "avail_phys", "total_page", "avail_page", "total_virtual", "avail_virtual", "extended")]

        value = MemoryStatus()
        value.length = ctypes.sizeof(value)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):
            raise OSError("Cannot determine available render memory")
        return value.avail_phys / 2 ** 30
    if sys.platform == "darwin":
        result = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, check=True)
        return int(result.stdout) / 2 ** 30 * .7
    return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_AVPHYS_PAGES") / 2 ** 30


def workers_for(resolution, requested=None):
    per_worker = {"720": 1, "1080": 3, "4k": 10}[resolution]
    available = memory_gib()
    if available < per_worker:
        raise ValueError(f"Only {available:.1f} GiB available; {resolution} needs about {per_worker} GiB. Close apps or lower --res.")
    safe = max(1, min(3, int(available // per_worker), max(1, (os.cpu_count() or 1) // 3)))
    return min(requested or 1, safe)
