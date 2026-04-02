# Network Model v1 – Services

## Purpose
This document defines the main services provided by each major asset in the homelab environment.
At this stage, it focuses only on service identity and purpose, without documenting detailed communication flows or firewall requirements.

---

## Asset: Firewall01
**Zone:** WAN / internal segmentation boundary
**Primary Services:**
- Network firewalling
- Inter-zone routing
- Default gateway
**Purpose:** Central firewall and routing point for the segmented environment.

---

## Asset: DC01-CYBERAUDIT
**Zone:** LAN / DATA
**Primary Services:**
- Active Directory
- Internal DNS
**Purpose:** Internal directory foundation for the cyberaudit.local domain and internal name resolution.

---

## Asset: DB01
**Zone:** LAN / DATA
**Primary Services:**
- MariaDB database services
- Vault
**Purpose:** Hosts the MariaDB layer for the SAAMS environment, including logically separated portal-side and internal audit-side databases, and also hosts Vault for secrets and certificate retrieval.

---

## Asset: APP01
**Zone:** APP_ZONE
**Primary Services:**
- Customer-facing web portal
- Nginx reverse proxy
- TLS termination for portal access
**Purpose:** Hosts the customer-facing portal and the Nginx reverse proxy layer that listens on HTTPS and forwards traffic to the local portal process on APP01.

---

## Asset: APP02
**Zone:** APP_ZONE
**Primary Services:**
- Internal employee audit application
**Purpose:** Hosts the internal C# employee audit application used for the internal workflow.

---

## Asset: IAM01
**Zone:** SERVICE_ZONE
**Primary Services:**
- Keycloak IAM
- Internal API
**Purpose:** Central identity and access management platform for customer and internal authentication, and host of the internal API used by the portal for internal workflow integration.

---

## Asset: PROXY01
**Zone:** DMZ_ZONE
**Primary Services:**
- Forward proxy
- Controlled outbound access
**Purpose:** Dedicated egress-related system for structured outbound Internet access.

---

## Asset: ESXi
**Zone:** MGMT
**Primary Services:**
- Virtualization host management
**Purpose:** Hosts the lab virtual machines and supports infrastructure management.

---

## Asset: Switch Management
**Zone:** MGMT
**Primary Services:**
- Switch administration
**Purpose:** Management interface for the Cisco switch infrastructure.

---

## Asset: Admin laptop
**Zone:** ADMIN
**Primary Services:**
- Administrative access workstation
**Purpose:** Used for privileged administrative access to the environment.

---

## Notes
- This file defines services at a high level only.
- Detailed flows, dependencies, and ports will be documented separately.
- No service assumptions should be added unless they are confirmed by the homelab documentation or by the owner.