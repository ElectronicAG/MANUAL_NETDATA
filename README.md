# Gestor de monitoreo de red con Netdata y MPLS Huawei

Proyecto de implementación de un sistema de monitoreo centralizado con **Netdata en una Raspberry Pi**, integrado con una red MPLS formada por equipos Huawei AR651 y S6730H.

El repositorio reúne los manuales de implementación, las evidencias gráficas, una topología de eNSP y un proyecto Python para la configuración de equipos por consola serie. El laboratorio aborda conectividad IP con OSPF, LSP estáticos, distribución dinámica de etiquetas con LDP y supervisión mediante SNMPv3.

## Objetivos

- Desplegar Netdata en una Raspberry Pi y comprobar la recolección de métricas.
- Integrar los dispositivos Huawei al monitoreo mediante SNMPv3.
- Configurar y verificar una red MPLS sobre una base de enrutamiento OSPF.
- Comparar LSP estáticos y dinámicos, incluyendo los modos de anuncio DU y DoD.
- Generar tráfico TCP y UDP con iPerf3 y observar su comportamiento en Netdata.
- Organizar la visualización mediante dashboards, alertas y topologías de red.

## Fases del proyecto

| Fase | Alcance | Documentación |
| --- | --- | --- |
| **Fase 1: implementación del gestor** | Preparación de la Raspberry Pi, instalación de Ubuntu Server y Netdata, pruebas de puesta en marcha e integración con Netdata Cloud. Incluye usuarios, roles, Rooms y dashboards. | [Manual de implementación](Fase_1/main.pdf) |
| **Fase 2: monitoreo y gestión de MPLS** | Integración SNMPv3, configuración OSPF y MPLS, transición de LSP estáticos a LDP, pruebas iPerf3, dashboards, alertas y monitoreo de adyacencias y sesiones. | [Guía de monitoreo y gestión de la red](Fase_2/main.pdf) |

## Contenido del repositorio

| Ruta | Contenido |
| --- | --- |
| [`eNSP/Topologia/`](eNSP/Topologia/) | Proyecto de simulación: `Topologia.topo` y los directorios de dispositivos con sus archivos `flash.efz`. |
| [`Fase_1/`](Fase_1/) | Informe de la primera fase y evidencias en `Pictures/`. Incluye fragmentos de documentación en formato `.tex`. |
| [`Fase_2/`](Fase_2/) | Informe de la segunda fase y capturas de configuración, monitoreo y pruebas de tráfico. |
| [`huawei_serial/`](huawei_serial/) | Proyecto Python para trabajar con la consola serie de los equipos. Consultar su [README específico](huawei_serial/README.md). |
| [`huawei_serial/configs/`](huawei_serial/configs/) | Configuraciones y comandos de verificación organizados por equipo y etapa. |
| [`huawei_serial/src/code_python/`](huawei_serial/src/code_python/) | Código fuente de la herramienta, incluido `serial_config.py` y el punto de entrada `__main__.py`. |
| [`huawei_serial/tests/`](huawei_serial/tests/) | Pruebas de la herramienta serie en `test_serial_config.py`. |
| [`huawei_serial/referencia/`](huawei_serial/referencia/) | Guion de referencia `MPLS_Lab_Huawei_Script_Completo.txt`. |

El proyecto Python incluye `pyproject.toml` y `uv.lock` para definir el paquete y sus dependencias. Los parámetros de ejecución y de conexión serie se consultan en su documentación interna.

## Entorno del laboratorio

| Componente | Configuración documentada |
| --- | --- |
| Servidor de monitoreo | Raspberry Pi 5 con 8 GB de RAM y SSD externo de 120 GB. |
| Sistema operativo | Ubuntu Server de 64 bits para ARM64. |
| Plataforma de monitoreo | Netdata Agent y Netdata Cloud para la administración compartida. |
| Equipos de borde | Dos routers Huawei AR651: `AR651-A` y `AR651-B`. |
| Equipos de tránsito | Dos switches Huawei S6730H: `S6730H-C` y `S6730H-D`. |
| Estaciones de prueba | Dos computadoras con iPerf3, conectadas a los extremos de la red. |
| Herramientas de apoyo | Cliente SSH, herramientas SNMP, consola serie y eNSP para abrir la topología de simulación. |

