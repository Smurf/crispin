import json
from pathlib import Path

def generate_menu(cookbook_dir, hostname):
    """
    Generates an iPXE menu from the answer files in the cookbook.
    """
    answers_dir = Path(cookbook_dir) / "answers"
    if not answers_dir.exists():
        return "#!ipxe\necho No answer files found\nshell"

    menu = "#!ipxe\n\n"
    menu += "menu Crispin iPXE Boot Menu\n\n"

    answer_files = sorted(list(answers_dir.glob("*.json")))
    if not answer_files:
        return "#!ipxe\necho No answer files found\nshell"

    default_item = answer_files[0].stem
    for answer_file in answer_files:
        answer_name = answer_file.stem
        menu += f"item {answer_name} {answer_name}\n"

    menu += f"\nchoose --default {default_item} --timeout 5000 target && goto ${{target}}\n\n"

    for answer_file in answer_files:
        answer_name = answer_file.stem
        menu += f":{answer_name}\n"

        with open(answer_file, "r") as f:
            try:
                data = json.load(f)
                source = data.get("metadata", {}).get("source")
            except json.JSONDecodeError:
                source = None

        kernel_url = f"http://{hostname}:9000/vmlinuz"
        initrd_url = f"http://{hostname}:9000/initrd.img"

        if source:
            if source.startswith("http://") or source.startswith("https://"):
                kernel_url = f"{source}vmlinuz"
                initrd_url = f"{source}initrd.img"
            else:
                kernel_url = f"http://{hostname}:9000/{source}/vmlinuz"
                initrd_url = f"http://{hostname}:9000/{source}/initrd.img"

        menu += f"kernel {kernel_url} inst.ks=http://{hostname}:9000/crispin/get/{answer_name} quiet\n"
        menu += f"initrd {initrd_url}\n"
        menu += "boot\n"

    return menu
