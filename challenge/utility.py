import socket
from typing import Optional


def get_free_port(start_port: int, end_port: int, host: str = "localhost") -> Optional[int]:
    """
    Scans for an available port between start_port and end_port on the given host.

    Returns:
        int: The first available port found.
        None: If no ports are available in the given range.
    """
    for port in range(start_port, end_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)  # Prevent long hangs on some systems
            result = sock.connect_ex((host, port))
            if result != 0:
                # Port is available
                print(f"[INFO] Port {port} is available.")
                return port

    print("[WARNING] No available ports found in the given range.")
    return None
