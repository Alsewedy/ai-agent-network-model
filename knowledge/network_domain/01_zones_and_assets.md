# Network Model v1 – Zones and Assets

## Purpose
This document defines the first layer of the network model for the homelab environment.
It focuses only on security zones and the main assets located inside each zone.
At this stage, the document does not include detailed service flows, firewall rules, or port-level communication.

---

## Zone: WAN
**Purpose:** External connectivity through pfSense.
**Assets:**
- Firewall01 (WAN interface)

---

## Zone: LAN / DATA
**Subnet:** 192.168.128.0/24
**Gateway:** 192.168.128.1
**Purpose:** Core internal infrastructure.
**Assets:**
- DC01-CYBERAUDIT
- DB01

---

## Zone: APP_ZONE
**Subnet:** 192.168.20.0/24
**Gateway:** 192.168.20.1
**Purpose:** Main application servers.
**Assets:**
- APP01
- APP02

---

## Zone: DMZ_ZONE
**Subnet:** 192.168.10.0/24
**Gateway:** 192.168.10.1
**Purpose:** Proxy services and controlled outbound access.
**Assets:**
- PROXY01

---

## Zone: SERVICE_ZONE
**Subnet:** 192.168.30.0/24
**Gateway:** 192.168.30.1
**Purpose:** Identity and access management services.
**Assets:**
- IAM01

---

## Zone: MGMT
**Subnet:** 192.168.50.0/24
**Gateway:** 192.168.50.1
**Purpose:** Infrastructure management network.
**Assets:**
- ESXi
- Switch Management

---

## Zone: ADMIN
**Subnet:** 192.168.60.0/24
**Gateway:** 192.168.60.1
**Purpose:** Administrative workstations and privileged access devices.
**Assets:**
- Admin laptop

---

## Zone: EMPLOYEE
**Subnet:** 192.168.70.0/24
**Gateway:** 192.168.70.1
**Purpose:** Internal employee devices and normal workstation-style systems.
**Assets:**
- Employee devices

---

## Zone: GUEST
**Subnet:** 192.168.80.0/24
**Gateway:** 192.168.80.1
**Purpose:** Guest or untrusted access.
**Assets:**
- Guest devices

---

## Notes
- This document represents the first layer of the network model only.
- Flows, services, and security policy logic will be documented separately in later files.
- The structure is based on the current segmented homelab design.