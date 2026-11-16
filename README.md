# Network Monitoring System with Netdata and Huawei MPLS

A project to implement a centralized monitoring system using **Netdata on a Raspberry Pi**, integrated with an MPLS network built with Huawei AR651 and S6730H devices.

This repository brings together implementation guides, screenshots, an eNSP topology, and a Python project for configuring devices through a serial console. The lab covers IP connectivity with OSPF, static LSPs, dynamic label distribution with LDP, and monitoring through SNMPv3.

## Objectives

- Deploy Netdata on a Raspberry Pi and verify metric collection.
- Integrate Huawei devices into the monitoring system through SNMPv3.
- Configure and verify an MPLS network over an OSPF routing infrastructure.
- Compare static and dynamic LSPs, including DU and DoD label advertisement modes.
- Generate TCP and UDP traffic with iPerf3 and observe its behavior in Netdata.
- Organize monitoring views through dashboards, alerts, and network topologies.

## Project Phases

| Phase | Scope | Documentation |
| --- | --- | --- |
| **Phase 1: Monitoring System Deployment** | Raspberry Pi preparation, Ubuntu Server and Netdata installation, initial operational checks, and Netdata Cloud integration. Includes users, roles, Rooms, and dashboards. | [Implementation Guide](Fase_1/main.pdf) |
| **Phase 2: MPLS Monitoring and Management** | SNMPv3 integration, OSPF and MPLS configuration, transition from static LSPs to LDP, iPerf3 testing, dashboards, alerts, and adjacency and session monitoring. | [Network Monitoring and Management Guide](Fase_2/main.pdf) |

## Repository Contents

| Path | Contents |
| --- | --- |
| [`eNSP/Topologia/`](eNSP/Topologia/) | Simulation project: `Topologia.topo` and device directories containing their `flash.efz` files. |
| [`Fase_1/`](Fase_1/) | Phase 1 report and screenshots in `Pictures/`. Includes documentation fragments in `.tex` format. |
| [`Fase_2/`](Fase_2/) | Phase 2 report and screenshots of configuration, monitoring, and traffic tests. |
| [`huawei_serial/`](huawei_serial/) | Python project for working with device serial consoles. See its [dedicated README](huawei_serial/README.md). |
| [`huawei_serial/configs/`](huawei_serial/configs/) | Configurations and verification commands organized by device and stage. |
| [`huawei_serial/src/code_python/`](huawei_serial/src/code_python/) | Tool source code, including `serial_config.py` and the `__main__.py` entry point. |
| [`huawei_serial/tests/`](huawei_serial/tests/) | Serial tool tests in `test_serial_config.py`. |
| [`huawei_serial/referencia/`](huawei_serial/referencia/) | Reference script: `MPLS_Lab_Huawei_Script_Completo.txt`. |

The Python project includes `pyproject.toml` and `uv.lock` to define the package and its dependencies. Refer to its internal documentation for execution and serial connection parameters.

## Lab Environment

| Component | Documented Configuration |
| --- | --- |
| Monitoring server | Raspberry Pi 5 with 8 GB of RAM and a 120 GB external SSD. |
| Operating system | 64-bit Ubuntu Server for ARM64. |
| Monitoring platform | Netdata Agent and Netdata Cloud for shared administration. |
| Edge devices | Two Huawei AR651 routers: `AR651-A` and `AR651-B`. |
| Transit devices | Two Huawei S6730H switches: `S6730H-C` and `S6730H-D`. |
| Test workstations | Two computers running iPerf3, connected at opposite ends of the network. |
| Supporting tools | SSH client, SNMP tools, serial console, and eNSP to open the simulation topology. |

Installing the monitoring system requires administrative access to the operating system and an Internet connection to download packages. Python requirements and serial tool dependencies are defined in [`huawei_serial/pyproject.toml`](huawei_serial/pyproject.toml).

## Topology and Addressing

The core consists of three consecutive links: **AR651-A to S6730H-C**, **S6730H-C to S6730H-D**, and **S6730H-D to AR651-B**. The routers act as edge devices, while the switches act as MPLS transit devices.

### Loopbacks

| Device | Loopback0 | Role |
| --- | --- | --- |
| AR651-A | `1.1.1.1/32` | MPLS network edge. |
| S6730H-C | `2.2.2.2/32` | MPLS transit. |
| S6730H-D | `3.3.3.3/32` | MPLS transit. |
| AR651-B | `4.4.4.4/32` | MPLS network edge. |

### Core Links

| Link | Subnet | Endpoint Addresses |
| --- | --- | --- |
| AR651-A / S6730H-C | `10.0.12.0/30` | A: `10.0.12.1`; C: `10.0.12.2`. |
| S6730H-C / S6730H-D | `10.0.23.0/30` | C: `10.0.23.1`; D: `10.0.23.2`. |
| S6730H-D / AR651-B | `10.0.34.0/30` | D: `10.0.34.1`; B: `10.0.34.2`. |

### Monitoring and Test Workstations

| Item | Address | Access or Gateway |
| --- | --- | --- |
| Raspberry Pi monitoring interface | `192.168.10.1/24` | Routes to the loopbacks through `192.168.10.2`. |
| AR651-A interface connected to the monitoring server | `192.168.10.2/24` | Monitoring network advertised through OSPF. |
| iPerf3 client computer | `10.10.10.1/30` | `10.10.10.2`, the AR651-A access interface. |
| iPerf3 server computer | `20.20.20.1/30` | `20.20.20.2`, the AR651-B access interface. |

