#!/usr/bin/env python3.11

import argparse, json
import crypt
from jinja2 import Environment, meta, DebugUndefined
import tempfile

def read_template(infile):
    with open(infile, 'r') as fh:
        return fh.read()

def hash_pass(pass_str):
    return crypt.crypt(pass_str, crypt.mksalt(crypt.METHOD_SHA256))

def generate_template(meta_template):
    print("Generating jinja template from the meta-template.")
    with open(meta_template, 'r') as fh:
        template = fh.read().strip()
        recipe = json.loads(template)
        
    with tempfile.NamedTemporaryFile(mode='r+') as outfile:
        print(f"Opening temporary file for writing")
        
        for template_directory in recipe:
            for template in recipe[template_directory]:
                print(f"template: {template}")
                path = f"templates/{template_directory}/{template}"
                outfile.write(read_template(path))

        outfile.seek(0)
        return outfile.read()

def generate_kickstart(generated_template:str , answers_file:str, template_name:str):
    print("Generating kickstart from the meta-template jinja")
    # Grab env, set it to debug undefined variables so an exception can be raised
    env = Environment(undefined=DebugUndefined)
    ks_template = env.from_string(generated_template)


    with open(answers_file, 'r') as fh:
        answers_dict = json.loads(fh.read())

    # Render the document
    ks_render = ks_template.render(answers_dict)

    #Check rendering
    # https://stackoverflow.com/a/55699590
    ast = env.parse(ks_render)
    undef_vars = meta.find_undeclared_variables(ast)
    if(undef_vars):
        raise Exception(f"The following variables are undefined: {undef_vars!r}")
    

    with open(f"output/kickstarts/{template_name}.ks", "w") as f:
        f.write(ks_render)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--meta-template', type=str, help="The chosen meta-template.", required=True)
    parser.add_argument('-n', '--name', type=str, help="Name of the generated kickstart or answer file.", required=True)

    #If answers are being generated answers should not be supplied
    arg_group = parser.add_mutually_exclusive_group()
    arg_group.add_argument('-g', '--generate-answers', action='store_true', help="Generate a blank answer file for the given meta-template")
    arg_group.add_argument('-a', '--answers', type=str, help="json answers to fill in kickstart")

    args = parser.parse_args()
    if(args.generate_answers):
        print("NOT YET IMPLEMENTED")
        exit(0)

    ks_template = generate_template(args.meta_template)
    generate_kickstart(ks_template, args.answers, args.name)

if __name__ == "__main__":
    main()
