# Комплексный план извлечения MAC адресов PPPoE соседей

## ⚠️ ВНИМАНИЕ

**Этот план предназначен ТОЛЬКО для авторизованных пентестов**
**Использование без письменного разрешения незаконно**
**Нарушение законов может привести к уголовной ответственности**

---

## Исполнительная сводка

**Цель**: Извлечение MAC адресов PPPoE клиентов соседних квартир/домов
**Методы**: Агрессивные атаки на provider infrastructure
**Уровень риска**: КРИТИЧЕСКИЙ
**Требуемый доступ**: Provider network или BRAS compromise

---

## Стратегия атаки

### Этап 1: Разведка (Reconnaissance)

**Цель**: Сбор информации о provider infrastructure

**Методы**:
1. **DNS Information Gathering** - Сбор информации через DNS
2. **Network Analysis** - Анализ provider network topology
3. **BRAS Fingerprinting** - Определение типа и версии BRAS

**Инструменты**:
- `dns_info_gathering.py` - DNS enumeration и subdomain discovery
- Traceroute и BGP analysis
- Nmap для port scanning

**Ожидаемые результаты**:
- Список DNS серверов провайдера
- Сетевая топология
- Информация о BRAS (IP, MAC, тип оборудования)

---

### Этап 2: Provider Network Access

**Цель**: Получение доступа к provider network

**Методы**:
1. **Physical Access** - Физический доступ к provider equipment
2. **Insider Threat** - Компрометация сотрудника провайдера
3. **Network Compromise** - Компрометация provider network

**Требования**:
- Физический доступ к провайдерскому оборудованию
- Insider в провайдере
- Или компрометация provider network

**Сложность**: ОЧЕНЬ ВЫСОКАЯ
**Вероятность успеха**: ОЧЕНЬ НИЗКАЯ

---

### Этап 3: BRAS Compromise

**Цель**: Компрометация BRAS для доступа к PPPoE session table

**Методы**:
1. **Vulnerability Exploitation** - Эксплуатация уязвимостей BRAS
2. **SNMP Brute Force** - Перебор SNMP community strings
3. **Direct Access** - Прямой доступ через SSH/Telnet

**Инструменты**:
- `aggressive_mac_extraction.py` - BRAS compromise script
- Metasploit для эксплуатации уязвимостей
- Nmap для vulnerability scanning

**Ожидаемые результаты**:
- Доступ к BRAS CLI
- Доступ к PPPoE session table
- Список всех активных PPPoE клиентов с MAC адресами

**Сложность**: ВЫСОКАЯ
**Вероятность успеха**: НИЗКАЯ-СРЕДНЯЯ

---

### Этап 4: Provider Network Sniffing

**Цель**: Перехват PPPoE discovery пакетов в provider network

**Методы**:
1. **Promiscuous Mode Sniffing** - Sniffing в promiscuous mode
2. **Port Mirroring** - Использование SPAN port на switch
3. **Tap Installation** - Установка network tap

**Инструменты**:
- `provider_network_sniffer.py` - Provider network sniffer
- Wireshark для packet analysis
- tcpdump для packet capture

**Ожидаемые результаты**:
- Перехват PADI/PADO/PADR/PADS пакетов
- MAC адреса всех PPPoE клиентов
- PPPoE credentials (если PAP включен)

**Сложность**: СРЕДНЯЯ
**Вероятность успеха**: СРЕДНЯЯ

---

### Этап 5: MITM Attacks

**Цель**: MITM атаки для перехвата PPPoE трафика

**Методы**:
1. **ARP Spoofing** - ARP spoofing для MITM
2. **Rogue PPPoE AC** - Создание поддельного PPPoE AC
3. **Session Hijacking** - Hijacking PPPoE сессий

**Инструменты**:
- `pppoe_mitm_interceptor.py` - PPPoE MITM interceptor
- Ettercap для ARP spoofing
- Bettercap для network attacks

**Ожидаемые результаты**:
- Перехват PPPoE credentials
- MAC адреса клиентов
- Возможность модификации трафика

**Сложность**: СРЕДНЯЯ
**Вероятность успеха**: СРЕДНЯЯ

---

## Детальные инструкции

### 1. DNS Information Gathering

```bash
# DNS enumeration
python3 dns_info_gathering.py --target 78.37.77.77 --domain rostelecom.ru --mode enumerate

# Subdomain discovery
python3 dns_info_gathering.py --target 78.37.77.77 --domain rostelecom.ru --mode subdomain

# Zone transfer attempt
python3 dns_info_gathering.py --target 78.37.77.77 --domain rostelecom.ru --mode zone-transfer
```

**Цель**: Получение информации о provider infrastructure

**Ожидаемые результаты**:
- Список DNS серверов
- Поддомены провайдера
- Network topology информация

---

### 2. BRAS Compromise

```bash
# Попытка эксплуатации BRAS уязвимости
python3 aggressive_mac_extraction.py --target 100.76.128.1 --mode exploit

# SNMP brute force
python3 aggressive_mac_extraction.py --target 100.76.128.1 --mode snmp-brute

# Прямой доступ к базе данных
python3 aggressive_mac_extraction.py --target 100.76.128.1 --mode direct-access
```

**Цель**: Получение доступа к BRAS и PPPoE session table

**Ожидаемые результаты**:
- Доступ к BRAS CLI
- PPPoE session table
- MAC адреса всех клиентов

