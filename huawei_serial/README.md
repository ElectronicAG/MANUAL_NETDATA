# Configuración de Huawei por consola serial

Selecciona un `.cfg`, conecta tu laptop al puerto de consola y envía los comandos al equipo conectado. La salida recibida, los comandos enviados, las selecciones y los mensajes del programa se muestran en pantalla y se añaden a `outpu.txt` (nombre solicitado, sin la segunda `t`). Cada ejecución tiene fecha, inicio y fin; no borra sesiones anteriores.

## Integrarlo en tu proyecto actual

Conserva tu `pyproject.toml`, `uv.lock` y los demás archivos. Copia del ZIP:

- `src/code_python/serial_config.py` a tu carpeta `src/code_python/`.
- `configs/` a la raíz de tu proyecto.
- Opcionalmente, `src/code_python/__main__.py` si quieres la ejecución como módulo.

Tu `__init__.py` adjunto solo importa `serial` y `paramiko`. El programa serial no necesita `paramiko`; puedes dejar `__init__.py` como el del ejemplo (un docstring) si aún no tienes allí otro código. No necesitas guardar la lógica del programa en `__init__.py`.

Desde la raíz de tu proyecto:

```bash
uv add pyserial
uv run python src/code_python/serial_config.py
```

`uv add` actualizará las dependencias y el lock de tu proyecto. No copies el `pyproject.toml` del ejemplo encima del tuyo: se incluye únicamente para usar este paquete como proyecto independiente.

## Ahora conectado a AR651-B

Ejecuta el menú con el comando anterior y selecciona `configs/AR651-B/01_base_ospf.cfg` si corresponde comenzar por la configuración base. Luego selecciona el puerto serial que usa tu adaptador.

También puedes indicar el archivo y el puerto directamente:

```bash
# Linux (ajusta el puerto si es distinto)
uv run python src/code_python/serial_config.py --port /dev/ttyUSB0 --file configs/AR651-B/01_base_ospf.cfg

# Windows (sustituye COM3 por tu puerto)
uv run python src/code_python/serial_config.py --port COM3 --file configs/AR651-B/01_base_ospf.cfg
```

El programa muestra el prompt real del equipo, por ejemplo `<AR651-B>` o `<Huawei>`, y te pide escribir el destino declarado en el archivo, `AR651-B`, antes de aplicar los comandos. El nombre del archivo no detecta ni cambia el equipo al que está conectado el cable; comprueba esa correspondencia. El archivo sí puede incluir `sysname` para cambiar su nombre.

Si ya completaste la fase base, selecciona la siguiente etapa que corresponda. No ejecuta todos los archivos consecutivamente.

## Archivos y etapas

| Ruta | Uso |
|---|---|
| `src/code_python/serial_config.py` | Programa y menú |
| `configs/AR651-A/` | Archivos para el router A |
| `configs/AR651-B/` | Archivos para el router B |
| `configs/S6730H-C/` | Archivos para el switch C |
| `configs/S6730H-D/` | Archivos para el switch D |
| `referencia/MPLS_Lab_Huawei_Script_Completo.txt` | Documento original, sin modificar |
| `tests/test_serial_config.py` | Pruebas sin hardware |
| `outpu.txt` | Se crea en el directorio desde el que ejecutas el programa |

Cada equipo tiene:

1. `01_base_ospf.cfg`: configuración base y OSPF.
2. `01_verificar_ospf.cfg`: consultas de OSPF; A también incluye el ping IP del documento.
3. `02_lsp_estatico.cfg`: habilitación de MPLS y LSP estático.
4. `02_verificar_lsp.cfg`: consultas del LSP estático.
5. `03_cambiar_a_ldp.cfg`: eliminación del LSP estático y habilitación de LDP.
6. `03_verificar_ldp.cfg`: consultas de LDP.

C y D incluyen además `04_dod_opcional.cfg` y `05_restaurar_du.cfg`. Úsalos solo después de comprobar manualmente que tu VRP admite la sintaxis y en ambos extremos del enlace C-D, como indica el documento.

Primero aplica la fase 1 a los cuatro equipos y verifica OSPF y la conectividad. Después aplica la fase 2 y verifícala. La fase 3 sustituye el LSP estático por LDP; no es una ampliación que conserve el LSP anterior. El programa no verifica por sí mismo el estado de toda la topología.

Se conservaron los comandos de configuración del documento. Las pruebas de desconexión de enlaces, los reinicios, el borrado de configuración y los comandos de ayuda `?` permanecen en el documento de referencia para ejecución manual. Las variantes de `ping lsp ip`/`ipv4` y `tracert` requieren comprobar la sintaxis de tu versión. No se incluyeron como pruebas automáticas indistintas.

## Formato para tus próximos archivos

Un archivo representa una acción o etapa sobre un único equipo. Guarda texto UTF-8, con un comando por línea, por ejemplo:

```text
# device: AR651-B
# Verificación básica del equipo conectado
return
display interface brief
display ip interface brief
```

