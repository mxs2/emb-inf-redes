from src.core.network_scanner import NetworkScanner


SAMPLE_DEVICES = [{"ip": "192.168.1.2", "mac": "AA:BB:CC", "hostname": "device1"}]


def test_scan_devices_uses_arp_when_requested(monkeypatch):
    """When caller disables nmap, scan_devices should call the ARP method."""
    print("TEST: test_scan_devices_uses_arp_when_requested — patch _scan_with_arp and call scan_devices(use_nmap=False)")
    scanner = NetworkScanner()

    # Patch ARP scanner to return our sample devices
    monkeypatch.setattr(scanner, "_scan_with_arp", lambda: SAMPLE_DEVICES)

    devices = scanner.scan_devices(use_nmap=False)
    assert isinstance(devices, list)
    assert devices == SAMPLE_DEVICES


def test_local_ip_and_detect_range(monkeypatch):
    print("TEST: test_local_ip_and_detect_range — patch get_local_ip and verify detected range format")
    scanner = NetworkScanner()
    # Patch get_local_ip to a deterministic value
    monkeypatch.setattr(scanner, "get_local_ip", lambda: "172.16.5.10")

    detected = scanner._detect_network_range()
    assert isinstance(detected, str)
    # basic sanity: network should contain the first three octets
    assert "172.16.5." in detected or detected.startswith("172.16.5")
