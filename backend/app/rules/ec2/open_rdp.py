from typing import Any

from app.rules.base import BaseRule, RuleResult


class EC2OpenRDPRule(BaseRule):
    rule_id = "EC2_OPEN_RDP_PORT_3389"
    name = "Security Group Allows Unrestricted Inbound RDP (Port 3389)"
    category = "EC2"
    severity = "CRITICAL"
    description = "Security Group has an inbound rule allowing port 3389 (RDP) open to the entire internet (0.0.0.0/0 or ::/0)."
    remediation = "Restrict RDP port 3389 access to private corporate IP subnets or route over AWS Client VPN."

    def evaluate(self, resource: dict[str, Any]) -> list[RuleResult]:
        group_id = resource.get("GroupId", "unknown")
        group_name = resource.get("GroupName", "unknown")
        ip_permissions = resource.get("IpPermissions", [])

        for perm in ip_permissions:
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            ip_protocol = perm.get("IpProtocol")

            port_matches = False
            if ip_protocol == "-1" or (from_port is not None and to_port is not None and from_port <= 3389 <= to_port):
                port_matches = True

            if port_matches:
                for ip_range in perm.get("IpRanges", []):
                    if ip_range.get("CidrIp") == "0.0.0.0/0":
                        return [
                            RuleResult(
                                passed=False,
                                rule_id=self.rule_id,
                                resource_id=f"arn:aws:ec2:::security-group/{group_id}",
                                resource_type="security_group",
                                severity=self.severity,
                                title=f"Security Group '{group_name}' ({group_id}) allows public RDP",
                                description=f"Port 3389 is open to 0.0.0.0/0 in Security Group {group_id}.",
                                remediation=self.remediation,
                                raw_details={"group_id": group_id, "group_name": group_name, "cidr": "0.0.0.0/0"}
                            )
                        ]
                for ipv6_range in perm.get("Ipv6Ranges", []):
                    if ipv6_range.get("CidrIpv6") == "::/0":
                        return [
                            RuleResult(
                                passed=False,
                                rule_id=self.rule_id,
                                resource_id=f"arn:aws:ec2:::security-group/{group_id}",
                                resource_type="security_group",
                                severity=self.severity,
                                title=f"Security Group '{group_name}' ({group_id}) allows public IPv6 RDP",
                                description=f"Port 3389 is open to ::/0 in Security Group {group_id}.",
                                remediation=self.remediation,
                                raw_details={"group_id": group_id, "group_name": group_name, "cidr": "::/0"}
                            )
                        ]
        return []
