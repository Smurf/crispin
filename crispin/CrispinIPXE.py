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
        menu += f"kernel http://{hostname}:9000/vmlinuz inst.ks=http://{hostname}:9000/crispin/get/{answer_name} quiet\n"
        menu += f"initrd http://{hostname}:9000/initrd.img\n"
        menu += "boot\n"

    return menu
