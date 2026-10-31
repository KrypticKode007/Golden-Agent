import ctypes
import os

class SomaticHardware(ctypes.Structure):
    _fields_ = [
        ("loop_latency_ms", ctypes.c_double),
        ("memory_rss_mb", ctypes.c_double),
        ("optical_flow_drift", ctypes.c_double),
        ("energy_reserve", ctypes.c_double)
    ]

def load_native_math_accelerator():
    """Links Python memory spaces directly into compiled .so binary segments."""
    try:
        lib_path = os.path.abspath("libkryptic_math.so")
        lib = ctypes.CDLL(lib_path)
        lib.calculate_somatic_friction_native.argtypes = [ctypes.POINTER(SomaticHardware), ctypes.c_double, ctypes.c_double]
        lib.calculate_somatic_friction_native.restype = ctypes.c_double
        return lib
    except Exception as e:
        print(f"Native binary link unavailable, reverting to Python mathematical baseline: {e}")
        return None
          