**Примечание**: Требует успешной эксплуатации уязвимости или правильных credentials

---

### 3. Provider Network Sniffing

```bash
# Promiscuous mode sniffing
sudo python3 provider_network_sniffer.py --interface eth0 --duration 300 --mode promiscuous

# PPPoE tags analysis
sudo python3 provider_network_sniffer.py --interface eth0 --duration 60 --mode tags
```

**Цель**: Перехват PPPoE discovery пакетов

**Требования**:
- Доступ к provider network
- Root права
- Promiscuous mode support

**Ожидаемые результаты**:
- MAC адреса PPPoE клиентов
- PPPoE discovery packets
- Дополнительная информация из PPPoE tags

---

### 4. PPPoE MITM Interception

```bash
# ARP spoofing
sudo python3 pppoe_mitm_interceptor.py --interface eth0 --target 192.168.0.1 --mode arp-spoof

# Rogue PPPoE AC
sudo python3 pppoe_mitm_interceptor.py --interface eth0 --mode rogue-ac --bras-mac 44:6A:2E:37:15:BE

# Session hijacking
sudo python3 pppoe_mitm_interceptor.py --interface eth0 --mode session-hijack
```

**Цель**: Перехват PPPoE credentials и MAC адресов

**Требования**:
- Доступ к локальной сети
- Root права
- Возможность ARP spoofing

**Ожидаемые результаты**:
- PPPoE credentials
- MAC адреса клиентов
- Session IDs

---

## Риски и последствия

### Юридические риски

**Уголовная ответственность**:
- Несанкционированный доступ к компьютерной информации (Ст. 272 УК РФ)
- Нарушение тайны переписки и связи (Ст. 138 УК РФ)
- Мошенничество в сфере IT (Ст. 274 УК РФ)

**Гражданская ответственность**:
- Штрафы за нарушение законодательства
- Компенсация ущерба провайдеру
- Возмещение убытков пострадавшим

**Административная ответственность**:
- Блокировка интернет-доступа
- Внесение в черные списки
- Ограничение в использовании IT услуг

### Технические риски

**Provider Detection**:
- IDS/IPS детекция атак
- Анализ аномалий в network traffic
- Мониторинг BRAS logs

**Countermeasures**:
- Блокировка IP адреса атакующего
- Изоляция compromised systems
- Усиление security measures

---

## Методы защиты

### Provider Side

1. **BRAS Hardening**
   - Отключение SNMP или использование SNMPv3
   - Сложные passwords для management
   - Регулярное обновление firmware
   - Мониторинг BRAS logs

2. **Network Segmentation**
   - VLAN для разных клиентов
   - ACL для ограничения доступа
   - Firewall rules для BRAS

3. **Monitoring**
   - IDS/IPS для детекции атак
   - SIEM для correlation событий
   - Анализ аномалий в traffic

### Client Side

1. **PPPoE Security**
   - Отключение PAP аутентификации
   - Использование CHAP/MSCHAP2
   - Регулярная смена passwords

2. **Network Security**
   - Мониторинг ARP таблицы
   - Использование static ARP entries
   - Внедрение ARP spoofing detection

---

## Альтернативные методы

### Legal Methods

1. **OSINT**
   - Поиск информации в открытых источниках
   - Анализ public BGP data
   - Geolocation analysis

2. **Social Engineering**
   - Получение информации от сотрудников
   - Фишинг атаки (требует авторизации)
   - Impersonation (требует авторизации)

3. **Physical Reconnaissance**
   - Наблюдение за provider equipment
   - Анализ physical infrastructure
   - Social engineering на месте

---

## Заключение

### Реалистичность

**Извлечение MAC адресов соседних PPPoE клиентов через роутер невозможно** без:
- Доступа к provider network
- Компрометации BRAS
- Или физического доступа к provider equipment

### Рекомендации

**Для легального анализа**:
1. Использовать OSINT методы
2. Анализировать public information
3. Проводить authorized penetration testing
4. Получать письменное разрешение

**Для понимания рисков**:
1. Изучить PPPoE архитектуру
2. Понять provider network topology
3. Оценить security measures провайдера
4. Рассмотреть альтернативные методы

### Этические соображения

**Использование этих методов без авторизации**:
- Незаконно
- Неэтично
- Опасно для атакующего
- Может привести к уголовной ответственности

**Рекомендуется**:
- Получать письменное разрешение
- Использовать только в authorized scope
- Сообщать о найденных уязвимостях
- Соблюдать законы и этику

---

## Приложения

### Созданные скрипты

1. `aggressive_mac_extraction.py` - BRAS compromise
2. `provider_network_sniffer.py` - Provider network sniffing
3. `dns_info_gathering.py` - DNS information gathering
4. `pppoe_mitm_interceptor.py` - PPPoE MITM interception

### Цели атаки

- **BRAS**: 100.76.128.1 (VNOV-BRAS2)
- **DNS**: 78.37.77.77, 212.48.197.77
- **CGNAT**: 188.254.2.98
- **Provider**: PJSC Rostelecom (AS12389)

### Ссылки

- [УК РФ Ст. 272](http://www.consultant.ru/document/cons_doc_LAW_27690/)
- [УК РФ Ст. 138](http://www.consultant.ru/document/cons_doc_LAW_27690/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [PTES Standard](https://www.pentest-standard.org/)

---
**План создан для образовательных целей**
**Использование без авторизации запрещено**
**Последнее обновление**: 30 июля 2026
