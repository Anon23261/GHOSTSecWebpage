import socket
import requests

def get_local_ip():
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "Could not determine local IP"

def get_public_ip():
    try:
        # Get public IP
        response = requests.get('https://api.ipify.org')
        return response.text
    except:
        return "Could not determine public IP"

if __name__ == "__main__":
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print("\nGhostSec Access Information:")
    print("-" * 50)
    print("For friends on your local network:")
    print(f"HTTP:  http://{local_ip}")
    print(f"HTTPS: https://{local_ip}")
    print("\nFor friends outside your network (requires port forwarding):")
    print(f"HTTP:  http://{public_ip}")
    print(f"HTTPS: https://{public_ip}")
    print("\nNOTE: To allow access from outside your network:")
    print("1. Configure port forwarding on your router:")
    print("   - Forward port 80 to your local IP:", local_ip)
    print("   - Forward port 443 to your local IP:", local_ip)
    print("2. Allow these ports in Windows Firewall")
    print("\nPress Enter to exit...")
