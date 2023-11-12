# Crispin

> **NOTE:** This project is in very eary alpha. Some of the features do not work yet.

Crispin is an easy to use meta-template engine for creating kickstarts and ISO files that can be used to install the operating system RHEL based computers.

## Install

Simply run the install script to setup the venv and install dependencies.

```
$ ./install.sh
```

## Usage:

> **NOTE:** Currently Crispin only allows generating kickstart files. Creating and serving ISOs are on the todo.

Once installed a meta-template and answers file must be created. This repository has a sample meta-template and answers file.

```
$ ./crispin.py -t recipes/f38-minimal.json -a answers/answers.example.json -n test-kickstart
$ cat output/kickstarts/test-kickstart.ks
```

## TODO:

- [ ] Verify example kickstart generated works
- [ ] Implement proper logging
- [ ] Implement generation of blank answer files based on provided meta-template
- [ ] Work to generate ISOs
- [ ] Work to Host ISOs
- [ ] Create REST API to dynamically generate kickstarts and ISOs
