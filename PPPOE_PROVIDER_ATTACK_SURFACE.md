# PPPoE Provider Attack Surface Analysis

## Executive Summary
**Purpose**: Risk assessment and attack surface mapping for PPPoE ISP infrastructure
**Target Provider**: PJSC Rostelecom (AS12389)
**Scope**: Protocol, infrastructure, authentication, network, and social engineering vectors
**Risk Level**: CRITICAL (9/10)

## Attack Surface Taxonomy

### 1. Protocol-Level Attack Surface

#### 1.1 PPPoE Protocol Vulnerabilities

**PPPoE Discovery Phase (PADI/PADO)**
```
Attack Vector: Discovery Phase Manipulation
- PADI (PPPoE Active Discovery Initiation) broadcast interception
- PADO (PPPoE Active Discovery Offer) spoofing
- AC name manipulation (VNOV-BRAS2)
- MAC address spoofing (44:6A:2E:37:15:BE)
```

**Exploitation Scenarios:**
1. **Rogue AC Injection**
   - Attacker sends fake PADO responses
   - Redirects client to malicious BRAS
   - Intercept authentication credentials
   - Success Probability: Medium (local network access required)

2. **Discovery Phase DoS**
   - Flood PADI packets to BRAS
   - Exhaust connection table
   - Deny service to legitimate users
   - Success Probability: High (simple amplification)

3. **MAC Address Cloning**
   - Clone legitimate customer MAC
   - Hijack existing PPPoE session
   - Bypass authentication
   - Success Probability: Low (requires timing and network position)

**PPPoE Session Phase (PADR/PADS)**
```
Attack Vector: Session Establishment Manipulation
- PADR (PPPoE Active Discovery Request) interception
- PADS (PPPoE Active Discovery Session) spoofing
- Session ID prediction/manipulation
- MTU/MRU negotiation attacks
```

**Exploitation Scenarios:**
1. **Session Hijacking**
   - Predict session IDs (16-bit field)
   - Send forged PADS packets
   - Take over established session
   - Success Probability: Low (requires real-time interception)

2. **MTU/MRU Manipulation**
   - Negotiate oversized MTU values
   - Cause fragmentation attacks
   - Bypass security controls
   - Success Probability: Medium

3. **Session Termination Attacks**
   - Send PADT (Terminate) packets
   - Disconnect legitimate users
   - DoS condition
   - Success Probability: High (no authentication required)

#### 1.2 PPP Authentication Vulnerabilities

**PAP (Password Authentication Protocol)**
```
Attack Vector: PAP Credential Harvesting
- Credentials transmitted in clear text
- Username: szt
- Password: szt
- Base64 encoding only (no encryption)
```

**Exploitation Scenarios:**
1. **Passive Sniffing**
   - Capture PPPoE session establishment
   - Extract PAP authentication frame
   - Decode credentials
   - Success Probability: High (PAP enabled)

2. **Replay Attacks**
   - Replay captured authentication frames
   - Authenticate as legitimate user
   - Success Probability: High (no nonce/timestamp)

3. **Credential Brute Force**
   - Offline password cracking
   - Dictionary attacks on captured hashes
   - Success Probability: Medium (weak passwords common)

**CHAP (Challenge Handshake Authentication Protocol)**
```
Attack Vector: CHAP Challenge Manipulation
- Challenge-response mechanism
- MD5 hash of challenge + password
- Susceptible to dictionary attacks
- No mutual authentication
```

**Exploitation Scenarios:**
1. **Challenge Replay**
   - Capture valid challenge-response pair
   - Replay to authenticate
   - Success Probability: Low (server tracks challenges)

2. **Offline Dictionary Attack**
   - Capture challenge and response
   - Brute force password offline
   - Success Probability: Medium (depends on password strength)

3. **Challenge Manipulation**
   - Inject custom challenges
   - Analyze response patterns
   - Success Probability: Low (requires active MITM)

