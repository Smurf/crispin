# crispin

> **NOTE:** This project is in very eary alpha. Some of the features do not work yet.

Crispin is an easy to use meta-template engine for creating kickstarts that can be used to automate the install of RHEL and RHEL-alike Linux distributions.


## Install

```
$ ./devenv.sh
$ ./rebuild.sh

# If you wish to install to your user python bin run rebuild.sh outside of the venv created by devenv.sh
```

## Usage:
```
usage: crispin [-h] -r RECIPE -n NAME [-g | -a ANSWERS] [-o OUTPUT_DIR] [-t TEMPLATE_DIR] [-v]

options:
  -h, --help            show this help message and exit
  -r RECIPE, --recipe RECIPE
                        The path of the chosen recipe.
  -n NAME, --name NAME  Name of the generated kickstart or answer file.
  -g, --generate-answers
                        Generate a blank answer file for the given recipe
  -a ANSWERS, --answers ANSWERS
                        Path to json answers to fill in kickstart.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        (Optional default: $PWD) The output dir. If this directory does not exist an attempt to
                        create it is made.
  -t TEMPLATE_DIR, --template-dir TEMPLATE_DIR
                        (Optional) Directory holding the templates specified in the recipe.
  -v, --verbose         (Optional) Enable verbose logging.
```

#### Generate a blank answers file

> **NOTE:** These examples are using the [crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) repository as an example.

crispin can generate a blank answers file for you. For more information on what an answers file is see the [answers file](#answers_file) section for more information.
```
crispin -r fedora/recipes/f38-minimal.json -n my-answers -g
```

#### Generate a kickstart file

> **NOTE:** These examples are using the [crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) repository as an example.

```
crispin -r fedora/recipes/f38-minimal.json -n f38 -a fedora/answers/answers.example.json
```

## How it works

Using crispin requires three things: kickstart templates, a recipe, and answers. These three things make a **cookbook**.

> **High level overview:** Crispin takes a JSON file that lists directories and files within in order, concatenates them to create a valid kickstart, and finally takes an answer file to fill in variables in the concatenated template.


### Cookbooks

A set of answers, recipes, and templates can be considered a **cookbook**. Each cookbook should be self contained and not reference other cookbooks.

```
├── my-cookbook
│   ├── answers
│   │   └── my-anwers.json
│   ├── recipes
│   │   └── my-recipe.json
│   └── templates
│       ├── folder1
│       │   └── part1.ks
│       ├── folder2
│       │   └── part2.ks
│       ├── folder3
│       │   ├── part3.ks
```

### Recipes

Recipes are a JSON file. The recipe reflects the folder structure of the `template-dir`. The files in the directories are Jinja2 templates.

> **NOTE:** This `template-dir` can be defined at  usage time. See [usage](#Usage) for details. This is **not recommended**.

```
{    
    "name": "My first recipe!"
    "recipe": {    
        "folder1": ["part1.ks"],
        "folder2": ["part2.ks"],
        "folder3": ["part3.ks"],
    }    
}
```
[crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) is under active development and contains an example recipe for my own Fedora 38 install.

### Answers File

The answers file contains the variables to fill in the Jinja2 templates listed in the recipe.

Blank answer files [can be automatically generated](#creating_a_blank_answers_file) and it is highly recommended to do so.

```
{
    "value1":"value1",
    "value2":"value2",
    "value3":["arr1", "arr2"]
}
```

## TODO:

- [ ] Work to generate ISOs
- [ ] Work to Host ISOs
- [ ] Create REST API to dynamically generate kickstarts and ISOs
