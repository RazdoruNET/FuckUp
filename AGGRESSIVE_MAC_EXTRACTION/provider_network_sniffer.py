#!/usr/bin/env python3
"""
Provider Network Sniffer
⚠️ ВНИМАНИЕ: Только для авторизованных пентестов
Назначение: Sniffing provider network для перехвата PPPoE discovery пакетов
Методы: Promiscuous mode sniffing, PPPoE discovery capture, MAC extraction

Использование:
python3 provider_network_sniffer.py --interface eth0 --duration 300
python3 provider_network_sniffer.py --interface eth0 --mode promiscuous --duration 600

Зависимости: pip install scapy

⚠️ LEGAL WARNING: Требует доступа к provider network
"""

from scapy.all import *
import threading
import time
import argparse
from collections import defaultdict

class ProviderNetworkSniffer:
    def __init__(self, interface, duration=300):
        self.interface = interface
        self.duration = duration
        self.captured_macs = defaultdict(dict)
        self.running = False
        self.packet_count = 0
    
    def start_promiscuous_sniffing(self):
        """Запуск promiscuous mode sniffing"""
        print("[*] Запуск promiscuous mode sniffing...")
        print(f"[*] Интерфейс: {self.interface}")
        print(f"[*] Длительность: {self.duration} секунд")
        print("[*] ⚠️  Требует root и доступ к provider network")
        
        self.running = True
        
        def packet_handler(packet):
            if not self.running:
                return
            
            self.packet_count += 1
            
            # PPPoE Discovery packets
            if packet.haslayer(PPPoE):
                pppoe = packet[PPPoE]
                src_mac = packet[Ether].src
                
                # PADI (PPPoE Active Discovery Initiation)
                if pppoe.code == 0x09:
                    self.captured_macs['PADI'][src_mac] = {
                        'timestamp': time.time(),
                        'type': 'PADI',
                        'interface': self.interface
                    }
                    print(f"[+] PADI от {src_mac}")
                
                # PADO (PPPoE Active Discovery Offer)
                elif pppoe.code == 0x07:
                    self.captured_macs['PADO'][src_mac] = {
                        'timestamp': time.time(),
                        'type': 'PADO',
                        'interface': self.interface
                    }
                    print(f"[+] PADO от {src_mac} (BRAS)")
                
                # PADR (PPPoE Active Discovery Request)
                elif pppoe.code == 0x19:
                    self.captured_macs['PADR'][src_mac] = {
                        'timestamp': time.time(),
                        'type': 'PADR',
                        'interface': self.interface
                    }
                    print(f"[+] PADR от {src_mac}")
                
                # PADS (PPPoE Active Discovery Session-confirmation)
                elif pppoe.code == 0x65:
                    self.captured_macs['PADS'][src_mac] = {
                        'timestamp': time.time(),
                        'type': 'PADS',
                        'interface': self.interface
                    }
                    print(f"[+] PADS от {src_mac}")
            
            # ARP packets (для MAC адресов)
            elif packet.haslayer(ARP):
                ifPacket[ARP].op == 2:  # ARP reply
                    src_mac = packet[Ether].src
                    src_ip = packet[ARP].psrc
                    
                    self.captured_macs['ARP'][src_mac] = {
                        'ip': src_ip,
                        'timestamp': time.time(),
                        'type': 'ARP-reply'
                    }
                    print(f"[+] ARP: {src_mac} -> {src_ip}")
        
        try:
            # Promiscuous mode sniffing
            sniff(iface=self.interface, prn=packet_handler, 
                  store=False, timeout=self.duration, promisc=True)
        except Exception as e:
            print(f"[-] Ошибка sniffing: {e}")
        
        self.running = False
    
    def analyze_pppoe_tags(self):
        """Анализ PPPoE tags для дополнительной информации"""
        print("[*] Анализ PPPoE tags...")
        
        def tag_handler(packet):
            if packet.haslayer(PPPoE) and packet.haslayer(PPPoETag):
                tags = packet[PPPoETag]
                src_mac = packet[Ether].src
                
                tag_info = {}
                if hasattr(tags, 'type'):
                    tag_info['tag_type'] = hex(tags.type)
                if hasattr(tags, 'length'):
                    tag_info['tag_length'] = tags.length
                
                self.captured_macs['TAGS'][src_mac] = {
                    'timestamp': time.time(),
                    'tags': tag_info
                }
                
                print(f"[+] PPPoE tags от {src_mac}: {tag_info}")
        
        try:
            sniff(iface=self.interface, prn=tag_handler, 
                  filter="pppoed or pppoes", timeout=60, promisc=True)
        except Exception as e:
            print(f"[-] Ошибка tag analysis: {e}")
    
    def generate_report(self):
        """Генерация отчета"""
        print("\n" + "="*60)
        print("ОТЧЕТ PROVIDER NETWORK SNIFFING")
        print("="*60)
        
        total_macs = 0
        unique_macs = set()
        
        for source, macs in self.captured_macs.items():
            if macs:
                print(f"\n[{source.upper()}] - {len(macs)} MAC адресов:")
                print("-" * 60)
                for mac, info in macs.items():
                    unique_macs.add(mac)
                    total_macs += 1
                    print(f"  MAC: {mac}")
                    for key, value in info.items():
                        print(f"    {key}: {value}")
        
        print("\n" + "="*60)
        print(f"Всего обработано пакетов: {self.packet_count}")
        print(f"Всего найдено MAC адресов: {total_macs}")
        print(f"Уникальных MAC адресов: {len(unique_macs)}")
        print("="*60)
        
        return {
            'total': total_macs,
            'unique': len(unique_macs),
            'packets': self.packet_count,
            'macs': dict(self.captured_macs)
        }

def main():
    parser = argparse.ArgumentParser(description='Provider Network Sniffer')
    parser.add_argument('--interface', required=True, help='Network interface')
    parser.add_argument('--duration', type=int, default=300, help='Sniffing duration (seconds)')
    parser.add_argument('--mode', choices=['promiscuous', 'tags', 'all'], default='promiscuous',
                       help='Sniffing mode')
    
    args = parser.parse_args()
    
    print("[*] Provider Network Sniffer")
    print(f"[*] Interface: {args.interface}")
    print(f"[*] Duration: {args.duration} seconds")
    print(f"[*] Mode: {args.mode}")
    print("[*] ⚠️  Требует root и доступ к provider network")
    
    sniffer = ProviderNetworkSniffer(args.interface, args.duration)
    
    if args.mode in ['promiscuous', 'all']:
        sniffer.start_promiscuous_sniffing()
    
    if args.mode in ['tags', 'all']:
        sniffer.analyze_pppoe_tags()
    
    sniffer.generate_report()

if __name__ == "__main__":
    main()
