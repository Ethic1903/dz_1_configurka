import os
import tarfile
import json

class Emulator:
    def __init__(self, config_path):
        self.load_config(config_path)
        self.current_dir = "/"
        self.file_structure = {}
        self.new_directories = set()
        self.load_virtual_fs()
        self.execute_startup_script()

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
            self.tar_path = config['tar_path']
            self.startup_script = config['startup_script']

    def load_virtual_fs(self):
        with tarfile.open(self.tar_path, 'r') as tar:
            for member in tar.getmembers():
                self.file_structure[member.name] = member

    def execute_startup_script(self):
        if os.path.exists(self.startup_script):
            with open(self.startup_script, 'r') as script:
                for command in script:
                    self.run_command(command.strip())

    def cd(self, path):
        if path == "/":
            self.current_dir = "/"
            return

        new_path = os.path.normpath(os.path.join(self.current_dir, path)).strip("/")

        if new_path in self.file_structure and self.file_structure[new_path].isdir():
            self.current_dir = "/" + new_path
        elif new_path in self.new_directories:
            self.current_dir = "/" + new_path
        else:
            print(f"cd: {path}: No such directory")

    def ls(self):
        current_dir_content = [
            os.path.basename(member)
            for member in self.file_structure
            if os.path.dirname(member).strip("/") == self.current_dir.strip("/")
        ]
        current_dir_content.extend([
            os.path.basename(new_dir)
            for new_dir in self.new_directories
            if os.path.dirname(new_dir).strip("/") == self.current_dir.strip("/")
        ])
        if current_dir_content:
            for item in current_dir_content:
                print(item)
        else:
            print("(empty)")

    def mkdir(self, dirname):
        new_dir = os.path.normpath(os.path.join(self.current_dir, dirname)).replace('\\', '/').strip("/")
        if new_dir in self.file_structure or new_dir in self.new_directories:
            print(f"mkdir: cannot create directory '{dirname}': File exists")
        else:
            self.new_directories.add(new_dir)
            print(f"Directory '{dirname}' created")

    def rev(self, filename):
        filename = filename.replace('\\', '/')
        filepath = os.path.normpath(os.path.join(self.current_dir, filename)).strip("/")
        if filepath in self.file_structure and self.file_structure[filepath].isfile():
            with tarfile.open(self.tar_path, 'r') as tar:
                content = tar.extractfile(self.file_structure[filepath]).read().decode('utf-8')
                print(content[::-1])
        else:
            print(f"rev: {filename}: No such file")

    def run_command(self, command):
        if command == "exit":
            return False
        elif command.startswith("cd"):
            parts = command.split()
            if len(parts) > 1:
                self.cd(parts[1])
            else:
                self.cd("/")
        elif command == "ls":
            self.ls()
        elif command.startswith("mkdir"):
            parts = command.split()
            if len(parts) > 1:
                self.mkdir(parts[1])
            else:
                print("mkdir: missing operand")
        elif command.startswith("rev"):
            parts = command.split()
            if len(parts) > 1:
                self.rev(parts[1])
            else:
                print("rev: missing operand")
        else:
            print(f"{command}: command not found")
        return True

    def run(self):
        while True:
            command = input(f"{self.current_dir} $ ")
            if not self.run_command(command):
                break

if __name__ == "__main__":
    config_path = "/mnt/c/Users/georgiyf/PycharmProjects/shell_emulator/config_1.json"
    emulator = Emulator(config_path)
    emulator.run()
