import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from code_python.serial_config import Console, SessionError, load_config, main

class Log:
    def __init__(self, answers=()): self.text=''; self.answers=iter(answers)
    def write(self, value): self.text += value
    def note(self, value): self.text += '\n'+value+'\n'
    def ask(self, *args): return next(self.answers)

class Port:
    def __init__(self, exchanges): self.exchanges=dict(exchanges); self.chunks=[]; self.writes=[]
    @property
    def in_waiting(self): return len(self.chunks[0]) if self.chunks else 0
    def write(self, data):
        self.writes.append(data)
        self.chunks.extend(self.exchanges.get(data, []))
        return len(data)
    def read(self, size): return self.chunks.pop(0) if self.chunks else b''

class ConsoleTests(unittest.TestCase):
    def test_fragmented_prompts_and_rename(self):
        port=Port({b'system-view\r':[b'system-view\r\n[Hua',b'wei]'],b'sysname AR651-B\r':[b'sysname AR651-B\r\n[AR651-',b'B]'],b'return\r':[b'return\r\n<AR651-B>']})
        c=Console(port,Log(),quiet=0)
        c.apply([(1,'system-view'),(2,'sysname AR651-B'),(3,'return')])
        self.assertEqual(c.prompt,'<AR651-B>'); self.assertEqual(len(port.writes),3)

    def test_stop_after_error(self):
        port=Port({b'bad\r':[b'bad\r\nError: Unrecognized command\r\n[AR651-B]']})
        with self.assertRaises(SessionError): Console(port,Log(),quiet=0).apply([(1,'bad'),(2,'must-not-run')])
        self.assertEqual(port.writes,[b'bad\r'])

    def test_pager_and_log(self):
        port=Port({b'display x\r':[b'page1\r\n---- More ----'],b' ':[b'\r\npage2\r\n<AR651-B>']})
        log=Log(); Console(port,log,quiet=0).command('display x')
        self.assertEqual(port.writes,[b'display x\r',b' ']); self.assertIn('page1',log.text); self.assertIn('page2',log.text)

    def test_confirmation_not_automatic(self):
        for question in [b'Continue? [Y/N]',b'\r\n[Y/N]']:
            port=Port({b'test\r':[question],b'n\r':[b'\r\n<AR651-B>']})
            Console(port,Log(['n']),quiet=0).command('test')
            self.assertEqual(port.writes,[b'test\r',b'n\r'])

    def test_timeout_stops(self):
        port=Port({})
        with self.assertRaises(SessionError): Console(port,Log(),timeout=0.001,quiet=0).apply([(1,'first'),(2,'second')])
        self.assertEqual(port.writes,[b'first\r'])

    def test_login(self):
        port=Port({b'\r':[b'Username:'],b'admin\r':[b'\r\nPassword:'],b'secret\r':[b'\r\n<AR651-B>']})
        log=Log(['admin','secret']); c=Console(port,log,quiet=0); c.send(''); c.wait_prompt(login=True)
        self.assertNotIn('secret',log.text); self.assertIn(b'secret\r',port.writes)

    def test_partial_write_stops(self):
        port=Port({})
        with patch.object(port, 'write', return_value=1):
            with self.assertRaises(SessionError):
                Console(port,Log(),quiet=0).command('system-view')

    def test_disconnection_stops_before_next_command(self):
        port=Port({})
        with patch.object(port, 'read', side_effect=OSError('desconectado')):
            with self.assertRaises(OSError):
                Console(port,Log(),quiet=0).apply([(1,'first'),(2,'second')])
        self.assertEqual(port.writes,[b'first\r'])

    def test_parser(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'router.cfg'; p.write_text('\ufeff# device: AR651-B\n! comment\n\n system-view\n return\n',encoding='utf-8')
            self.assertEqual(load_config(p),('AR651-B',[(4,'system-view'),(5,'return')]))
            p.write_text('mpls ?\n')
            with self.assertRaises(ValueError): load_config(p)

    def test_dry_run_append(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'test.cfg'; f.write_text('display version\n')
            log=Path(d)/'outpu.txt'; log.write_text('ANTERIOR\n')
            with patch('sys.stdout'): result=main(['--dry-run','--file',str(f),'--output',str(log)])
            self.assertEqual(result,0); text=log.read_text()
            self.assertTrue(text.startswith('ANTERIOR')); self.assertIn('display version',text); self.assertIn('Fin de sesión',text)

    def test_sample_configs(self):
        configs=list(Path('configs').rglob('*.cfg')); self.assertEqual(len(configs),28)
        for p in configs:
            target,commands=load_config(p); self.assertEqual(target,p.parent.name); self.assertTrue(commands)
            self.assertNotIn('save',[c for _,c in commands])
        _,commands=load_config(Path('configs/AR651-B/01_base_ospf.cfg'))
        self.assertIn('ip address 10.0.34.2 255.255.255.252',[c for _,c in commands])

if __name__=='__main__': unittest.main()
