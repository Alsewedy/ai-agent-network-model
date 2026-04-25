# Naming Conventions

Standard naming rules applied across all domains.
Follow these when creating or referencing any entity, scope unit, or service.

---

## Entity Names
- Use the actual hostname or canonical identifier: `DC01-CYBERAUDIT`, not "the domain controller"
- Preserve case as defined in the source system
- Once an entity name is defined in `scope/`, use it identically everywhere

## Scope Unit Names
- Use the exact name from the infrastructure design: `APP_ZONE`, not "application zone"
- If the scope unit has a formal identifier (subnet, OU path), include it in the definition

## Service Names
- Use functional names: `keycloak`, `internal_api`, `mariadb`
- Avoid product versions in the name unless version-specific behavior matters

## Compound References
- When referring to a service hosted on a specific entity, use `Service on Host` format:
  `Vault on DB01`, `Internal API on IAM01`, `Kerberos on DC01`
- This distinguishes "I depend on the service" from "I depend on the entire host"

## Flow Directions
- Always use `Source → Destination` format in headings and references
- Be explicit about direction: `outbound from APP01`, `inbound to IAM01`

## File Names
- Use lowercase with underscores: `scope_units.md`, `required_flows.md`
- Domain folder names: lowercase, underscores: `network`, `active_directory`
