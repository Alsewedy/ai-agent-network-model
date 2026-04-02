# Network Model v1 – Blocked or Unnecessary Flows

## Purpose
This document defines communication paths that should not be treated as part of the final intended security baseline.
It focuses on:
- flows that appear broader than necessary in the current build phase,
- flows that should later be blocked or tightly restricted,
- and areas where current access should not be interpreted as permanent design intent.

This document does not attempt to define final firewall syntax.
It focuses on security intent and reduction of unnecessary exposure.

---

## Flow: LAN / DATA -> APP_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** Core infrastructure should not maintain unrestricted access to application systems unless specific service dependencies require it.  
**Target State:** Only explicitly required communication should remain.

---

## Flow: LAN / DATA -> SERVICE_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** Core infrastructure should not maintain unrestricted access to identity services unless specific operational dependencies require it.  
**Target State:** Restrict to required infrastructure and identity-related communication only.

---

## Flow: LAN / DATA -> DMZ_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** Broad access from core infrastructure into the DMZ increases unnecessary trust exposure.  
**Target State:** Limit communication to explicitly required proxy-related paths only.

---

## Flow: APP_ZONE -> LAN / DATA (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP01 and APP02 do require communication into LAN / DATA, but only for specific functions such as database access, Vault access, and selected DC-related services.  
**Target State:** Restrict to asset-specific and service-specific communication only.

---

## Flow: APP_ZONE -> SERVICE_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP01 and APP02 require access to IAM-related services, but not unrestricted access to the entire SERVICE_ZONE.  
**Target State:** Restrict to only the identity and internal API communication actually required.

---

## Flow: APP_ZONE -> DMZ_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP systems should not have unrestricted access into the DMZ.  
**Target State:** Restrict to proxy-related communication to PROXY01 only.

---

## Flow: SERVICE_ZONE -> LAN / DATA (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** IAM01 requires selected access to DC01, DB01, and Vault on DB01, but broad access to the whole LAN / DATA zone is not justified.  
**Target State:** Restrict to only required identity, database, Vault, DNS, and time-related communication.

---

## Flow: SERVICE_ZONE -> APP_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** Broad reverse trust from SERVICE_ZONE into application systems is not justified unless specific communication is confirmed.  
**Target State:** Keep only explicitly required return-path or service-specific access.

---

## Flow: SERVICE_ZONE -> DMZ_ZONE (broad access)
**Current State:** Broad access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** IAM-related systems should not have unrestricted access into the DMZ.  
**Target State:** Restrict to proxy-related outbound communication to PROXY01 only.

---

## Flow: DMZ_ZONE -> any internal destination
**Current State:** Broad access currently appears to exist  
**Should Remain Broad in Final Design:** No  
**Reasoning:** The DMZ should not act as a broadly trusted source into internal zones.  
**Target State:** Only explicitly required communication from PROXY01 should remain. Any unnecessary internal reachability from DMZ should be blocked.

---

## Flow: ADMIN laptop -> any destination
**Current State:** Broad access currently exists from 192.168.60.120 to any destination  
**Should Remain Broad in Final Design:** No  
**Reasoning:** Administrative access is operationally important, but unrestricted any-to-any access should not be treated as a permanent baseline.  
**Target State:** Restrict administrative access to approved targets, management protocols, and justified operational needs only.

---

## Flow: APP01 -> entire SERVICE_ZONE
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP01 needs Keycloak and the Internal API on IAM01, but it does not need unrestricted access to all services in SERVICE_ZONE.  
**Target State:** Limit access to IAM01 and only the required authentication/API-related services.

---

## Flow: APP02 -> entire SERVICE_ZONE
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP02 needs Keycloak on IAM01 for employee authentication, but not broad access across the entire SERVICE_ZONE.  
**Target State:** Limit access to IAM01 and only the required authentication-related services.

---

## Flow: APP01 -> entire LAN / DATA
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP01 needs access to DB01 and Vault on DB01, but not unrestricted access to all systems in LAN / DATA.  
**Target State:** Limit access to DB01 and only the specific database and Vault-related services required.

---

## Flow: APP02 -> entire LAN / DATA
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** APP02 needs access to DB01, Vault on DB01, and selected DC-related services, but not unrestricted access to all systems in LAN / DATA.  
**Target State:** Limit access to DB01, DC01, and only the exact required services.

---

## Flow: IAM01 -> entire LAN / DATA
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** IAM01 requires communication with DC01, DB01, and Vault on DB01, but unrestricted access to all systems in LAN / DATA is broader than necessary.  
**Target State:** Limit access to the exact required infrastructure services only.

---

## Flow: DB01 -> broad access to DMZ_ZONE
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** DB01 may need outbound proxy-related access, but it does not need unrestricted reachability to the DMZ.  
**Target State:** Restrict to only the required proxy path to PROXY01.

---

## Flow: DC01 -> broad access to DMZ_ZONE
**Current State:** Broad zone-level access currently exists  
**Should Remain Broad in Final Design:** No  
**Reasoning:** DC01 may need outbound proxy-related access, but it does not need unrestricted reachability to the DMZ.  
**Target State:** Restrict to only the required proxy path to PROXY01.

---

## Flow: MGMT_SEGMENT undefined access model
**Current State:** No active rules currently defined  
**Should Remain Undefined in Final Design:** No  
**Reasoning:** A management network should not remain policy-undefined in a mature environment.  
**Target State:** Define explicit management-only communication paths and block unnecessary access.

---

## Flow: EMPLOYEE_SEGMENT undefined access model
**Current State:** No active rules currently defined  
**Should Remain Undefined in Final Design:** No  
**Reasoning:** Employee systems should not be left without a clear communication policy in the final design.  
**Target State:** Define exactly what internal services employee systems may access and block unnecessary direct reachability to sensitive zones.

---

## Flow: GUEST_SEGMENT undefined access model
**Current State:** No active rules currently defined  
**Should Remain Undefined in Final Design:** No  
**Reasoning:** Guest systems should remain highly restricted and isolated from sensitive internal services.  
**Target State:** Explicitly restrict guest access and avoid direct communication with trusted internal zones.

---

## Flow: WAN inbound exposure
**Current State:** No inbound pass rules currently defined  
**Should Be Added Broadly in Final Design:** No  
**Reasoning:** The absence of inbound WAN exposure is currently consistent with a safer default posture.  
**Target State:** Only add WAN-facing access if there is a clearly justified requirement and tightly scoped protection around it.

---

## Notes
- This document captures communication that should not remain broad in the final intended design.
- Many currently allowed zone-to-zone paths appear to be build-phase allowances rather than permanent policy decisions.
- The final target state should move from broad zone-based trust to asset-specific and service-specific communication only.
- This document should be read together with the required flows document, since some currently allowed paths include both valid operational communication and unnecessary excess exposure.