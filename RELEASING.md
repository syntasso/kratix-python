# Releasing `kratix-sdk`

The release process for this repository is almost entirely automated, consisting
of these steps:

1. **Run quality checks (unit tests and linting)** (automated)

Every PR and every merge to `main` will trigger the testing workflow. This
workflow checks for successful unit test runs and whether the linting and
formatting rules are being respected.

1. **Prepare the release PR** (automated)

`release-please` will prepare a release PR for this project after each each
successful run of the of the quality checks in the `main` branch.

1. **Merge the release PR** (manual)

A maintainer decided whether the release PR created by `release-please` should
be merged. If a release PR is merged, `release-please` will update the
[CHANGELOG](CHANGELOG.md) and create a new Github Release with notes.

1. **Publish repositories to PyPI** (automated)

When a release is created, the publish workflow will package the code onto a
new release and push this release as a new package on PyPI. If the package is
published successfully, it will publish the API documentation to the
[documentation website](https://syntasso.github.io/kratix-python/).

1. **Communicate the release** (manual)

After all artifacts are published, a human needs to:
- Share release notes on the relevant channels.
- Update downstream sample projects if they pin versions.
