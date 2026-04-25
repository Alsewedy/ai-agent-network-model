# Network – Scope Units

<!--
  CATEGORY: Scope (descriptive) — REQUIRED

  "Scope units" is generic. Map to your domain:
    Network → zones   |   AD → OUs, forests, sites
    Cloud → VPCs, accounts   |   IAM → realms, tenants
-->

## Purpose
Define the organizational structure and entities of the network domain.

---

## Scope Unit: WAN

**Identifier:** N/A  
**Purpose:** External connectivity through pfSense.

**Entities:**
- Firewall01

**Shared entities:** None currently documented

---

## Scope Unit: LAN

**Identifier:** Subnet: 192.168.128.0/24 | Gateway: 192.168.128.1  
**Purpose:** Core internal infrastructure.

**Entities:**
- DC01-CYBERAUDIT
- DB01

**Shared entities:** None currently documented

---

## Scope Unit: APP_ZONE

**Identifier:** Subnet: 192.168.20.0/24 | Gateway: 192.168.20.1  
**Purpose:** Main application servers.

**Entities:**
- APP01
- APP02

**Shared entities:** None currently documented

---

## Scope Unit: DMZ_ZONE

**Identifier:** Subnet: 192.168.10.0/24 | Gateway: 192.168.10.1  
**Purpose:** Proxy services and controlled outbound access.

**Entities:**
- PROXY01

**Shared entities:** None currently documented

---

## Scope Unit: SERVICE_ZONE

**Identifier:** Subnet: 192.168.30.0/24 | Gateway: 192.168.30.1  
**Purpose:** Identity and access management services.

**Entities:**
- IAM01

**Shared entities:** None currently documented

---

## Scope Unit: MGMT_SEGMENT

**Identifier:** Subnet: 192.168.50.0/24 | Gateway: 192.168.50.1  
**Purpose:** Infrastructure management network.

**Entities:**
- ESXi
- Switch Management

**Shared entities:** None currently documented

---

## Scope Unit: ADMIN_SEGMENT

**Identifier:** Subnet: 192.168.60.0/24 | Gateway: 192.168.60.1  
**Purpose:** Administrative workstations and privileged access devices.

**Entities:**
- Admin laptop

**Shared entities:** None currently documented

---

## Scope Unit: EMPLOYEE_SEGMENT

**Identifier:** Subnet: 192.168.70.0/24 | Gateway: 192.168.70.1  
**Purpose:** Internal employee network segment for normal workstation-style systems.

**Entities:**
- None currently documented

**Shared entities:** None currently documented

---

## Scope Unit: GUEST_SEGMENT

**Identifier:** Subnet: 192.168.80.0/24 | Gateway: 192.168.80.1  
**Purpose:** Guest or untrusted access network segment.

**Entities:**
- None currently documented

**Shared entities:** None currently documented