import socket
import logging

logger = logging.getLogger(__name__)

def get_network_interfaces():
    """Get all available network interface IP addresses"""
    interfaces = []
    try:
        # Get hostname
        hostname = socket.gethostname()
        
        # Get all IP addresses
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip not in ['127.0.0.1', '::1'] and not ip.startswith('169.254.'):
                interfaces.append(ip)
        
        # Also try to get local IP addresses
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            if local_ip not in interfaces:
                interfaces.append(local_ip)
        except:
            pass
            
    except Exception as e:
        logger.warning(f"Could not detect network interfaces: {e}")
    
    return list(set(interfaces))  # Remove duplicates 