# P1-ANS-01 Evidence Index

## 1. Ticket Information

- Ticket ID: P1-ANS-01
- Phase: Phase 1
- Category: Automation / Configuration Management
- Lead: 이권욱
- Support: 이하영, 이재환
- Priority: P0
- Technical Status: Complete
- Actual Completion Date: 2026-08-28
- Next Gate: MS-G1-01 Infrastructure Ready

## 2. Managed Nodes

- k8s-control01: 10.1.93.102
- k8s-control02: 10.1.93.103
- k8s-control03: 10.1.93.104
- k8s-worker01: 10.1.93.105
- k8s-worker02: 10.1.93.107
- k8s-worker03: 10.1.93.108

## 3. Final Result

- Inventory: PASS=6
- Ansible Ping: PASS=6
- Source Preservation: PASS=6
- Source Address: 10.250.10.10
- Node Precheck: PASS=6
- Canary Apply: PASS
- Full Apply: PASS
- Full Postcheck: PASS=6
- Idempotency: changed=0 on all six nodes
- Final Check/Diff: No Drift
- Unreachable: 0
- Failed: 0

## 4. Applied Scope

- svc_ansible SSH automation
- Common operating system baseline
- Asia/Seoul timezone persistence
- chronyd enablement
- Bootstrap /etc/hosts mapping
- Swap disabled
- overlay module persistence
- br_netfilter module persistence
- Kubernetes prerequisite sysctl
- Check/Diff validation
- Canary deployment
- Full deployment
- Idempotency validation

## 5. Out of Scope Confirmation

The following items were not changed:

- VMware VM provisioning
- Fixed IP, Gateway and Route design
- Resolver cutover to P1 DNS
- kubeadm init
- kubeadm join
- Container runtime installation
- Calico installation
- Kubernetes security manifests
- Application deployment

## 6. Gate Evidence

- 01_network_precheck.txt
- 03_inventory_validation.txt
- 04b_ansible_ping_success.txt
- 05a_precheck_syntax.txt
- 05b_node_precheck.txt
- 05c_source_preservation.txt
- 06a_site_syntax.txt
- 06b6_check_diff_control01.txt
- 06c_canary_apply.txt
- 06d_canary_postcheck.txt
- 06e_canary_idempotency.txt
- 06f_full_apply.txt
- 06g_full_postcheck.txt
- 06h_full_idempotency.txt
- 07_final_ansible_ping.txt
- 08_final_check_diff_no_drift.txt
- 99_SHA256SUMS.txt

## 7. Troubleshooting Evidence

The following files document corrected implementation issues and are not
used as final PASS evidence:

- 04_ansible_ping.txt
- 06b_site_check_diff.txt
- 06b3_check_diff_readonly_command_failed.txt
- 06b4_check_diff_control01.txt

## 8. Exit Criteria

- [x] Inventory contains three Control Plane and three Worker nodes
- [x] Ansible Ping succeeds on all six nodes
- [x] Remote Source is preserved as 10.250.10.10
- [x] Linux and Kubernetes prerequisites are applied
- [x] SELinux remains Enforcing
- [x] Network baseline remains unchanged
- [x] Second execution reports changed=0
- [x] Evidence integrity manifest is available

## 9. Gate Recommendation

P1-ANS-01: DONE

MS-G1-01 Infrastructure Ready review may proceed.