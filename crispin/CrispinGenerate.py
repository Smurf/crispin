import json
from pathlib import Path
from jinja2 import Environment, Undefined
from typing import Dict
from ._util import logger, dict_to_dot, dot_to_dict
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

    try:
        logger.info(f"Reading template {infile}")
        with open(infile, "r") as fh:
            return fh.read()
    except FileNotFoundError:
        logger.error(f"!!! File not found {infile}")
        raise
    except PermissionError:
        logger.error(
            f"!!! You do not have permission to read {infile}. Please check permissions."
        )
        raise
    except Exception as e:
        logger.error(f"!!! {e}")
        raise


def write_file(file_data: str, output_path: str, file_name: str):
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
        raise
    except PermissionError as e:
        logger.error(f"!!! Insufficient permissions to write to file: {e}")
        raise
    except Exception as e:
        logger.error(f"!!! UNHANDLED EXCEPTION {e}")
        raise


def generate_template(recipe, template_path, ks_logging: bool = False):

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
        raise
    except PermissionError as e:
        logger.error(f"!!! Insufficient permissions to read recipe: {e}")
        raise
    except Exception as e:
        logger.error(f"!!! UNHANDLED EXCEPTION {e}")
        raise

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
            logger.debug(f"Searching for {template} at {path}")
            current_template = read_template(path)
            if(ks_logging):
                split_template = current_template.splitlines()
                for line in split_template:
                    if(line.startswith("%pre") or line.startswith("%post")):
                        line += f" --log=/tmp/crispin-{template}"
                    master_template += line+"\n"
                master_template += "\n"
            else:
                master_template += current_template
                master_template += "\n"

    return master_template


def check_answers(generated:Dict[str,str], supplied:Dict[str,str]):
    
    missing = []
    supplied = dict_to_dot(supplied)
    for g_ans in generated:
        if(g_ans not in supplied):
            missing.append(g_ans)
    if len(missing) > 0:
        raise ValueError(f"Answers file is missing values for: {missing}.")

def generate_kickstart(generated_template: str, answers_file: str):
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
        raise


def generate_kickstart_from_answers_dict(generated_template: str, answers: dict):
    env = Environment()

    ks_template = env.from_string(generated_template)

    generated_answers = json.loads(generate_empty_answers(generated_template))
    try:
        check_answers(generated_answers, answers)
        ks_render = ks_template.render(answers)
        return ks_render, None
    except ValueError as e:
        logger.error(f"!!! Answer check failed: {e}")
        return None, e
    except Exception as e:
        logger.error(f"!!! Unable to render file !!!")
        logger.error(f"{e=}")
        return None, e

def generate_empty_answers(generated_template: str):
    set_vars = find_all_vars(generated_template)
    ret_dict = dot_to_dict(list(set_vars))

    return json.dumps(ret_dict, indent=2)
