# Development

## Pre-commit actions

Before each commit developer should run

```bash
make fix
```

This will reformat code to not be longer than 100 symbols on the line and other things that `black` requres. This will also resort imports and regenerate schemas for YAML configuration files.

```bash
make check
```

This will run style checks, typing checks and all of the unit tests.

## Miscellaneous

```bash
make build-*
```

Depending on the glob this will build docs or the project itself. See [Makefile](https://github.com/Kraysent/OMTool/blob/main/Makefile) for specifics. 

## Automated testing

This project has [automated testing](https://www.atlassian.com/continuous-delivery/software-testing/automated-testing) enabled using [Github Actions](https://github.com/features/actions). 

### Dockerfile

Since Github Actions work as a container (kinda like virtual machine) that runs specific commands, it is faster to prepare container with all of the dependencies already installed and only run commands themself. This is exactly what Dockerfile does: prepare container which can be installed and then pushed to docker repository ([Docker Hub](https://hub.docker.com/)). Then Github Actions download this image and run all of the tests inside it. Dockerfile is located [here](https://github.com/Kraysent/OMTool/blob/main/package/Dockerfile).

### Tests

There are 4 types of tests: 

* **Building**: check if pip package can be built and upload result of the build into artefacts.
* **Linting**: check if all of the codestyle is correct across all of the files.
* **Statistics**: not really a check, just spits out some statistics about the project.
* **Testing**: Run all of the tests with `unittest`.

Also there is action for documentation building but it is handled by ReadTheDocs.
