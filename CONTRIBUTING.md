# OpenAPI Pydantic Contribution Guide

We welcome all contributions!

## Issues

Questions, feature requests and bug reports are all welcome as issues. When raising a bug or
question, please include as much information as possible including the specific version you
are using.

## Pull Requests

It should be very simple to get started and open a pull request, however for anything non-trivial
please open an issue to discuss your intended change _before_ creating your PR. This avoids wasting
time by ensuring that your changes will be accepted with fewer revisions down the line!

### Local Development

A [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) configuration is provided in the repo to get your environment setup automatically. Alternatively you can install [tox](https://tox.wiki/en/latest/) and [poetry](https://python-poetry.org/) manually.

### Testing

Please ensure all changes have good test coverage and are formatted correctly. You can run the test
suite and linters using [tox](https://tox.wiki/en/latest/) - just run `tox` from the root of this
repo to run the checks. These will also be run automatically in CI once your PR is opened. Don't
worry about testing against every Ptyhon version - the CI action will do this for you!

### Tagging

When your PR is ready, please tag it with the appropriate tags: one of `feature`, `change`, `fix`,
as well as `breaking` if you've introduced backwards-incompatible changes to the public API or
behaviour.

## Review

We'll review your PR as soon as possible - either approving or requesting changes. Once the PR is
approved, it will be merged into main and cut into the next release.

## Releases

The release schedule is not set in stone and will depend on the number of changes in flight, but where possible we'll look to cut a release with your changes as soon as possible. Once a new version is tagged,
a package version is uploaded to PyPI automatically.