**MSCHAP1/MSCHAP2 Vulnerabilities**
```
Attack Vector: Microsoft CHAP Flaws
- MSCHAP1: Uses DES with weak keys
- MSCHAP2: Known vulnerabilities (LanManager)
- Susceptible to dictionary attacks
- No server authentication in some implementations
```

**Exploitation Scenarios:**
1. **LanManager Hash Attack**
   - Extract LanManager hash from response
   - Crack using rainbow tables
   - Success Probability: High (LM hash weak)

2. **ASLEAP Attack**
   - Exploit MSCHAPv2 weakness
   - Offline password cracking
   - Success Probability: Medium-High

3. **Credential Theif Tool**
   - Use automated MSCHAP cracking tools
   - Success Probability: Medium-High

### 2. ISP Infrastructure Attack Surface

#### 2.1 BRAS (Broadband Remote Access Server) Attacks

**Target: VNOV-BRAS2**
```
Infrastructure Details:
- MAC: 44:6A:2E:37:15:BE
- IP: 100.76.128.1 (CGNAT space)
- Role: PPPoE termination
- Vendor: Unknown (likely Cisco/Juniper/ Huawei)
```

**Attack Vectors:**

1. **BRAS Vulnerability Exploitation**
   - Scan for known BRAS vulnerabilities
   - Exploit authentication bypasses
   - CVE-2021-xxxx (BRAS-specific)
   - Success Probability: Medium

2. **Configuration Extraction**
   - SNMP community attacks (public/private)
   - TFTP configuration download
   - HTTP/HTTPS management interface
   - Success Probability: Medium (default credentials common)

3. **BRAS DoS**
   - PPPoE connection flooding
   - Resource exhaustion
   - Authentication table overflow
   - Success Probability: High

4. **Memory Corruption Exploits**
   - Buffer overflow in PPPoE handling
   - Heap spraying attacks
   - Code execution on BRAS
   - Success Probability: Low (requires specific vulnerability)

#### 2.2 CGNAT (Carrier-Grade NAT) Infrastructure

**Target: CGNAT Gateway (188.254.2.98)**
```
Infrastructure Details:
- IP: 188.254.2.98
- Role: NAT translation
- Scale: Thousands of customers
- Technology: LSN (Large Scale NAT)
```

**Attack Vectors:**

1. **NAT Table Exhaustion**
   - Flood with connection attempts
   - Exhaust NAT translation table
   - Deny service to other customers
   - Success Probability: Medium-High

2. **NAT Mapping Prediction**
   - Predict port allocation algorithms
   - Hijack other customer sessions
   - Success Probability: Low (complex algorithms)

3. **NAT Log Analysis**
   - Access NAT translation logs
   - Correlate customer activity
   - Success Probability: Low (requires ISP access)

4. **CGNAT Bypass**
   - Teredo/6to4 tunneling
   - IPv6 transition mechanisms
   - Success Probability: Medium (if IPv6 available)

#### 2.3 DNS Infrastructure Attacks

**Target: DNS Servers (78.37.77.77, 212.48.197.77)**
```
Infrastructure Details:
- Primary: 78.37.77.77 (Rostelecom regional)
- Secondary: 212.48.197.77 (North-West Telecom)
- Role: Recursive DNS resolution
- Security: No DNSSEC observed
```

**Attack Vectors:**

1. **DNS Cache Poisoning**
   - Kaminsky attack (transaction ID prediction)
   - Inject malicious responses
   - Redirect traffic to malicious sites
   - Success Probability: Medium (no DNSSEC)

2. **DNS Amplification DDoS**
   - Use ISP DNS as amplifier
   - Reflect attacks to targets
   - Success Probability: High (open resolvers common)

3. **DNS Tunneling**
   - Exfiltrate data via DNS queries
   - Bypass firewall restrictions
   - Success Probability: Medium

4. **DNS Server Compromise**
   - Exploit BIND vulnerabilities
   - Take over DNS infrastructure
   - Success Probability: Low (requires specific vulnerability)

#### 2.4 Routing Infrastructure Attacks

**Target: Transit Routers (95.71.2.226, 188.254.2.98)**
```
Infrastructure Details:
- ASN: AS12389 (Rostelecom)
- Role: Transit and edge routing
- Protocol: BGP, OSPF, IS-IS
```

