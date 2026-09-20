from typing import Any, Dict, List
from app.rules.base import BaseRule, RuleResult


class EC2OpenSSHRule(BaseRule):
    rule_id = "EC2_OPEN_SSH_PORT_22"
    name = "Security Group Allows Unrestricted Inbound SSH (Port 22)"
    category = "EC2"
    severity = "CRITICAL"
    description = "Security Group has an inbound rule allowing port 22 (SSH) open to the entire internet (0.0.0.0/0 or ::/0)."
    remediation = "Restrict SSH port 22 access to specific bastion IPs, VPN CIDR blocks, or use AWS Systems Manager (SSM) Session Manager instead."

    def evaluate(self, resource: Dict[str, Any]) -> List[RuleResult]:
        # resource is a SecurityGroup dictionary
        group_id = resource.get("GroupId", "unknown")
        group_name = resource.get("GroupName", "unknown")
        ip_permissions = resource.get("IpPermissions", [])

        for perm in ip_permissions:
            from_port = perm.get("FromPort")
            to_port = perm.get("ToPort")
            ip_protocol = perm.get("IpProtocol")

            # Check if port 22 is included in the range (or -1 for all traffic)
            port_matches = False
            if ip_protocol == "-1":
                port_matches = True
            elif from_port is not None and to_port is not None:
                if from_port <= 22 <= to_port:
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
                                title=f"Security Group '{group_name}' ({group_id}) allows public SSH",
                                description=f"Port 22 is open to 0.0.0.0/0 in Security Group {group_id}.",
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
                                title=f"Security Group '{group_name}' ({group_id}) allows public IPv6 SSH",
                                description=f"Port 22 is open to ::/0 in Security Group {group_id}.",
                                remediation=self.remediation,
                                raw_details={"group_id": group_id, "group_name": group_name, "cidr": "::/0"}
                            )
                        ]
        return []
