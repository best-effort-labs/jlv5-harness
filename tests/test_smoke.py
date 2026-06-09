"""
Smoke tests — require a physically connected Jumperless V5.
Run with: pytest -m hardware
"""
import pytest
from jlv5_harness import Harness, find_ports


@pytest.fixture(scope="module")
def jl():
    ports = find_ports()
    if len(ports) < 3:
        pytest.skip("Jumperless not connected")
    with Harness() as h:
        yield h


@pytest.mark.hardware
def test_ports_found():
    ports = find_ports()
    assert len(ports) >= 3, f"Expected ≥3 ports, got {ports}"


@pytest.mark.hardware
def test_connect_and_clear(jl):
    jl.nodes_clear()
    jl.connect(1, 2)
    assert jl.is_connected(1, 2)
    jl.disconnect(1, 2)
    jl.nodes_clear()


@pytest.mark.hardware
def test_adc_reads_float(jl):
    v = jl.adc_get(0)
    assert isinstance(v, float)
    assert -9.0 < v < 9.0


@pytest.mark.hardware
def test_dac_roundtrip(jl):
    jl.dac_set("TOP_RAIL", 3.3)
    got = jl.dac_get("TOP_RAIL")
    assert abs(got - 3.3) < 0.2, f"Expected ~3.3V, got {got}"
    jl.dac_set("TOP_RAIL", 0.0)


@pytest.mark.hardware
def test_get_state_returns_dict(jl):
    state = jl.get_state()
    assert isinstance(state, dict)