**Attack Vectors:**

1. **BGP Hijacking**
   - Announce more specific routes
   - Intercept traffic
   - Success Probability: Low (requires ISP access)

2. **Route Flapping**
   - Cause route instability
   - Degrade network performance
   - Success Probability: Medium (if customer edge compromised)

3. **OSPF/IS-IS Attacks**
   - Inject false routing information
   - Create routing loops
   - Success Probability: Low (requires internal access)

### 3. Authentication Attack Surface

#### 3.1 Credential Theft Vectors

**Passive Interception**
```
Methods:
- Local network sniffing (PAP)
- PPPoE session capture
- Wireless interception
- Shared network medium
```

**Active Interception**
```
Methods:
- ARP poisoning
- MAC flooding
- STP manipulation
- DHCP spoofing
```

**Success Probability: High (PAP enabled)**

#### 3.2 Authentication Bypass Methods

**Session Hijacking**
```
Techniques:
- TCP sequence prediction
- Session fixation
- Cookie theft (if web management)
- Token reuse
```

**Authentication Flaw Exploitation**
```
Techniques:
- Null authentication
- Default credentials
- Weak password policies
- Authentication bypass vulnerabilities
```

**Success Probability: Medium**

#### 3.3 Account Takeover Scenarios

**Credential Stuffing**
```
Method:
- Use leaked credentials from other breaches
- Try common username/password combinations
- Success Probability: Medium (credential reuse common)
```

**Social Engineering**
```
Method:
- Phishing for credentials
- Vishing (voice phishing)
- Impersonation of ISP support
- Success Probability: Medium (user awareness varies)
```

### 4. Network-Level Attack Scenarios

#### 4.1 Man-in-the-Middle Attacks

**Local Network MITM**
```
Attack Chain:
1. ARP poison victim and gateway
2. Intercept PPPoE discovery
3. Redirect to rogue AC
4. Capture authentication
5. Relay to legitimate BRAS
```

**Success Probability: Medium (requires local access)**

**ISP-Level MITM**
```
Attack Chain:
1. Compromise BRAS or transit router
2. Modify routing tables
3. Intercept all traffic
4. Perform SSL stripping
5. Inject malicious content
```

**Success Probability: Low (requires ISP infrastructure access)**

#### 4.2 Denial of Service Attacks

**PPPoE-Specific DoS**
```
Methods:
- PADI/PADO flooding
- Session table exhaustion
- Authentication flooding
- PADT termination attacks
```

**Network Infrastructure DoS**
```
Methods:
- Bandwidth saturation
- Resource exhaustion
- Protocol abuse
- Amplification attacks
```

**Success Probability: High**

#### 4.3 Data Exfiltration Vectors

**DNS Tunneling**
```
Implementation:
- Encode data in subdomains
- Use ISP DNS as exfiltration channel
- Bypass firewall restrictions
- Success Probability: Medium
```

**Protocol Tunneling**
```
Implementation:
- ICMP tunneling
- HTTP covert channels
- TCP header manipulation
- Success Probability: Medium
```

### 5. Social Engineering Attack Surface

#### 5.1 Impersonation Attacks

**ISP Support Impersonation**
```
Scenarios:
- "We need to verify your connection"
- "Your account will be suspended"
- "Upgrade your modem firmware"
- "Security breach detected"
```

**Success Probability: Medium**

**Technical Support Scams**
```
Scenarios:
- Fake technician visits
- Malicious equipment installation
- Configuration changes
- Success Probability: Low (physical access required)
```

#### 5.2 Phishing Vectors

**Credential Harvesting**
```
Methods:
- Fake ISP portal
- Email with configuration links
- SMS with malicious URLs
- Success Probability: Medium
```

**Malware Distribution**
```
Methods:
- Fake modem firmware updates
- ISP-branded software
- Configuration utilities
- Success Probability: Medium
```

### 6. Attack Tree Methodology

#### 6.1 Primary Goal: Compromise Customer Connection

