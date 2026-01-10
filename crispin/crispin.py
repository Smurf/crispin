#!/usr/bin/env python3

import argparse, logging, sys
from pathlib import Path
from crispin.CrispinGenerate import (
    generate_template,
    generate_empty_answers,
    write_file,
    generate_kickstart,
)
from crispin._util import logger, set_log_level

def main():
    base_path = Path().cwd()
    parser = argparse.ArgumentParser()
    # Required arguments
    subparser = parser.add_subparsers(
        help="Choose a command: generate or serve.", dest="command"
    )
    serve_parser = subparser.add_parser("serve", help="Start the Crispin API server")
    serve_parser.add_argument(
        "-c",
        "--cookbook-dir",
        type=str,
        help="The path to the cookbook directory.",
        required=True,
    )
    serve_parser.add_argument(
        "-i",
        "--ipxe-dir",
        type=str,
        help="The path to the directory containing vmlinuz and initrd.img.",
        required=True,
    )

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
    generate_parser.add_argument(
        "-l",
        "--logging",
        action="store_true",
        help="(Optional) Enables logging in the kickstarted machine's /tmp/ directory. All pre and post scripts will log to /tmp/.",
        default=False,
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

    # Check for help printing
    if len(sys.argv) < 2:
        parser.print_help()
        exit(1)
    if len(sys.argv) == 2 and sys.argv[1] == 'generate':
        generate_parser.print_help()
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
    

    if args.command == 'serve':
        from crispin.CrispinServe import run
        run(cookbook_dir=args.cookbook_dir, ipxe_dir=args.ipxe_dir)
        sys.exit(0)
    match args.template_dir:
        case None:
            template_path = Path(args.recipe).parents[1] / "templates"
        case _:
            logger.info(
                "Not using a cookbook! Tread with caution. See crispin README for details."
            )
            template_path = Path(args.template_path)

    try:
        ks_template = generate_template(args.recipe, template_path, args.logging)

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
    except Exception as e:
        logger.error(f"!!! {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
