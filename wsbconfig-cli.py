import os
import configparser

from wsbconfig import WSBConfigHelper
from template import TemplateParser

def yes_or_no(question, default=False):
    if default:
        question = question + " [Y/n]: "
    else:
        question = question + " [y/N]: "
    while True:
        choice = input(question).lower()
        if choice == '':
            return default
        elif choice in ['y', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False

if __name__ == "__main__":
    # create config

    config = WSBConfigHelper()
    parser = TemplateParser()
    config_parser = configparser.ConfigParser()
    wsb_config = {}
    ui_config = {}
    env_vars = {}
    if os.path.exists('config.ini'):
        config_parser.read('config.ini')
        if config_parser.has_section('Config'):
            ui_config = dict(config_parser.items('Config'))
        if config_parser.has_section('WSBConfig'):
            wsb_config = dict(config_parser.items('WSBConfig'))
        if config_parser.has_section('Environments'):
            env_vars = dict(config_parser.items('Environments'))

    print(wsb_config)
    print(env_vars)


    # ask user for config
    # vGPU if not in WSBConfig section of config.ini
    if 'vgpu' not in wsb_config:
        vgpu = yes_or_no("Enable vGPU?", default=False)
    else:
        vgpu = wsb_config['vgpu'] == '1'
    config.set_vgpu(vgpu)
    # Networking
    if 'networking' not in wsb_config:
        networking = yes_or_no("Allow Networking?", default=True)
    else:
        networking = wsb_config['networking'] == '1'
    config.set_networking(networking)
    # AudioInput
    if 'audioinput' not in wsb_config:
        audio_input = yes_or_no("Allow Audio Input?", default=False)
    else:
        audio_input = wsb_config['audioinput'] == '1'
    config.set_audio_input(audio_input)
    # VideoInput
    if 'videoinput' not in wsb_config:
        video_input = yes_or_no("Allow Video Input?", default=False)
    else:
        video_input = wsb_config['videoinput'] == '1'
    config.set_video_input(video_input)
    # Protected Client
    if 'protectedclient' not in wsb_config:
        protected_client = yes_or_no("Protected Client?", default=False)
    else:
        protected_client = wsb_config['protectedclient'] == '1'
    config.set_protected_client(protected_client)
    # Printer Redirection
    if 'printerredirection' not in wsb_config:
        printer_redirection = yes_or_no("Enable Printer Redirection?", default=False)
    else:
        printer_redirection = wsb_config['printerredirection'] == '1'
    config.set_printer_redirection(printer_redirection)
    # Clipboard Redirection
    if 'clipboardredirection' not in wsb_config:
        clipboard_redirection = yes_or_no("Enable Clipboard Redirection?", default=True)
    else:
        clipboard_redirection = wsb_config['clipboardredirection'] == '1'
    config.set_clipboard_redirection(clipboard_redirection)
    # Memory in MB
    if 'memoryinmb' not in wsb_config:
        memory_in_mb = input("Memory in MB: ")
        if memory_in_mb != '':
            try:
                memory_in_mb = int(memory_in_mb)
            except ValueError:
                print("Invalid memory value. Using default.")
                memory_in_mb = None
    else:
        memory_in_mb = int(wsb_config['memoryinmb'])
    config.set_memory_in_mb(memory_in_mb)

    if 'templates' in ui_config:
        templates = TemplateParser._parse_list_string(ui_config['templates'])
    else:
        # print templates
        # use numbered list for user to choose from
        print()
        template_lookup = {}
        print("Available templates:")
        for i, template in enumerate(parser.templates.values()):
            # print number and template name
            print(f"{i+1}. {template['name']}")
            # print description
            print(f"        {template['description']}")
            # add to lookup
            template_lookup[i+1] = template['basename']

        # ask user to choose template, split by space
        templates_selected = input("Choose template(s): ").split()
        # remove whitespace
        templates_selected = [template.strip() for template in templates_selected]
        # convert to int
        templates_selected = [int(template) for template in templates_selected]
        # get template basenames
        templates = [template_lookup[template] for template in templates_selected]

    # parse templates
    mappings, commands, env_required = parser.parse_templates(templates)

    # make a copy of env_required
    env_required_copy = env_required.copy()

    # remove existing env vars from env_required_copy
    for env_var in env_vars:
        if env_var in env_required_copy:
            env_required_copy.remove(env_var)

    # let user provide environment variables
    print('Please provide the following environment variables:')
    for env in env_required_copy:
        env_vars[env] = input(f"{env}: ")
    
    # replace environment variables in host_folders in mappings
    new_mappings = []
    sandbox_folders = []
    
    for mapping in mappings:
        host_folder = mapping[0]
        sandbox_folder = mapping[1]
        for env in env_required:
            # replace <env> with environment[env]
            host_folder = host_folder.replace(f"<{env}>", env_vars[env])
        # expand OS variables and get absolute path
        host_folder = os.path.abspath(os.path.expandvars(host_folder))
        # add to new_mappings if sandbox_folder is not in sandbox_folders
        if sandbox_folder in sandbox_folders:
            print(f"Warning: {sandbox_folder} already exists in mappings. Skipping.")
            continue
        else:
            new_mappings.append((host_folder, sandbox_folder))
            sandbox_folders.append(sandbox_folder)
        # create folder if config says to
        if 'makedir' in ui_config and ui_config['makedir'] != '0':
            os.makedirs(host_folder, exist_ok=True)
        print(host_folder)
    
    # add mappings to config
    for mapping in new_mappings:
        config.add_mapped_folder(*mapping)
    # add commands to config
    for command in commands:
        config.add_logon_command(command)
    
    # write config
    # if outputpath is not in Config section of config.ini
    # get user input for filename
    if 'outputpath' not in ui_config:
        output_path = input("Output path: ")
    else:
        output_path = ui_config['outputpath']
    config.save(output_path)

    