These addresses correspond to the setup described in Phase 2. Check the actual interface names before applying configurations, especially when adapting the lab to eNSP or other devices.

## Getting Started

1. **Prepare the monitoring server.** Follow the [Phase 1 guide](Fase_1/main.pdf) to install the operating system, enable remote access, and deploy Netdata.
2. **Verify Netdata.** Check the service, web interface, and metric availability. Access the local dashboard at `http://RASPBERRY_PI_IP:19999`.
3. **Prepare the Huawei network.** Identify the interfaces and apply the base configuration to each device. Verify OSPF and connectivity between loopbacks before proceeding with MPLS.
4. **Configure MPLS in stages.** Set up and verify the static LSP, then transition to LDP as described in the [Phase 2 guide](Fase_2/main.pdf).
5. **Integrate monitoring.** Configure SNMPv3 on the devices and collection jobs in `/etc/netdata/go.d/snmp.conf`. Ensure bidirectional connectivity between the Raspberry Pi and the devices.
6. **Enable the test networks.** Configure the workstations, advertise their subnets, and verify that LSPs exist for the access networks.
7. **Run the tests.** Generate traffic with iPerf3 and review interfaces, throughput, OSPF/LDP states, and alerts in Netdata.

To use the serial console, follow the instructions in [`huawei_serial/README.md`](huawei_serial/README.md) and select the files for the connected device.

### Configuration Order

Files are located in `huawei_serial/configs/<DEVICE>/`, where `<DEVICE>` is `AR651-A`, `AR651-B`, `S6730H-C`, or `S6730H-D`.

| Order | File | Purpose |
| --- | --- | --- |
| 1 | `01_base_ospf.cfg` | Base configuration and OSPF routing. |
| 2 | `01_verificar_ospf.cfg` | Neighbor, route, and IP connectivity verification. |
| 3 | `02_lsp_estatico.cfg` | Static LSP configuration. |
| 4 | `02_verificar_lsp.cfg` | MPLS and static LSP verification. |
| 5 | `03_cambiar_a_ldp.cfg` | Transition from the static scenario to LDP. |
| 6 | `03_verificar_ldp.cfg` | Neighbor, session, and dynamic LSP verification. |
| 7, optional | `04_dod_opcional.cfg` | Downstream on Demand mode test, available on C and D. |
| 8 | `05_restaurar_du.cfg` | Restore Downstream Unsolicited after the test, available on C and D. |

Review each file before applying it, and complete the same stage on all involved devices before proceeding. SNMP configurations, Netdata profiles, and access networks are covered in the Phase 2 report; consult that guide to complete the setup.

## Verification

### Monitoring Server

Run the following commands on the Raspberry Pi:

```bash
sudo systemctl is-enabled netdata
sudo systemctl is-active netdata
curl -fsS http://127.0.0.1:19999/api/v1/info
sudo journalctl -u netdata -b --priority=err --no-pager
```

The service should be enabled and active, the API should return node information, and the log should be checked for errors that could prevent metric collection.

### OSPF and MPLS

Run the following commands in the Huawei device console, as appropriate for the current stage:

```text
display ospf peer brief
display ip routing-table protocol ospf
display mpls interface
display mpls static-lsp
display mpls ldp peer
display mpls ldp session
display mpls ldp lsp
display mpls lsp
```

In the dynamic stage, OSPF adjacencies should be **Full** and LDP sessions should be **Operational**. For tests between computers, also verify the `10.10.10.0/30` and `20.20.20.0/30` FECs, including outgoing labels on the corresponding ingress devices.

### iPerf3 Traffic

On the server computer at `20.20.20.1`:

```bash
iperf3 -s
```

On the client computer at `10.10.10.1`:

```bash
# TCP for 120 seconds
iperf3 -c 20.20.20.1 -t 120 -i 1

# TCP in the reverse direction
iperf3 -c 20.20.20.1 -t 120 -i 1 -R

# UDP at 500 Mbit/s for 120 seconds
iperf3 -c 20.20.20.1 -u -b 500M -t 120 -i 1
```

Allow the required connections through the workstation firewalls. For UDP, record the received throughput, jitter, and datagram loss; in Netdata, verify that interfaces along the path reflect the generated traffic.

## Lab Considerations

- **Connectivity and labeling:** verify the FECs for the access networks; a ping response and an active LDP session alone do not prove that traffic between the computers is being label-switched.
- **Failure testing:** the topology is linear and has no alternate path. Restore any links affected by testing before continuing with verification.
- **OSPF monitoring:** the report documents the use of `ospf mib-binding 1` to bind the OSPF process to the MIB and expose its states through SNMP on the devices used.
- **Credentials:** configure SNMPv3 with authentication, encryption, and read-only access. Replace the example credentials in the guides and keep tokens out of the repository.
- **Custom topology:** Phase 2 describes an additional web application on port `8080`. Its files are documented in the PDF and are not included in this repository's structure; deploy it separately by following that guide.

## Authors

| Team Member | Student ID |
| --- | --- |
| Alan Samuel Gomez Paz | 22115 |
| Samuel David Tórtola Bardales | 22094 |
| Luis Alejandro Luna Hernández | 22017 |
