#!/usr/bin/env python3

import argparse, json, logging, sys
from pathlib import Path
from jinja2 import Environment, Undefined
from typing import Dict

# https://stackoverflow.com/a/77311286
def create_collector():
    collected_variables = set()

    class CollectUndefined(Undefined):
        def __init__(self, name, parent=None):
            self.name = name
            self.parent = parent
            collected_variables.add(str(self))

        def __str__(self):
            if self.parent is not None:
                return f"{self.parent}.{self.name}"
            return self.name

        def __getattr__(self, name: str):
            return CollectUndefined(name, parent=self)

    return collected_variables, CollectUndefined


def find_all_vars(template_content):
    vars, undefined_cls = create_collector()
    env = Environment(undefined=undefined_cls)
    tpl = env.from_string(template_content)
    tpl.render({})  # empty so all variables are undefined
    return vars


def read_template(infile):
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Reading template {infile}")
        with open(infile, "r") as fh:
            return fh.read()
    except FileNotFoundError:
        logger.error(f"!!! File not found {infile}")
        exit(1)
    except PermissionError:
        logger.error(
            f"!!! You do not have permission to read {infile}. Please check permissions."
        )
        exit(1)
    except Exception as e:
        logger.error(f"!!! {e}")
        exit(1)


def write_file(file_data: str, output_path: str, file_name: str):
    logger = logging.getLogger(__name__)
    write_path = Path(output_path)
    try:
        # Create the output directory if it doesn't exist
        write_path.mkdir(parents=True, exist_ok=True)
        write_path = write_path / file_name

        with write_path.open("w") as f:
            f.write(file_data)

        return write_path
    except FileNotFoundError as e:
        logger.error(f"!!! Could not create file at {write_path}? - {e}")
        exit(1)

    except PermissionError as e:
        logger.error(f"!!! Insufficient permissions to write to file: {e}")
        exit(1)

    except Exception as e:
        logger.error(f"!!! UNHANDLED EXCEPTION {e}")
        exit(1)


def generate_template(recipe, template_path):
    logger = logging.getLogger(__name__)

    try:
        with open(recipe, "r") as fh:
            logger.info(f"Opened recipe {recipe}.")
            template = fh.read().strip()
            recipe_json = json.loads(template)
            logger.debug(
                f"Recipe loaded as json:\n {json.dumps(recipe_json, indent=2)}"
            )
    except FileNotFoundError as e:
        logger.error(f"!!! Could not read {recipe}: {e}")
        exit(1)

    except PermissionError as e:
        logger.error(f"!!! Insufficient permissions to read recipe: {e}")
        exit(1)

    except Exception as e:
        logger.error(f"!!! UNHANDLED EXCEPTION {e}")
        exit(1)

    logger.info("Concatenating templates into master template.")
    master_template = ""
    ingredients = recipe_json["recipe"]
    logger.debug(f"Templates found:\n {json.dumps(ingredients, indent=2)}")
    for template_directory in ingredients:
        logger.info(
            f"Starting {template_directory} scan in {template_path / template_directory}."
        )
        for template in ingredients[template_directory]:
            path = template_path / template_directory / template
            logger.debug(f"Found template at {path}")
            master_template += read_template(path)
            master_template += "\n"

    return master_template


def check_answers(generated:Dict[str,str], supplied:Dict[str,str]):
    
    missing = []
    for g_ans in generated:
        if(g_ans not in supplied):
            missing.append(g_ans)
        
    if len(missing) > 0:
        raise ValueError(f"Answers file is missing values for: {missing}.")

def generate_kickstart(generated_template: str, answers_file: str):
    logger = logging.getLogger(__name__)
    env = Environment()

    ks_template = env.from_string(generated_template)

    generated_answers = json.loads(generate_empty_answers(generated_template))
    with open(answers_file, "r") as fh:
        user_answers = json.loads(fh.read())
    try:
        check_answers(generated_answers, user_answers)
        ks_render = ks_template.render(user_answers)
        return ks_render
    except Exception as e:
        logger.error(f"!!! Unable to render file !!!")
        logger.error(f"{e=}")
        exit(1)


def generate_empty_answers(generated_template: str):
    set_vars = find_all_vars(generated_template)
    ret_dict = {}
    for var in set_vars:
        ret_dict[var] = ""

    return json.dumps(ret_dict, indent=2)


def set_log_level(logging_level):
    # For some reason setting the level in basicConfig fails?
    logging.getLogger(__name__).level = logging_level

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )


def main():
    base_path = Path().cwd()

    parser = argparse.ArgumentParser()
    # Required arguments
    subparser = parser.add_subparsers(
        help="Choose a command: generate or serve.", dest="command"
    )
    serve_parser = subparser.add_parser("serve", help="Start the Crispin API server")

    generate_parser = subparser.add_parser(
        "generate", help="Set options for generating answers, kickstarts, and ISOs."
    )
    generate_parser.add_argument(
        "-r", "--recipe", type=str, help="The path of the chosen recipe.", required=True
    )
    generate_parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Name of the generated kickstart or answer file.",
        required=True,
    )

    # If answers are being generated answers should not be supplied
    arg_group = generate_parser.add_mutually_exclusive_group()
    arg_group.add_argument(
        "-g",
        "--generate-answers",
        action="store_true",
        help="Generate a blank answer file for the given recipe",
    )
    arg_group.add_argument(
        "-a", "--answers", type=str, help="Path to json answers to fill in kickstart."
    )

    # Optional arguments
    generate_parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="(Optional default: $PWD) The output dir. If this directory does not exist an attempt to create it is made.",
        default=base_path,
    )
    generate_parser.add_argument(
        "-t",
        "--template-dir",
        type=str,
        help="(Optional) Directory holding the templates specified in the recipe.",
        default=None,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="(Optional) Enable verbose logging.",
        default=False,
    )
    parser.add_argument(
        "-vv",
        "--debug",
        action="store_true",
        help="(Optional) Enable debug logging.",
        default=False,
    )
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)
    if len(sys.argv) == 2:
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    match args.verbose:
        case True:
            set_log_level(logging.INFO)
        case False:
            set_log_level(logging.ERROR)

    match args.debug:
        case True:
            set_log_level(logging.DEBUG)

    logger = logging.getLogger(__name__)

    match args.template_dir:
        case None:
            template_path = Path(args.recipe).parents[1] / "templates"
        case _:
            logger.info(
                "Not using a cookbook! Tread with caution. See crispin README for details."
            )
            template_path = Path(args.template_path)

    ks_template = generate_template(args.recipe, template_path)

    match args.generate_answers:
        case True:
            generated_answers = generate_empty_answers(ks_template)
            abs_path = write_file(
                generated_answers, args.output_dir, args.name + ".json"
            )
            logger.info(f"Wrote answers for recipe {args.recipe} to {abs_path}.")
            print(f"Wrote answers for recipe {args.recipe} to {abs_path}.")
        case _:
            generated_ks = generate_kickstart(ks_template, args.answers)
            abs_path = write_file(generated_ks, args.output_dir, args.name + ".ks")
            logger.info(f"Wrote the kickstart for recipe {args.recipe} to {abs_path}.")
            print(f"Wrote the kickstart for recipe {args.recipe} to {abs_path}.")


if __name__ == "__main__":
    main()
