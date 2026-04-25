# Network – Services

<!--
  CATEGORY: Scope (descriptive) — REQUIRED

  "Services" is generic. Map to your domain:
    Network → listening ports   |   AD → directory services, GPO
    IAM → auth endpoints        |   Cloud → managed services, APIs
-->

## Purpose
Define services provided by each entity in the network domain.

---

## Entity: Firewall01

**Scope unit:** WAN

**Services:**
- Network firewalling
- Inter-zone routing
- Default gateway

**Purpose:** Central firewall and routing point for the segmented environment. Acts as the gateway for the network segments.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: DC01-CYBERAUDIT

**Scope unit:** LAN

**Services:**
- Active Directory
- Internal DNS
- Time service

**Purpose:** Internal directory foundation for the cyberaudit.local domain, internal name resolution, and time-related services for domain-connected systems.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: DB01

**Scope unit:** LAN

**Services:**
- MariaDB database services
- Vault

**Purpose:** Hosts the MariaDB layer for the SAAMS environment and Vault for secrets and certificate retrieval.

**Hosted components (if applicable):**
- saams_portal_db – Portal-side database
- audit_system_db – Internal audit-side database
- Vault – Secrets and certificate retrieval

---

## Entity: APP01

**Scope unit:** APP_ZONE

**Services:**
- Customer-facing web portal
- Nginx HTTPS front-end
- TLS termination for portal access

**Purpose:** Hosts the customer-facing portal and the local Nginx HTTPS front-end that listens on HTTPS and forwards traffic to the local portal process on the same server.

**Hosted components (if applicable):**
- Local portal process – Local application process behind Nginx

---

## Entity: APP02

**Scope unit:** APP_ZONE

**Services:**
- Internal employee audit application

**Purpose:** Hosts the internal C# employee audit application used for the internal workflow.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: IAM01

**Scope unit:** SERVICE_ZONE

**Services:**
- Keycloak IAM
- Internal API

**Purpose:** Central identity and access management platform for customer and internal authentication, and host of the internal API used for internal workflow integration.

**Hosted components (if applicable):**
- Keycloak – Identity and access management platform
- Internal API – Internal workflow integration service

---

## Entity: PROXY01

**Scope unit:** DMZ_ZONE

**Services:**
- Forward proxy
- Controlled outbound access

**Purpose:** Dedicated egress-related system for structured outbound Internet access.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: ESXi

**Scope unit:** MGMT_SEGMENT

**Services:**
- Virtualization host management

**Purpose:** Hosts the lab virtual machines and supports infrastructure management.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: Switch Management

**Scope unit:** MGMT_SEGMENT

**Services:**
- Switch administration

**Purpose:** Management interface for the Cisco switch infrastructure.

**Hosted components (if applicable):**
- None currently documented

---

## Entity: Admin laptop

**Scope unit:** ADMIN_SEGMENT

**Services:**
- Administrative access workstation

**Purpose:** Used for privileged administrative access to the environment.

**Hosted components (if applicable):**
- None currently documented