La instalación del gestor requiere acceso administrativo al sistema e Internet para descargar los paquetes. Los requisitos de Python y las dependencias de la herramienta serie se definen en [`huawei_serial/pyproject.toml`](huawei_serial/pyproject.toml).

## Topología y direccionamiento

El núcleo tiene tres enlaces consecutivos: **AR651-A con S6730H-C**, **S6730H-C con S6730H-D** y **S6730H-D con AR651-B**. Los routers actúan como equipos de borde y los switches como equipos de tránsito MPLS.

### Loopbacks

| Equipo | Loopback0 | Función |
| --- | --- | --- |
| AR651-A | `1.1.1.1/32` | Borde de la red MPLS. |
| S6730H-C | `2.2.2.2/32` | Tránsito MPLS. |
| S6730H-D | `3.3.3.3/32` | Tránsito MPLS. |
| AR651-B | `4.4.4.4/32` | Borde de la red MPLS. |

### Enlaces del núcleo

| Enlace | Subred | Direcciones de los extremos |
| --- | --- | --- |
| AR651-A / S6730H-C | `10.0.12.0/30` | A: `10.0.12.1`; C: `10.0.12.2`. |
| S6730H-C / S6730H-D | `10.0.23.0/30` | C: `10.0.23.1`; D: `10.0.23.2`. |
| S6730H-D / AR651-B | `10.0.34.0/30` | D: `10.0.34.1`; B: `10.0.34.2`. |

### Monitoreo y estaciones de prueba

| Elemento | Dirección | Acceso o puerta de enlace |
| --- | --- | --- |
| Raspberry Pi, interfaz de monitoreo | `192.168.10.1/24` | Rutas hacia las loopbacks mediante `192.168.10.2`. |
| AR651-A, interfaz hacia el gestor | `192.168.10.2/24` | Red de monitoreo anunciada en OSPF. |
| Computadora cliente iPerf3 | `10.10.10.1/30` | `10.10.10.2`, interfaz de acceso de AR651-A. |
| Computadora servidora iPerf3 | `20.20.20.1/30` | `20.20.20.2`, interfaz de acceso de AR651-B. |

Las direcciones corresponden al montaje descrito en la Fase 2. Comprobar los nombres reales de las interfaces antes de aplicar las configuraciones, especialmente al adaptar el laboratorio a eNSP u otros equipos.

## Puesta en marcha

1. **Preparar el gestor.** Seguir el [manual de la Fase 1](Fase_1/main.pdf) para instalar el sistema operativo, habilitar el acceso remoto y desplegar Netdata.
2. **Verificar Netdata.** Comprobar el servicio, la interfaz web y la disponibilidad de métricas. El panel local se consulta en `http://IP_DE_LA_RASPBERRY:19999`.
3. **Preparar la red Huawei.** Identificar las interfaces y aplicar la configuración base de cada equipo. Verificar OSPF y la conectividad entre loopbacks antes de continuar con MPLS.
4. **Configurar MPLS por etapas.** Construir el LSP estático, comprobarlo y realizar la transición a LDP según la [guía de la Fase 2](Fase_2/main.pdf).
5. **Integrar el monitoreo.** Configurar SNMPv3 en los equipos y los trabajos de recolección en `/etc/netdata/go.d/snmp.conf`. Asegurar conectividad de ida y vuelta entre la Raspberry Pi y los dispositivos.
6. **Habilitar las redes de prueba.** Configurar las estaciones, anunciar sus subredes y verificar que existan LSP para las redes de acceso.
7. **Ejecutar las pruebas.** Generar tráfico con iPerf3 y revisar interfaces, caudal, estados OSPF/LDP y alertas en Netdata.

Para utilizar la consola serie, seguir las instrucciones de [`huawei_serial/README.md`](huawei_serial/README.md) y seleccionar los archivos correspondientes al equipo conectado.

### Orden de las configuraciones

Los archivos se encuentran en `huawei_serial/configs/<EQUIPO>/`, donde `<EQUIPO>` es `AR651-A`, `AR651-B`, `S6730H-C` o `S6730H-D`.