- `# device:` es una etiqueta para mostrar y confirmar el destino; no es un comando del router.
- Las líneas vacías y las que comienzan con `#` o `!` se ignoran.
- Los comentarios deben ir en líneas separadas; no pongas comentarios al final de un comando.
- Se elimina la indentación visual; el contexto depende de `system-view`, `interface`, `quit` y `return`.
- El menú busca recursivamente archivos `*.cfg` en `configs/`.
- `--file ruta/archivo.txt` también acepta otro nombre o extensión.
- No uses el documento MPLS completo como archivo de comandos: contiene instrucciones y varios equipos.
- No se admiten `?`, comandos partidos en varias líneas, banners multilínea, secuencias de control ni diálogos de primer arranque/cambio obligatorio de contraseña.

## Puerto y parámetros

Se usa **9600 baudios, 8 bits, sin paridad, 1 bit de parada y sin control de flujo** como valor inicial configurable. Debe coincidir con la configuración real de tu consola; el programa no detecta automáticamente la velocidad.

```bash
uv run python src/code_python/serial_config.py --baud 115200 --timeout 60
```

Cierra PuTTY, minicom u otro programa que tenga abierto ese puerto. En Linux tu usuario debe tener permisos sobre el dispositivo serial. En macOS puedes seleccionar el adaptador de la lista o indicar su ruta `/dev/cu...` con `--port`.

Si el equipo pide `Username:`, `Login:` o `Password:`, el programa solicita los datos. No añade la contraseña escrita a su registro de comandos; la salida que envíe el equipo sí se registra tal como llega. Si aparece un asistente inicial, cambio obligatorio de clave u otro diálogo no reconocido, complétalo previamente con una terminal serial y cierra esa terminal antes de ejecutar el programa.

## Envío y registro

Cada comando se envía con retorno de carro y el programa espera el siguiente prompt Huawei (`<nombre>` o `[nombre-vista]`), incluyendo cambios de nombre y de vista. Antes de aplicar el archivo vuelve a la vista de usuario si detecta una vista de configuración. No basta una pausa fija entre líneas para declarar terminado un comando.

La salida paginada con `---- More ----` se continúa mediante espacio. Ante preguntas `y/n`, el programa muestra la pregunta y pide tu respuesta; no responde `y` automáticamente.

Ante un error VRP reconocido o un timeout, se detiene y no envía los siguientes comandos. No hay rollback: los comandos anteriores pueden haber modificado la configuración. La detección cubre patrones habituales como `Error:`, `Unrecognized command`, `Incomplete command` y `Ambiguous command`; no sustituye la verificación funcional de OSPF/MPLS.

En S6730H-C/D, si `undo portswitch` no existe o la interfaz ya es Layer 3, revisa la salida y el estado del puerto antes de omitir esa línea en tu archivo. No se ignoran errores automáticamente. Si se corta la ejecución, revisa qué comandos se aplicaron antes de volver a comenzar; los archivos no se garantizan idempotentes en todas las versiones VRP.

El documento original indica ejecutar `save` solo cuando lo autorice el instructor. Ninguno de los archivos generados lo ejecuta y el programa tampoco lo añade. Aplicar comandos cambia la configuración activa; guardarla de forma persistente es otro paso. Si tú creas un archivo con `save`, el programa lo enviará y pedirá las confirmaciones reconocidas. Diálogos distintos, como selección de nombre de archivo, deben atenderse manualmente en una terminal.

El registro contiene el texto recibido por serial durante la sesión, incluidas secuencias de terminal. Se decodifica como UTF-8 por defecto; puedes usar `--encoding` si tu consola utiliza otra codificación. Se conserva la salida completa en el archivo, aunque los caracteres de control puedan afectar cómo la muestre un editor. Las respuestas del equipo pueden contener información sensible de su configuración.

```bash
# Revisar comandos sin abrir el puerto ni modificar el equipo
uv run python src/code_python/serial_config.py --file configs/AR651-B/01_base_ospf.cfg --dry-run

# Cambiar ubicación del registro (también añade, no sobrescribe)
uv run python src/code_python/serial_config.py --output registros/AR651-B.txt

# Ayuda
uv run python src/code_python/serial_config.py --help
```

Ctrl+C detiene el envío y cierra el puerto. La consola puede quedar en el último contexto o diálogo; revisa su estado antes de reintentar.

## Usarlo como proyecto independiente

Extrae la carpeta completa y ejecuta los comandos anteriores desde ella. Con el `pyproject.toml` incluido también está disponible:

```bash
uv run huawei-serial
uv run python -m code_python
```

## Validación

Se probaron la recepción fragmentada, cambio de prompt, paginación, parada por error y timeout, confirmaciones, login, carga de archivos y conservación del registro mediante una consola simulada. No se ha conectado este programa a un AR651/S6730 físico ni se ha validado la compatibilidad de los comandos con tu versión VRP.

Para ejecutar las pruebas:

```bash
uv run python -m unittest discover -s tests -v
```

API utilizada: [pySerial](https://pyserial.readthedocs.io/en/latest/pyserial_api.html) y [listado de puertos](https://pyserial.readthedocs.io/en/latest/tools.html).
