"""Configurador serial Huawei VRP. Ejecutar desde la raíz del proyecto."""
from __future__ import annotations

import argparse
import codecs
from datetime import datetime
import getpass
from pathlib import Path
import re
import sys
import time

ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
PROMPT = re.compile(r"(?:^|\n)(<[^<>\r\n ]+>|\[[^\[\]\r\n ]+\])[ \t]*\Z")
ERROR = re.compile(r"(?im)^\s*(?:Error\s*:|%\s*(?:Error|Unrecognized|Unknown|Incomplete|Ambiguous)|(?:Unrecognized|Unknown|Incomplete|Ambiguous) command|Failure\s*:)")
QUESTION = re.compile(r"(?i)(?:\[(?:y(?:es)?/n(?:o)?|n/y)\]|\((?:y/n|yes/no)\))\s*[:?]?\s*$")
PAGER = re.compile(r"(?i)(?:-{2,}\s*More\s*-{2,}|--More--)\s*$")
LOGIN = re.compile(r"(?i)(?:^|\n)\s*(username|login|password):\s*$")


class SessionError(RuntimeError):
    pass


class Transcript:
    """Mismos textos en pantalla y archivo, vaciados inmediatamente."""
    def __init__(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file = path.open('a', encoding='utf-8', newline='')

    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()
        self.file.write(text)
        self.file.flush()

    def note(self, text):
        self.write('\n' + text + '\n')

    def ask(self, label, secret=False):
        self.write('\n' + label)
        if secret:
            answer = getpass.getpass('')
            self.file.write('[oculto]\n')
        else:
            answer = input()
            # input ya muestra el texto por eco local; guardarlo una sola vez.
            self.file.write(answer + '\n')
        self.file.flush()
        return answer

    def close(self):
        self.file.close()


def clean(text):
    text = ANSI.sub('', text).replace('\r', '')
    result = []
    for c in text:
        if c == '\b':
            if result and result[-1] != '\n':
                result.pop()
        else:
            result.append(c)
    return ''.join(result)


def load_config(path):
    commands = []
    target = None
    for number, raw in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
        line = raw.strip()
        if line.lower().startswith('# device:'):
            target = line.split(':', 1)[1].strip()
        if not line or line.startswith(('#', '!')):
            continue
        if any(ord(c) < 32 for c in line) or '?' in line:
            raise ValueError(f'{path}:{number}: no se admite ayuda interactiva ni caracteres de control.')
        commands.append((number, line))
    if not commands:
        raise ValueError('El archivo no contiene comandos.')
    return target, commands


class Console:
    def __init__(self, port, log, timeout=30, encoding='utf-8', quiet=0.25):
        self.port = port
        self.log = log
        self.timeout = timeout
        self.quiet = quiet
        self.encoding = encoding
        self.decoder = codecs.getincrementaldecoder(encoding)(errors='replace')
        self.prompt = ''

    def send(self, text, secret=False):
        self.log.note('[TX] ' + ('[oculto]' if secret else text))
        data = (text + '\r').encode(self.encoding)
        if self.port.write(data) != len(data):
            raise SessionError('Escritura serial incompleta; se detuvo el envío.')

    def wait_prompt(self, login=False):
        deadline = time.monotonic() + self.timeout
        last_rx = time.monotonic()
        pending = ''
        response = ''
        attempts = 0
        while time.monotonic() < deadline:
            data = self.port.read(min(max(self.port.in_waiting, 1), 8192))
            if data:
                text = self.decoder.decode(data)
                self.log.write(text)
                pending += text
                response += text
                last_rx = time.monotonic()
                continue
            if time.monotonic() - last_rx < self.quiet:
                continue
            screen = clean(pending)
            match = PROMPT.search(screen)
            if match and not QUESTION.search(screen):
                self.prompt = match.group(1)
                return clean(response)
            if PAGER.search(screen):
                self.log.note('[TX] espacio para continuar la salida')
                if self.port.write(b' ') != 1:
                    raise SessionError('No se pudo continuar la salida paginada.')
                pending = ''
                continue
            match = LOGIN.search(screen)
            if match:
                if not login or attempts >= 6:
                    raise SessionError('Se requiere iniciar sesión; no se enviaron más comandos.')
                secret = match.group(1).lower() == 'password'
                answer = self.log.ask('Contraseña: ' if secret else 'Usuario: ', secret)
                self.send(answer, secret)
                attempts += 1
                pending = ''
                deadline = time.monotonic() + self.timeout
                continue
            if QUESTION.search(screen):
                answer = self.log.ask('El equipo solicita confirmación. Responde y/n: ').strip().lower()
                if answer not in ('y', 'n'):
                    raise SessionError('Respuesta no válida. Se detuvo el envío.')
                self.send(answer)
                pending = ''
                deadline = time.monotonic() + self.timeout
        raise SessionError('Tiempo agotado esperando el prompt. Revisa outpu.txt, la consola y la velocidad serial.')

    def command(self, command):
        self.send(command)
        response = self.wait_prompt()
        if ERROR.search(response):
            raise SessionError(f'El equipo rechazó: {command!r}. Se detuvo el envío; los comandos anteriores permanecen aplicados.')
        return response

    def apply(self, commands):
        for index, (line, command) in enumerate(commands, 1):
            self.log.note(f'[{index}/{len(commands)}] Línea {line}')
            self.command(command)


def choose(log, title, options):
    if not options:
        raise ValueError(f'No hay opciones disponibles: {title}')
    log.note(title)
    for i, option in enumerate(options, 1):
        log.note(f'  {i}. {option}')
    while True:
        answer = log.ask('Número: ').strip()
        if answer.isdigit() and 1 <= int(answer) <= len(options):
            return int(answer) - 1
        log.note('Selecciona un número de la lista.')


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', help='COM3, /dev/ttyUSB0, etc.; si se omite, muestra un menú')
    p.add_argument('--baud', type=int, default=9600, help='Velocidad configurada en el equipo (predeterminado: 9600)')
    p.add_argument('--file', type=Path, help='Archivo de comandos; si se omite, muestra un menú')
    p.add_argument('--configs', type=Path, default=Path('configs'))
    p.add_argument('--output', type=Path, default=Path('outpu.txt'))
    p.add_argument('--timeout', type=float, default=30, help='Máximo de segundos por comando')
    p.add_argument('--encoding', default='utf-8')
    p.add_argument('--dry-run', action='store_true', help='Mostrar comandos sin abrir ningún puerto')
    return p


def main(argv=None):
    args = parser().parse_args(argv)
    log = Transcript(args.output)
    port = None
    try:
        log.note('=== Sesión ' + datetime.now().astimezone().isoformat(timespec='seconds') + ' ===')
        if args.timeout <= 0 or args.baud <= 0:
            raise ValueError('La velocidad y el timeout deben ser positivos.')
        codecs.lookup(args.encoding)
        if args.file:
            config = args.file
        else:
            configs = sorted(args.configs.rglob('*.cfg'))
            config = configs[choose(log, 'Selecciona el archivo para el equipo conectado:', configs)]
        target, commands = load_config(config)
        log.note(f'Archivo: {config.resolve()} | Destino declarado: {target or "sin especificar"}')
        log.note(f'{len(commands)} comandos; registro: {args.output.resolve()}')
        if args.dry_run:
            for line, command in commands:
                log.note(f'{line:4}: {command}')
            log.note('Simulación terminada; no se abrió ningún puerto serial.')
            return 0
        try:
            import serial
            from serial.tools import list_ports
        except ImportError as exc:
            raise SessionError('Falta pyserial. Ejecuta: uv add pyserial') from exc
        device = args.port
        if not device:
            ports = sorted(list_ports.comports(), key=lambda item: item.device)
            if ports:
                selected = choose(log, 'Selecciona el puerto serial:', [f'{p.device} — {p.description}' for p in ports])
                device = ports[selected].device
            else:
                device = log.ask('No se detectaron puertos. Escribe el puerto (COM3, /dev/ttyUSB0): ').strip()
        log.note(f'Abriendo {device}: {args.baud} baudios, 8N1, sin control de flujo.')
        options = dict(port=device, baudrate=args.baud, bytesize=8, parity='N', stopbits=1,
                       timeout=0.1, write_timeout=5, xonxoff=False, rtscts=False, dsrdtr=False)
        port = serial.Serial(**options)
        console = Console(port, log, args.timeout, args.encoding)
        # Primero leer lo que ya está en la consola; no descartar buffers.
        # Un CR permite mostrar el prompt o despertar el inicio de sesión.
        console.send('')
        console.wait_prompt(login=True)
        log.note(f'Prompt recibido: {console.prompt}')
        expected = target or 'APLICAR'
        answer = log.ask(f'Verifica el equipo físico. Escribe {expected} para enviar este archivo: ').strip()
        if answer != expected:
            log.note('Cancelado; no se enviaron comandos de configuración.')
            return 1
        # Actualizar el prompt tras la pausa humana; detectar expiración de sesión.
        console.send('')
        console.wait_prompt()
        if console.prompt.startswith('['):
            console.command('return')
        console.apply(commands)
        log.note('Archivo enviado por completo. No se ejecuta save automáticamente; la persistencia depende de los comandos de tu archivo.')
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        log.note(f'DETENIDO: {str(exc) or "Interrumpido por el usuario"}')
        log.note('No se continúa ni se revierte automáticamente. Comprueba el estado actual antes de reintentar.')
        return 130 if isinstance(exc, KeyboardInterrupt) else 1
    finally:
        try:
            if port is not None:
                port.close()
        finally:
            log.note('=== Fin de sesión ===')
            log.close()


if __name__ == '__main__':
    raise SystemExit(main())