```
ROOT: Compromise Customer PPPoE Connection
├── A1: Intercept Authentication
│   ├── A1.1: Passive Sniffing (PAP)
│   ├── A1.2: Active MITM
│   ├── A1.3: Rogue AC Injection
│   └── A1.4: BRAS Compromise
├── A2: Session Hijacking
│   ├── A2.1: TCP Sequence Prediction
│   ├── A2.2: Session ID Prediction
│   └── A2.3: MAC Address Cloning
├── A3: Authentication Bypass
│   ├── A3.1: Credential Stuffing
│   ├── A3.2: Default Credentials
│   └── A3.3: Vulnerability Exploitation
└── A4: Denial of Service
    ├── A4.1: PPPoE Flooding
    ├── A4.2: NAT Table Exhaustion
    └── A4.3: BRAS Resource Exhaustion
```

#### 6.2 Primary Goal: Compromise ISP Infrastructure

```
ROOT: Compromise ISP Infrastructure
├── B1: BRAS Compromise
│   ├── B1.1: Vulnerability Exploitation
│   ├── B1.2: Default Credentials
│   ├── B1.3: Configuration Extraction
│   └── B1.4: Memory Corruption
├── B2: DNS Infrastructure
│   ├── B2.1: Cache Poisoning
│   ├── B2.2: Server Compromise
│   └── B2.3: Zone Transfer
├── B3: Routing Infrastructure
│   ├── B3.1: BGP Hijacking
│   ├── B3.2: Route Manipulation
│   └── B3.3: Protocol Exploitation
└── B4: Management Systems
    ├── B4.1: SNMP Attacks
    ├── B4.2: Web Interface Compromise
    └── B4.3: Database Breach
```

#### 6.3 Primary Goal: Data Exfiltration

```
ROOT: Exfiltrate Data Through ISP
├── C1: DNS Tunneling
│   ├── C1.1: Subdomain Encoding
│   ├── C1.2: TXT Record Exfiltration
│   └── C1.3: CNAME Chaining
├── C2: Protocol Tunneling
│   ├── C2.1: ICMP Tunneling
│   ├── C2.2: HTTP Covert Channels
│   └── C2.3: TCP Header Manipulation
└── C3: Legitimate Channel Abuse
    ├── C3.1: Cloud Storage
    ├── C3.2: Email Attachments
    └── C3.3: Web Uploads
```

### 7. Risk Assessment Matrix

| Attack Vector | Likelihood | Impact | Risk Score | Mitigation Difficulty |
|--------------|-----------|--------|------------|---------------------|
| PAP Sniffing | High | High | 9/10 | Easy |
| PPPoE DoS | High | Medium | 7/10 | Medium |
| DNS Poisoning | Medium | High | 7/10 | Medium |
| BRAS Compromise | Low | Critical | 8/10 | Hard |
| Session Hijacking | Low | High | 6/10 | Hard |
| NAT Exhaustion | Medium | Medium | 6/10 | Medium |
| Social Engineering | Medium | Medium | 6/10 | Medium |
| BGP Hijacking | Low | Critical | 7/10 | Very Hard |

### 8. Mitigation Strategies

#### 8.1 Protocol-Level Mitigations

**Disable PAP Authentication**
```
Implementation:
/interface pppoe-client set pppoe-out1 allow=mschap2
```

**Implement PPPoE Security**
```
Measures:
- Enable PPPoE encryption
- Use strong authentication only
- Implement session timeout
- Rate limit discovery packets
```

#### 8.2 Infrastructure Hardening

**BRAS Security**
```
Measures:
- Regular firmware updates
- Disable unused services
- Implement access controls
- Monitor for anomalies
```

**DNS Security**
```
Measures:
- Implement DNSSEC
- Use DNS over HTTPS/TLS
- Rate limit queries
- Monitor for cache poisoning
```

**Network Security**
```
Measures:
- Implement BGP security (RPKI)
- Use routing filters
- Monitor for route leaks
- Implement DDoS protection
```

#### 8.3 Customer-Side Protections

