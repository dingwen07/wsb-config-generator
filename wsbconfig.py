import xml.etree.ElementTree as ET


class WSBConfig:
    TEXT_ENABLED = "Enable"
    TEXT_DISABLED = "Disable"
    TEXT_DEFAULT = "Default"

    def __init__(self):
        self.clear()
    
    def clear(self):
        self.root = ET.Element("Configuration")
        # add MappedFolders (list)
        self.mapped_folders_e = ET.SubElement(self.root, "MappedFolders")
        # add LogonCommand (list)
        self.logon_command_e = ET.SubElement(self.root, "LogonCommand")
    
    def config(self):
        return ET.tostring(self.root, encoding="unicode", method="xml")

    def set_vgpu(self, enabled: bool):
        child = ET.SubElement(self.root, "vGPU")
        if enabled:
            child.text = self.TEXT_ENABLED
        else:
            child.text = self.TEXT_DISABLED
    
    def set_networking(self, enabled: bool):
        child = ET.SubElement(self.root, "Networking")
        if enabled:
            child.text = self.TEXT_DEFAULT
        else:
            child.text = self.TEXT_DISABLED
        
    def add_mapped_folder(self, host_folder: str, sandbox_folder: str, read_only: bool = False):
        # create MappedFolder element
        mapped_folder_e = ET.SubElement(self.mapped_folders_e, "MappedFolder")
        # set HostFolder
        host_folder_e = ET.SubElement(mapped_folder_e, "HostFolder")
        host_folder_e.text = host_folder
        # set SandboxFolder
        sandbox_folder_e = ET.SubElement(mapped_folder_e, "SandboxFolder")
        sandbox_folder_e.text = sandbox_folder
        # set ReadOnly
        read_only_e = ET.SubElement(mapped_folder_e, "ReadOnly")
        if read_only:
            read_only_e.text = 'true'
        else:
            read_only_e.text = 'false'
    
    def add_logon_command(self, command: str):
        child = ET.SubElement(self.logon_command_e, "Command")
        child.text = command
    
    def set_audio_input(self, enabled: bool):
        child = ET.SubElement(self.root, "AudioInput")
        if enabled:
            child.text = self.TEXT_ENABLED
        else:
            child.text = self.TEXT_DISABLED
    
    def set_video_input(self, enabled: bool):
        child = ET.SubElement(self.root, "VideoInput")
        if enabled:
            child.text = self.TEXT_ENABLED
        else:
            child.text = self.TEXT_DISABLED
    
    def set_protected_client(self, enabled: bool):
        child = ET.SubElement(self.root, "ProtectedClient")
        if enabled:
            child.text = self.TEXT_ENABLED
        else:
            child.text = self.TEXT_DISABLED
    
    def set_printer_redirection(self, enabled: bool):
        child = ET.SubElement(self.root, "PrinterRedirection")
        if enabled:
            child.text = self.TEXT_ENABLED
        else:
            child.text = self.TEXT_DISABLED
    
    def set_clipboard_redirection(self, enabled: bool):
        child = ET.SubElement(self.root, "ClipboardRedirection")
        if enabled:
            child.text = self.TEXT_DEFAULT
        else:
            child.text = self.TEXT_DISABLED
    
    def set_memory_in_mb(self, memory: int):
        child = ET.SubElement(self.root, "MemoryInMB")
        child.text = str(memory)


class WSBConfigHelper(WSBConfig):
    def __init__(self):
        self.clear()
    
    def clear(self):
        super().clear()
        self.vgpu = False
        self.networking = True
        self.mapped_folders = []
        self.logon_command = []
        self.audio_input = False
        self.video_input = False
        self.protected_client = False
        self.printer_redirection = False
        self.clipboard_redirection = True
        self.memory_in_mb = None
    
    def set_vgpu(self, enabled: bool):
        self.vgpu = enabled
    
    def set_networking(self, enabled: bool):
        self.networking = enabled
    
    def add_mapped_folder(self, host_folder: str, sandbox_folder: str, read_only: bool = False):
        self.mapped_folders.append((host_folder, sandbox_folder, read_only))
    
    def add_logon_command(self, command: str):
        self.logon_command.append(command)
    
    def set_audio_input(self, enabled: bool):
        self.audio_input = enabled
    
    def set_video_input(self, enabled: bool):
        self.video_input = enabled
    
    def set_protected_client(self, enabled: bool):
        self.protected_client = enabled
    
    def set_printer_redirection(self, enabled: bool):
        self.printer_redirection = enabled
    
    def set_clipboard_redirection(self, enabled: bool):
        self.clipboard_redirection = enabled
    
    def set_memory_in_mb(self, memory: int):
        self.memory_in_mb = memory
    
    def apply(self):
        super().clear()
        super().set_vgpu(self.vgpu)
        super().set_networking(self.networking)
        for host_folder, sandbox_folder, read_only in self.mapped_folders:
            super().add_mapped_folder(host_folder, sandbox_folder, read_only)
        for command in self.logon_command:
            super().add_logon_command(command)
        super().set_audio_input(self.audio_input)
        super().set_video_input(self.video_input)
        super().set_protected_client(self.protected_client)
        super().set_printer_redirection(self.printer_redirection)
        super().set_clipboard_redirection(self.clipboard_redirection)
        if self.memory_in_mb is not None:
            super().set_memory_in_mb(self.memory_in_mb)
        
        return super().config()
    
    def config(self):
        self.apply()
        return super().config()
    
    def save(self, path: str):
        with open(path, 'w') as f:
            f.write(self.config())
