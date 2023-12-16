#!/usr/bin/env python3

import argparse, json, logging, sys
from pathlib import Path
import crypt
from jinja2 import Environment, Undefined
import tempfile

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


def hash_pass(pass_str):
    return crypt.crypt(pass_str, crypt.mksalt(crypt.METHOD_SHA256))


def generate_template(recipe, template_path):
    logger = logging.getLogger(__name__)

    try:
        with open(recipe, "r") as fh:
            logger.info(f"Opened recipe {recipe}.")
            template = fh.read().strip()
            recipe_json = json.loads(template)
            logger.info(f"Recipe loaded as json:\n {json.dumps(recipe_json, indent=2)}")
    except FileNotFoundError as e:
        logger.error(f"!!! Could not create read {recipe}: {e}")
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
    logger.info(f"Templates found:\n {json.dumps(ingredients, indent=2)}")
    for template_directory in ingredients:
        logger.info(f"Starting {template_directory} scan in {template_path / template_directory}.")
        for template in ingredients[template_directory]:
            path = template_path / template_directory / template
            logger.info(f"Found template at {path}")
            master_template += read_template(path)
            master_template += "\n"

    return master_template


def generate_kickstart(generated_template: str, answers_file: str):
    logger = logging.getLogger(__name__)
    env = Environment()

    ks_template = env.from_string(generated_template)

    with open(answers_file, "r") as fh:
        answers_dict = json.loads(fh.read())

    try:
        ks_render = ks_template.render(answers_dict)
        return ks_render
    except Exception as e:
        logger.error(f"!!! Unable to render file due to {e}")
        exit(1)


def generate_empty_answers(generated_template: str):
    set_vars = find_all_vars(generated_template)
    ret_dict = {}
    for var in set_vars:
        ret_dict[var] = ""

    return json.dumps(ret_dict, indent=2)


def main():
    base_path = Path().cwd()

    parser = argparse.ArgumentParser()
    # Required arguments
    parser.add_argument(
        "-r", "--recipe", type=str, help="The path of the chosen recipe.", required=True
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Name of the generated kickstart or answer file.",
        required=True,
    )

    # If answers are being generated answers should not be supplied
    arg_group = parser.add_mutually_exclusive_group()
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
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="(Optional default: $PWD) The output dir. If this directory does not exist an attempt to create it is made.",
        default=base_path,
    )
    parser.add_argument(
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
    
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)

    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
    else:
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )

    logger = logging.getLogger(__name__)

    if args.template_dir is None:
        template_path = Path(args.recipe).parents[1] / "templates"
    else:
        logger.info("Not using a cookbook! Tread with caution. See crispin README for details.")
        template_path = Path(args.template_path)

    
    ks_template = generate_template(args.recipe, template_path)
    if args.generate_answers:
        generated_answers = generate_empty_answers(ks_template)
        abs_path = write_file(generated_answers, args.output_dir, args.name + ".json")
        logger.info(f"Wrote answers for recipe {args.recipe} to {abs_path}.")
        print(f"Wrote answers for recipe {args.recipe} to {abs_path}.")
    else:
        generated_ks = generate_kickstart(ks_template, args.answers)
        abs_path = write_file(generated_ks, args.output_dir, args.name + ".ks")
        logger.info(f"Wrote the kickstart for recipe {args.recipe} to {abs_path}.")
        print(f"Wrote the kickstart for recipe {args.recipe} to {abs_path}.")


if __name__ == "__main__":
    main()
