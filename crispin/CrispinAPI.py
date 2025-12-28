import json
from pathlib import Path
from crispin.CrispinGenerate import generate_template, generate_kickstart, generate_kickstart_from_answers_dict

def get_kickstart(answer_name, cookbook_dir):
    """
    Generates a kickstart file using a pre-existing answers file.
    """
    cookbook_dir = Path(cookbook_dir)
    answers_dir = cookbook_dir / "answers"
    answer_file = answers_dir / (answer_name + ".json")

    if not answer_file.exists():
        raise FileNotFoundError(f"Answer file not found at {answer_file}")

    with open(answer_file, "r") as f:
        answers = json.load(f)

    recipe_name = answers.get("recipe")
    if not recipe_name:
        raise ValueError("Recipe not specified in answers file")

    recipe_file = cookbook_dir / "recipes" / (recipe_name + ".json")
    if not recipe_file.exists():
        raise FileNotFoundError(f"Recipe file not found at {recipe_file}")

    template_dir = cookbook_dir / "templates"
    generated_template = generate_template(recipe_file, template_dir)
    kickstart = generate_kickstart(generated_template, str(answer_file))

    return kickstart

def post_kickstart(recipe_name, answers, cookbook_dir):
    """
    Generates a kickstart file using the answers provided in the POST request body.
    """
    cookbook_dir = Path(cookbook_dir)
    recipe_file = cookbook_dir / "recipes" / (recipe_name + ".json")

    if not recipe_file.exists():
        raise FileNotFoundError(f"Recipe file not found at {recipe_file}")

    try:
        answers_dict = json.loads(answers)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON in request body")

    template_dir = cookbook_dir / "templates"
    generated_template = generate_template(recipe_file, template_dir)
    kickstart, error = generate_kickstart_from_answers_dict(generated_template, answers_dict)

    if error:
        raise ValueError(error)

    return kickstart