**Encryption**
```
Measures:
- Use VPN for all traffic
- Implement encrypted DNS
- Enable HTTPS everywhere
- Use certificate pinning
```

**Network Segmentation**
```
Measures:
- Separate guest networks
- Implement VLANs
- Use firewall rules
- Monitor internal traffic
```

**Authentication Security**
```
Measures:
- Use strong passwords
- Enable multi-factor authentication
- Regular credential rotation
- Monitor for suspicious activity
```

### 9. Monitoring and Detection

#### 9.1 Indicators of Compromise

**PPPoE-Specific IOCs**
```
- Multiple PADI from same MAC
- Unusual PADT patterns
- Authentication failures
- Session ID anomalies
```

**Network-Level IOCs**
```
- ARP spoofing alerts
- MAC flooding
- Unusual routing changes
- DNS query patterns
```

#### 9.2 Detection Mechanisms

**Passive Monitoring**
```
- Network traffic analysis
- PPPoE session logging
- Authentication attempt monitoring
- DNS query logging
```

**Active Monitoring**
```
- Vulnerability scanning
- Configuration auditing
- Penetration testing
- Red team exercises
```

### 10. Incident Response

#### 10.1 Response Procedures

**Authentication Compromise**
```
1. Immediate credential rotation
2. Disable compromised accounts
3. Investigate source of compromise
4. Implement additional controls
```

**Infrastructure Compromise**
```
1. Isolate affected systems
2. Preserve forensic evidence
3. Restore from backups
4. Patch vulnerabilities
5. Monitor for recurrence
```

**Denial of Service**
```
1. Implement rate limiting
2. Blacklist attacking sources
3. Scale infrastructure
4. Engage upstream providers
```

### 11. Compliance and Legal Considerations

#### 11.1 Russian Regulatory Context

**SORM System**
```
Implications:
- Mandatory surveillance capability
- Government access to traffic
- Data retention requirements
- ISP cooperation mandatory
```

**Yarovaya Law**
```
Requirements:
- 6 months to 3 years data retention
- Metadata storage
- Content storage for certain services
- Encryption key disclosure
```

#### 11.2 Legal Attack Vectors

**Lawful Intercept**
```
Capabilities:
- Real-time monitoring
- Historical data access
- Metadata analysis
- Content interception
```

**Covert Access**
```
Risks:
- Undisclosed surveillance
- Equipment implantation
- Network infrastructure modification
- Backdoor implementation
```

### 12. Conclusion

#### 12.1 Overall Risk Assessment

**Critical Risk Areas:**
1. PAP authentication (clear text credentials)
2. ISP infrastructure visibility
3. DNS security (no DNSSEC)
4. Legal surveillance capabilities
5. CGNAT limitations

**Attack Surface Summary:**
- **Protocol Level**: 12 attack vectors
- **Infrastructure Level**: 16 attack vectors
- **Authentication Level**: 9 attack vectors
- **Network Level**: 8 attack vectors
- **Social Engineering**: 6 attack vectors
- **Total**: 51 identified attack vectors

#### 12.2 Priority Recommendations

**Immediate (Within 24 Hours):**
1. Disable PAP authentication
2. Implement encrypted DNS
3. Enable VPN for sensitive traffic

**Short-term (Within 1 Week):**
1. Audit all PPPoE configurations
2. Implement network monitoring
3. Update router firmware

**Long-term (Within 1 Month):**
1. Implement IPv6
2. Request public IP assignment
3. Evaluate alternative ISPs

#### 12.3 Residual Risk

**After Mitigations:**
- **Protocol Risk**: Reduced from 9/10 to 4/10
- **Infrastructure Risk**: Remains 7/10 (ISP-controlled)
- **Authentication Risk**: Reduced from 8/10 to 3/10
- **Legal Risk**: Remains 9/10 (jurisdiction-dependent)

**Overall Residual Risk**: 6/10 (MEDIUM)

---
**Document Classification**: Internal Security Assessment
**Last Updated**: July 29, 2026
**Next Review**: August 29, 2026
