# jlv5-harness

PC-side Python driver for the [Jumperless V5](https://jumperless.org) programmable breadboard, over the MicroPython Raw REPL.

## Installation

```bash
pip install jlv5-harness
# or from source:
pip install -e ".[yaml]"   # include PyYAML for get_state() fallback
```

## Quick start

```python
from jlv5_harness import Harness

with Harness() as h:
    # Route signals
    h.connect(1, "ADC0")          # connect breadboard row 1 to ADC0
    v = h.adc_get(0)              # read voltage at ADC0
    h.disconnect(1, "ADC0")

    # Power rails
    h.dac_set("TOP_RAIL", 3.3)    # set top power rail to 3.3V
    h.dac_set("BOTTOM_RAIL", 0)   # set bottom rail to GND

    # Current monitoring
    i = h.ina_get_current(1)      # amps on TOP_RAIL

    # Waveform generator
    h.wavegen_start(channel=1, waveform="SINE", freq=1000, amplitude=1.0)

    # Board state
    state = h.get_state()         # full snapshot as dict
    h.nodes_clear()               # remove all connections
```

## Node addressing

Nodes can be specified as integers or strings:

| Node | Integer | String |
|------|---------|--------|
| Breadboard rows | 1–60 | `"1"` – `"60"` |
| GND | 100 | `"GND"` |
| Top power rail | 101 | `"TOP_RAIL"` |
| Bottom power rail | 102 | `"BOTTOM_RAIL"` |
| DAC0 (probe) | 106 | `"DAC0"` |
| DAC1 | 107 | `"DAC1"` |
| ADC0–ADC4 | 110–114 | `"ADC0"`–`"ADC4"` |
| GPIO 1–8 | 131–138 | `"GPIO_1"`–`"GPIO_8"` |
| Digital pins D0–D13 | 70–83 | `"D0"`–`"D13"` |
| Analog pins A0–A7 | 86–93 | `"A0"`–`"A7"` |

## Hardware notes

- **Voltage range**: ±8V on all DAC outputs and ADC inputs
- **Bandwidth**: ~8MHz 3dB rolloff; reliable signal routing to ~1MHz
- **Current**: ~300mA per rail/DAC output
- **Crossbar resistance**: ~80Ω per routed path
- DAC0 is wired through an INA219 current sensor to the probe tip — use `ina_get_current(0)` to monitor current draw
- TOP_RAIL also has INA219 monitoring — use `ina_get_current(1)`

## USB ports

The Jumperless exposes four USB serial ports. This driver uses the **third** (Raw REPL):

| Port | Device | Use |
|------|--------|-----|
| 1 | `JLV5port1` | Main terminal (`>` commands) |
| 2 | `JLV5port3` | Arduino UART passthrough |
| **3** | **`JLV5port5`** | **MicroPython Raw REPL ← this driver** |
| 4 | `JLV5port7` | — |

`Harness()` auto-detects the correct port. Pass `port=` explicitly to override.

## API reference

### Connection management

```python
h.connect(node1, node2)           # create connection
h.disconnect(node1, node2)        # remove connection
h.nodes_clear()                   # remove all connections
h.is_connected(node1, node2)      # → bool
```

### Analog I/O

```python
h.adc_get(channel)                # → float volts; channel 0–4 or "ADC0" etc.
h.dac_set(channel, voltage)       # channel: 0/1/"TOP_RAIL"/"BOTTOM_RAIL"
h.dac_get(channel)                # → float volts
```

### Current / power monitoring

```python
h.ina_get_current(sensor=0)       # → float amps; sensor 0=DAC0, 1=TOP_RAIL
h.ina_get_power(sensor=0)         # → float watts
h.ina_get_bus_voltage(sensor=0)   # → float volts
```

### GPIO

```python
h.gpio_set_dir(pin, output=True)
h.gpio_set(pin, value)
h.gpio_get(pin)                   # → bool
h.gpio_set_pull(pin, pull)        # pull: 1=up, -1=down, 0=none
h.pwm(pin, frequency, duty=0.5)
h.pwm_stop(pin)
```

### Waveform generator

```python
h.wavegen_start(channel=1, waveform="SINE", freq=100.0, amplitude=3.3, offset=1.65)
h.wavegen_stop()
```

### Board state

```python
h.get_state()                     # → dict (bridges, power, config)
h.set_state(state_dict)
h.active_slot()                   # → int (0–7)
h.switch_slot(slot)
h.nodes_save(slot=None)
```

### OLED

```python
h.oled_print(text, size=2)
h.oled_clear()
```

### Net info

```python
h.get_net_info(net_num)           # → dict
h.get_num_nets()                  # → int
h.get_num_bridges()               # → int
h.set_net_color(net_num, color)
```

### Low-level execution

```python
stdout, stderr = h.exec("some_micropython_code()")
result = h.eval("expression")     # → str
```

## Hardware-in-the-loop testing

The Jumperless V5's programmable crossbar makes this driver well-suited as a routing layer for hardware-in-the-loop (HIL) tests: signals between a DUT and bench instruments can be (re)connected from Python without physical rewiring, and the onboard DACs / ADCs / INA219s cover stimulus and measurement on the lower-bandwidth pins.

[dwf-mcp](https://github.com/best-effort-labs/dwf-mcp) — an MCP server for the Digilent Analog Discovery 3 — uses this driver in its own hardware test suite to route AD3 pins to known loads/sources for validating scope / wavegen / logic / pattern behavior end-to-end.

## Running tests

```bash
pip install -e ".[dev]"
pytest -m 'not hardware'          # unit tests only (no device needed)
pytest -m hardware                # requires connected Jumperless
```

## Known firmware quirks

- `get_state()` raises `UnicodeError` on some firmware versions. The driver transparently falls back to reading the active slot YAML file (`/slots/slotN.yaml`) — requires `pyyaml` on the host (`pip install jlv5-harness[yaml]`).
