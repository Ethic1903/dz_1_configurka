import unittest
import os
import tarfile
import tempfile
from emulator import Emulator
from io import StringIO
import sys


class TestEmulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.tar_path = os.path.join(cls.temp_dir, 'test_virtual_fs.tar')

        with tarfile.open(cls.tar_path, 'w') as tar:
            file1_path = os.path.join(cls.temp_dir, 'file1.txt')
            with open(file1_path, 'w') as f:
                f.write('Hello, world!')
            tar.add(file1_path, arcname='file1.txt')

        cls.config_path = os.path.join(cls.temp_dir, 'test_config.json')
        with open(cls.config_path, 'w') as f:
            f.write(f'{{"tar_path": "{cls.tar_path.replace("\\", "/")}", "startup_script": "test_startup.sh"}}')

        cls.startup_script_path = os.path.join(cls.temp_dir, 'test_startup.sh')
        with open(cls.startup_script_path, 'w') as f:
            f.write('')

        cls.emulator = Emulator(cls.config_path)

    @staticmethod
    def _suppress_output():
        sys_stdout = sys.stdout
        sys_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        return sys_stdout, sys_stderr

    @staticmethod
    def _restore_output(sys_stdout, sys_stderr):
        sys.stdout = sys_stdout
        sys.stderr = sys_stderr

    def test_ls(self):
        sys_stdout, sys_stderr = self._suppress_output()
        try:
            output = self._capture_output(self.emulator.ls)
            self.assertIn('file1.txt', output)
        finally:
            self._restore_output(sys_stdout, sys_stderr)

    def test_cd(self):
        sys_stdout, sys_stderr = self._suppress_output()
        try:
            self.emulator.cd('/')
            self.assertEqual(self.emulator.current_dir, '/')
        finally:
            self._restore_output(sys_stdout, sys_stderr)

    def test_mkdir(self):
        sys_stdout, sys_stderr = self._suppress_output()
        try:
            self.emulator.current_dir = "/"
            command = 'mkdir new_folder'
            output = self._capture_output(lambda: self.emulator.run_command(command))
            self.assertIn("Directory 'new_folder' created", output)
            self.assertIn("new_folder", self.emulator.new_directories)
            output = self._capture_output(lambda: self.emulator.run_command(command))
            self.assertIn("mkdir: cannot create directory 'new_folder': File exists", output)
        finally:
            self._restore_output(sys_stdout, sys_stderr)

    def test_rev(self):
        sys_stdout, sys_stderr = self._suppress_output()
        try:
            filename = "virtual_fs/file.txt"
            expected_output = "!dlrow ,olleH"
            self.emulator.cd("virtual_fs")
            output = self.emulator.rev(filename)
        finally:
            self._restore_output(sys_stdout, sys_stderr)

    @staticmethod
    def _capture_output(function):
        captured_output = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured_output
        try:
            function()
        finally:
            sys.stdout = sys_stdout
        return captured_output.getvalue()

    @classmethod
    def tearDownClass(cls):
        for file in os.listdir(cls.temp_dir):
            file_path = os.path.join(cls.temp_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

        if os.path.exists(cls.tar_path):
            os.remove(cls.tar_path)
        if os.path.exists(cls.config_path):
            os.remove(cls.config_path)
        if os.path.exists(cls.startup_script_path):
            os.remove(cls.startup_script_path)

        os.rmdir(cls.temp_dir)


if __name__ == '__main__':
    unittest.main()
