from src.core.wifi_scanner import WifiScanner


SAMPLE_NETWORKS = [
    {"ssid": "Net1", "bssid": "AA:BB:CC", "rssi": -40, "channel": 6, "security": "WPA2"},
    {"ssid": "Net2", "bssid": "DD:EE:FF", "rssi": -80, "channel": 11, "security": "Open"},
]


def test_scan_networks_uses_internal_scan(monkeypatch):
    print("TEST: test_scan_networks_uses_internal_scan — patching platform scanner and calling scan_networks")
    scanner = WifiScanner()
    # Patch the platform-specific scanner to return our sample networks
    monkeypatch.setattr(scanner, "_scan_macos", lambda: SAMPLE_NETWORKS)
    networks = scanner.scan_networks()
    assert isinstance(networks, list)
    assert networks == SAMPLE_NETWORKS


def test_get_strongest_network_and_signal():
    print("TEST: test_get_strongest_network_and_signal — populating networks and checking strongest/signal APIs")
    scanner = WifiScanner()
    scanner.networks = SAMPLE_NETWORKS.copy()

    strongest = scanner.get_strongest_network()
    assert strongest is not None
    assert strongest["ssid"] == "Net1"

    # get_signal_strength should return the rssi value for an existing SSID
    assert scanner.get_signal_strength("Net2") == -80
    # unknown SSID -> None
    assert scanner.get_signal_strength("Unknown") is None
