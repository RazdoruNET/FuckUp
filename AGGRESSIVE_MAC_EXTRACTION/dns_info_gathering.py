#!/usr/bin/env python3
"""
DNS Information Gathering for MAC Extraction
⚠️ ВНИМАНИЕ: Только для авторизованных пентестов
Назначение: Использование DNS для сбора информации о провайдерской инфраструктуре
Методы: DNS enumeration, subdomain discovery, DNS cache poisoning for information gathering

Использование:
python3 dns_info_gathering.py --target 78.37.77.77 --mode enumerate
python3 dns_info_gathering.py --target 78.37.77.77 --mode subdomain --domain rostelecom.ru
python3 dns_info_gathering.py --target 78.37.77.77 --mode zone-transfer

Зависимости: pip install scapy dnspython

⚠️ LEGAL WARNING: Использование без авторизации незаконно
"""

import dns.resolver
import dns.query
import dns.zone
from scapy.all import *
import threading
import time
import argparse
from collections import defaultdict

class DNSInfoGatherer:
    def __init__(self, target_dns):
        self.target_dns = target_dns
        self.gathered_info = defaultdict(dict)
    
    def enumerate_dns_records(self, domain):
        """Полное перечисление DNS записей"""
        print(f"[*] DNS enumeration для {domain} через {self.target_dns}")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']
        
        for record_type in record_types:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [self.target_dns]
                
                answers = resolver.resolve(domain, record_type, timeout=5)
                
                for answer in answers:
                    record_info = {
                        'type': record_type,
                        'value': str(answer),
                        'ttl': answer.ttl,
                        'timestamp': time.time()
                    }
                    
                    self.gathered_info['DNS_ENUM'][str(answer)] = record_info
                    print(f"[+] {record_type}: {answer}")
                    
            except Exception as e:
                print(f"[-] {record_type}: {e}")
    
    def subdomain_discovery(self, domain, wordlist=None):
        """Обнаружение поддоменов"""
        print(f"[*] Subdomain discovery для {domain}")
        
        if not wordlist:
            subdomains = [
                'www', 'mail', 'ftp', 'ns1', 'ns2', 'dns', 'dhcp', 'pppoe',
                'bras', 'radius', 'auth', 'portal', 'admin', 'api', 'vpn',
                'gw', 'gateway', 'router', 'switch', 'firewall', 'proxy'
            ]
        else:
            subdomains = wordlist
        
        found_subdomains = []
        
        for subdomain in subdomains:
            full_domain = f"{subdomain}.{domain}"
            
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = [self.target_dns]
                
                answer = resolver.resolve(full_domain, 'A', timeout=2)
                
                if answer:
                    found_subdomains.append(full_domain)
                    self.gathered_info['SUBDOMAINS'][full_domain] = {
                        'ip': str(answer[0]),
                        'timestamp': time.time()
                    }
                    print(f"[+] Subdomain: {full_domain} -> {answer[0]}")
                    
            except Exception as e:
                continue
        
        return found_subdomains
    
    def attempt_zone_transfer(self, domain):
        """Попытка zone transfer"""
        print(f"[*] Попытка zone transfer для {domain}")
        
        try:
            zone = dns.zone.transfer(domain, self.target_dns, timeout=10)
            
            if zone:
                print(f"[+] Zone transfer успешен!")
                
                for name in zone.keys():
                    node = zone[name]
                    for rdataset in node:
                        for record in rdataset:
                            self.gathered_info['ZONETRANSFER'][str(name)] = {
                                'record': str(record),
                                'timestamp': time.time()
                            }
                            print(f"[+] {name}: {record}")
                
                return True
            else:
                print("[-] Zone transfer не удался")
                return False
                
        except Exception as e:
            print(f"[-] Zone transfer ошибка: {e}")
            return False
    
    def dns_cache_snooping(self):
        """DNS cache snooping для получения информации о запросах"""
        print("[*] DNS cache snooping...")
        
        try:
            # Попытка получить информацию о кэше через random subdomains
            random_domains = [
                f"{time.time()}.cache.test",
                f"{time.time()}.random.test",
                f"{time.time()}.snoop.test"
            ]
            
            for domain in random_domains:
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [self.target_dns]
                    
                    answer = resolver.resolve(domain, 'A', timeout=2)
                    
                    if answer:
                        self.gathered_info['CACHE'][domain] = {
                            'cached': True,
                            'answer': str(answer[0]),
                            'timestamp': time.time()
                        }
                        print(f"[+] Cached: {domain}")
                        
                except:
                    pass
            
        except Exception as e:
            print(f"[-] Cache snooping ошибка: {e}")
    
    def dns_fingerprinting(self):
        """DNS fingerprinting для определения типа DNS сервера"""
        print("[*] DNS fingerprinting...")
        
        try:
            # CHAOS TXT version.bind
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.target_dns]
            
            answer = resolver.resolve('version.bind', 'TXT', 'CH', timeout=5)
            
            if answer:
                version = str(answer[0])
                self.gathered_info['FINGERPRINT']['version'] = version
                print(f"[+] DNS версия: {version}")
                
        except Exception as e:
            print(f"[-] Fingerprinting: {e}")
    
    def generate_report(self):
        """Генерация отчета"""
        print("\n" + "="*60)
        print("ОТЧЕТ DNS INFORMATION GATHERING")
        print("="*60)
        
        for source, info in self.gathered_info.items():
            if info:
                print(f"\n[{source.upper()}] - {len(info)} записей:")
                print("-" * 60)
                for key, value in info.items():
                    print(f"  {key}: {value}")
        
        print("\n" + "="*60)
        print(f"Всего собрано информации: {sum(len(v) for v in self.gathered_info.values())}")
        print("="*60)
        
        return dict(self.gathered_info)

def main():
    parser = argparse.ArgumentParser(description='DNS Information Gathering')
    parser.add_argument('--target', required=True, help='Target DNS server')
    parser.add_argument('--domain', default='rostelecom.ru', help='Target domain')
    parser.add_argument('--mode', choices=['enumerate', 'subdomain', 'zone-transfer', 'cache', 'fingerprint', 'all'],
                       default='all', help='Gathering mode')
    parser.add_argument('--wordlist', help='Subdomain wordlist file')
    
    args = parser.parse_args()
    
    print("[*] DNS Information Gathering")
    print(f"[*] Target DNS: {args.target}")
    print(f"[*] Domain: {args.domain}")
    print(f"[*] Mode: {args.mode}")
    print("[*] ⚠️  Только для авторизованных пентестов")
    
    gatherer = DNSInfoGatherer(args.target)
    
    if args.mode in ['enumerate', 'all']:
        gatherer.enumerate_dns_records(args.domain)
    
    if args.mode in ['subdomain', 'all']:
        gatherer.subdomain_discovery(args.domain)
    
    if args.mode in ['zone-transfer', 'all']:
        gatherer.attempt_zone_transfer(args.domain)
    
    if args.mode in ['cache', 'all']:
        gatherer.dns_cache_snooping()
    
    if args.mode in ['fingerprint', 'all']:
        gatherer.dns_fingerprinting()
    
    gatherer.generate_report()

if __name__ == "__main__":
    main()
