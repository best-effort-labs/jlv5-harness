"""
jlv5_harness — PC-side Python driver for the Jumperless V5 programmable breadboard.

    from jlv5_harness import Harness

    with Harness() as h:
        h.connect(1, "ADC0")
        v = h.adc_get(0)
        h.dac_set("TOP_RAIL", 3.3)
"""

from .driver import Harness, HarnessError, find_ports

__all__ = ["Harness", "HarnessError", "find_ports"]
__version__ = "0.1.0"