| Orden | Archivo | Propósito |
| --- | --- | --- |
| 1 | `01_base_ospf.cfg` | Configuración base y enrutamiento OSPF. |
| 2 | `01_verificar_ospf.cfg` | Verificación de vecinos, rutas y conectividad IP. |
| 3 | `02_lsp_estatico.cfg` | Configuración del LSP estático. |
| 4 | `02_verificar_lsp.cfg` | Verificación de MPLS y del LSP estático. |
| 5 | `03_cambiar_a_ldp.cfg` | Transición del escenario estático a LDP. |
| 6 | `03_verificar_ldp.cfg` | Verificación de vecinos, sesiones y LSP dinámicos. |
| 7, opcional | `04_dod_opcional.cfg` | Prueba del modo Downstream on Demand, disponible en C y D. |
| 8 | `05_restaurar_du.cfg` | Restauración de Downstream Unsolicited después de la prueba, disponible en C y D. |

Revisar cada archivo antes de aplicarlo y completar la misma etapa en los equipos implicados antes de avanzar. Las configuraciones SNMP, los perfiles de Netdata y las redes de acceso se desarrollan en el informe de la Fase 2; consultar ese manual para completar el montaje.

## Verificación

### Gestor de monitoreo

Ejecutar en la Raspberry Pi:

```bash
sudo systemctl is-enabled netdata
sudo systemctl is-active netdata
curl -fsS http://127.0.0.1:19999/api/v1/info
sudo journalctl -u netdata -b --priority=err --no-pager
```

El servicio debe estar habilitado y activo, la API debe responder con información del nodo y el registro debe permitir descartar errores que impidan la recolección.

### OSPF y MPLS

Ejecutar en la consola de los equipos Huawei, según la etapa:

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

En la etapa dinámica, las adyacencias OSPF deben estar en **Full** y las sesiones LDP en **Operational**. Para las pruebas entre computadoras, verificar también las FEC `10.10.10.0/30` y `20.20.20.0/30`, con etiquetas de salida en los equipos de ingreso correspondientes.

### Tráfico con iPerf3

En la computadora servidora, con dirección `20.20.20.1`:

```bash
iperf3 -s
```

En la computadora cliente, con dirección `10.10.10.1`:

```bash
# TCP durante 120 segundos
iperf3 -c 20.20.20.1 -t 120 -i 1

# TCP en sentido inverso
iperf3 -c 20.20.20.1 -t 120 -i 1 -R

# UDP a 500 Mbit/s durante 120 segundos
iperf3 -c 20.20.20.1 -u -b 500M -t 120 -i 1
```

Permitir las conexiones necesarias en el firewall de las estaciones. En UDP, registrar el caudal recibido, el jitter y la pérdida de datagramas; en Netdata, comprobar que las interfaces del recorrido reflejen el tráfico generado.

## Consideraciones del laboratorio

- **Conectividad y etiquetado:** comprobar las FEC de las redes de acceso; una respuesta a ping y una sesión LDP activa, por sí solas, no demuestran que el tráfico de las computadoras viaje etiquetado.
- **Pruebas de falla:** la topología es lineal y carece de una ruta alternativa. Restaurar los enlaces intervenidos antes de continuar con las verificaciones.
- **Monitoreo de OSPF:** el informe documenta la vinculación del proceso mediante `ospf mib-binding 1` para exponer sus estados por SNMP en los equipos utilizados.
- **Credenciales:** configurar SNMPv3 con autenticación, cifrado y acceso de lectura. Sustituir las credenciales de ejemplo de los manuales y mantener los tokens fuera del repositorio.
- **Topología personalizada:** la Fase 2 describe una aplicación web adicional en el puerto `8080`. Sus archivos se documentan en el PDF y no aparecen en la estructura de este repositorio; su despliegue se realiza por separado siguiendo esa guía.

## Autores

| Integrante | Carné |
| --- | --- |
| Alan Samuel Gomez Paz | 22115 |
| Samuel David Tórtola Bardales | 22094 |
| Luis Alejandro Luna Hernández | 22017 |
