import json
import logging
from pathlib import Path
from urllib.parse import urljoin
class MenuEntry:

    def __init__(self, name:str, bootcmd=None):
        self.name = name
        self.bootcmd = self._bootcmd(bootcmd)
        self.item = self._item(name)
    
    def _item(self, name):
        return f"item {name} {name}\n\n"

    def _bootcmd(self, cmd):
        entry = f":{self.name}\n"
        entry += f"{cmd}\n\n"
        return entry

class IPXEMenu:

    def __init__(self, menu_entries:list[MenuEntry]):
        self.menu = ""
        self.menu = "#!ipxe\n\n"
        self.menu += "dhcp\n\n"
        self.menu += "menu Crispin iPXE Boot Menu\n\n"
        
        self.menu_entries = menu_entries

    def __str__(self):
        menu = self.menu
        # Create items first!
        for entry in self.menu_entries:
            menu += entry.item
        
        menu += f"\nchoose --default {self.menu_entries[0].name} --timeout 60000 target && goto ${{target}}\n\n"

        for entry in self.menu_entries:
            menu += entry.bootcmd
        
        return menu

def generate_menu(cookbook_dir, hostname):
    """
    Generates an iPXE menu from the answer files in the cookbook.
    """
    logging.debug("Generating iPXE menu.")
    answers_dir = Path(cookbook_dir) / "answers"
    if not answers_dir.exists():
        logging.error(f"Answer dir {answers_dir} does not exist!")
        return "#!ipxe\necho No answer files found\nshell"

    menu_entries = []

    answer_files = sorted(list(answers_dir.glob("*.json")))
    if not answer_files:
        logging.error(f"No answer files found in {answers_dir}!")
        return "#!ipxe\necho No answer files found\nshell"

    for answer_file in answer_files:
        answer_name = answer_file.stem
        logging.debug(f"Set default entry {answer_name}.")

    for answer_file in answer_files:
        answer_name = answer_file.stem
        logging.debug(f"Creating menu entry for {answer_name}.")
        with open(answer_file, "r") as f:
            try:
                data = json.load(f)
                source = data.get("metadata", {}).get("source")
                logging.debug(f"Found source {source}.")
            except json.JSONDecodeError:
                source = None
                logging.error(f"Check metadata for {answer_file}. An error ocurred parsing it.")
                logging.warning(f"JSON parsing error for answer file {f.name}, skipping...")
                continue #Skip that shit

        if source:
            match source:
                case uri if source.startswith("http") and source.endswith("/"):
                    logging.debug(f"Found a URI for {answer_file} that appears to be an http repo: {uri}")
                    kernel_url = urljoin(source, "images/pxeboot/vmlinuz")
                    initrd_url = urljoin(source, "images/pxeboot/initrd.img")
                    stage2_url = urljoin(source, "images/install.img")

                    bootcmd = f"kernel {kernel_url} inst.ks=http://{hostname}:9000/crispin/get/{answer_name} inst.repo={source} ip=dhcp quiet\n"
                    bootcmd += f"initrd {initrd_url}\n"
                    bootcmd += "boot"

                    menu_entry = MenuEntry(answer_name, bootcmd)
                    menu_entries.append(menu_entry)

                case uri if source.endswith(".iso"):
                    logging.debug(f"Found URI for {answer_file} that is an ISO file: {uri}.")

                case uri if source.endswith("/") and Path(source).exists():
                    logging.debug(f"Found URI for {answer_file} that appears to be a crispin hosted file: {uri}.")
                    kernel_url = f"http://{hostname}:9000/{source}/vmlinuz"
                    initrd_url = f"http://{hostname}:9000/{source}/initrd.img"
                    stage2_url = f"http://{hostname}:9000/{source}/install.img"

                    bootcmd = f"kernel {kernel_url} inst.ks=http://{hostname}:9000/crispin/get/{answer_name} inst.repo={source} inst.stage2={stage2_url} ip=dhcp quiet\n"
                    bootcmd += f"initrd {initrd_url}\n"
                    bootcmd += "boot"

                    menu_entry = MenuEntry(answer_name, bootcmd)
                    menu_entries.append(menu_entry)

                case _:
                    logging.warning(f"Source in metadata could not be parsed! Skipping {answer_file}!")
                    continue

    menu = IPXEMenu(menu_entries)
    return str(menu)
