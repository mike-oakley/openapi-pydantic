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

A [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) configuration is provided in the repo to get your environment setup automatically.

If devcontainers aren't your speed, you can manually setup your environment by installing `uv` and
then running `uv sync --all-groups`.

### Testing

Please ensure all changes have good test coverage. We use [pytest](https://docs.pytest.org/en/latest/) for testing, and [coverage](https://coverage.readthedocs.io/en/latest/) for measuring code coverage.

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
