# crispin

> **NOTE:** This project is in very eary alpha. None of this is stable and should never be used by any sane person.

Crispin is an easy to use meta-template engine for creating kickstarts that can be used to automate the install of RHEL and RHEL-alike Linux distributions.


# Install

```
$ ./devenv.sh
$ ./rebuild.sh

# If you wish to install to your user python bin run rebuild.sh outside of the venv created by devenv.sh
```

# Usage:

Crispin has two modes: generate and serve.

> **NOTE:** For a high level overview of crispin and the terminology used here see the [How it works](#how-it-works) section.

## Generate:

Generate can create both kickstarts from recipes and answer files from recipes.


```
$ crispin generate
usage: crispin generate [-h] -r RECIPE -n NAME [-l] [-g | -a ANSWERS] [-o OUTPUT_DIR] [-t TEMPLATE_DIR]

options:
  -h, --help            show this help message and exit
  -r RECIPE, --recipe RECIPE
                        The path of the chosen recipe.
  -n NAME, --name NAME  Name of the generated kickstart or answer file.
  -l, --logging         (Optional) Enables logging in the kickstarted machine's /tmp/ directory. All pre and post
                        scripts will log to /tmp/.
  -g, --generate-answers
                        Generate a blank answer file for the given recipe
  -a ANSWERS, --answers ANSWERS
                        Path to json answers to fill in kickstart.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        (Optional default: $PWD) The output dir. If this directory does not exist an attempt to
                        create it is made.
  -t TEMPLATE_DIR, --template-dir TEMPLATE_DIR
```

### Generate a blank answers file

> **NOTE:** These examples are using the [crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) repository as an example.

crispin can generate a blank answers file for you. For more information on what an answers file is see the [answers file](#answers-file) section for more information.
```
crispin -r fedora/recipes/f38-minimal.json -n my-answers -g
```

### Generate a kickstart file

> **NOTE:** These examples are using the [crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) repository as an example.

```
crispin -r fedora/recipes/f38-minimal.json -n f38-my-answers -a my-answers.json
```

## Serve

The serve command starts an HTTP server that can be used to generate kickstarts on demand.

```
$ crispin serve -h
usage: crispin serve [-h] -c COOKBOOK_DIR -i IPXE_DIR

options:
  -h, --help            show this help message and exit
  -c COOKBOOK_DIR, --cookbook-dir COOKBOOK_DIR
                        The path to the cookbook directory.
  -i IPXE_DIR, --ipxe-dir IPXE_DIR
                        The path to the directory containing vmlinuz and
                        initrd.img.
```

### API

The server exposes a simple API for generating kickstarts.

#### GET /crispin/get/<answer_name>

This endpoint generates a kickstart using a pre-existing answers file from the cookbook. The `answer_name` in the URL should correspond to the name of an answers file (without the `.json` extension) in the `answers` directory of the cookbook.

Example:

```
curl http://localhost:9000/crispin/get/minimal-desktop-example
```

#### POST /crispin/get/<recipe_name>

This endpoint generates a kickstart using the JSON answers provided in the request body. The `recipe_name` in the URL should correspond to the name of a recipe file (without the `.json` extension) in the `recipes` directory of the cookbook.

Example:

```
curl -X POST -d '{"hostname": "my-new-host"}' http://localhost:9000/crispin/get/minimal-desktop
```


## Debug Mode

Crispin has a verbose and debug mode.

```
usage: crispin [-h] [-v] [-vv] {serve,generate} ...

positional arguments:
  {serve,generate}  Choose a command: generate or serve.
    serve           Start the Crispin API server
    generate        Set options for generating answers, kickstarts, and ISOs.

options:
  -h, --help        show this help message and exit
  -v, --verbose     (Optional) Enable verbose logging.
  -vv, --debug      (Optional) Enable debug logging.
```

At the moment these options **must** come before the `generate` and `serve` options.

# How it works

Using crispin requires three things: kickstart templates, a recipe, and answers. These three things make a **cookbook**.

> **High level overview:** Crispin takes a JSON file that lists directories and files within in order, concatenates them to create a valid kickstart, and finally takes an answer file to fill in variables in the concatenated template.


## Cookbooks

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

## Recipes

Recipes are a JSON file. The recipe reflects the folder structure of the `template-dir`. The files in the directories are Jinja2 templates. **These files are concatinated in the order that they are listed.**

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
[crispin-cookbooks](https://github.com/Smurf/crispin-cookbooks) is under active development and contains an example recipe for my own Fedora 43 install.

## Answers File

The answers file contains the variables to fill in the Jinja2 templates listed in the recipe.

Blank answer files [can be automatically generated](#generate-a-blank-answers-file) and it is highly recommended to do so.

```
{
    "value1":"value1",
    "value2":"value2",
    "value3":["arr1", "arr2"]
}
```

## TODO:
- [X] Move to f43
- [ ] Make readme more comprehensible
- [ ] Break generation of KS and Answers into its own file.
- [ ] Remove global var ks_logging

### LONG TERM:
- [ ] Work to generate ISOs
- [ ] Work to Host ISOs
