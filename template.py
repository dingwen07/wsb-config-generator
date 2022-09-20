from genericpath import isfile
import os
import configparser
import re

TEMPLATE_DIR = 'templates'

class TemplateParser():
    def __init__(self, template_dir: str = TEMPLATE_DIR, template_dirs: list = []):
        self.template_dirs = [template_dir] + template_dirs
        self.templates = {}
        self.template_files = {}
        self._template_files()
        self._templates_metadata()
    
    def set_environment(self, key: str, value: str):
        self.environments[key] = value

    @staticmethod
    def _parse_list_string(list_string: str) -> list:
        l = []
        for item in list_string.split(','):
            # remove whitespace
            item = item.strip()
            l.append(item)
        return l

    def _template_files(self) -> dict:
        for template_dir in self.template_dirs:
            for file in os.listdir(template_dir):
                abs_path = os.path.abspath(os.path.join(template_dir, file))
                base_name = os.path.basename(abs_path)
                if isfile(abs_path):
                    self.template_files[base_name] = abs_path

    def _templates_metadata(self) -> list:
        # parse basic info from each template file
        for template_basename, template_file in self.template_files.items(): 
            config = configparser.ConfigParser()
            config.read(template_file)
            template = {}
            template['name'] = config.get('Template', 'name')
            template['description'] = config.get('Template', 'description')
            if config.has_option('Template', 'author'):
                template['author'] = config.get('Template', 'author')
            requires = []
            if config.has_option('Template', 'requires'):
                requires = self._parse_list_string(config.get('Template', 'requires'))
            template['requires'] = requires
            template['basename'] = template_basename
            template['env_required'] = set()
            self.templates[template_basename] = template
        

    def parse_template(self, template_basename: str) -> tuple:
        # returns tuple of (mappings, commands)
        # mapping: (HostFolder, SandboxFolder, ReadOnly)
        template_file = self.template_files[template_basename]
        config = configparser.ConfigParser()
        config.read(template_file)

        # get number of mappings
        num_mappings = config.getint('Template', 'Mappings')
        mappings = []
        for i in range(1, num_mappings + 1):
            host_folder = config.get(f'Mapping{i}', 'HostFolder')
            sandbox_folder = config.get(f'Mapping{i}', 'SandboxFolder')
            read_only = config.getint(f'Mapping{i}', 'ReadOnly')
            if read_only == 0:
                read_only = False
            else:
                read_only = True
            mappings.append((host_folder, sandbox_folder, read_only))
            # check if env wrapped with <> is required in host_folder
            env_required = re.findall(r'<(.*?)>', host_folder)
            self.templates[template_basename]['env_required'].update(env_required)

        # get number of commands
        num_commands = config.getint('Template', 'Commands')
        commands = []
        for i in range(1, num_commands + 1):
            command = config.get(f'Command{i}', 'Command')
            commands.append(command)

        return (mappings, commands)
    

    def parse_templates(self, template_basenames: list) -> tuple:
        processed_templates = []
        to_do_templates = template_basenames

        mappings = []
        commands = []
        env_required = set()

        while len(to_do_templates) > 0:
            template_basename = to_do_templates.pop(0)
            if template_basename in processed_templates:
                continue
            mappings_temp, commands_temp = self.parse_template(template_basename)
            processed_templates.append(template_basename)
            to_do_templates += self.templates[template_basename]['requires']
            mappings += mappings_temp
            commands += commands_temp
            env_required.update(self.templates[template_basename]['env_required'])

        return (mappings, commands, env_required)
