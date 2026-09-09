# panorama-openedx-backend

This is a Django app for Open edX that implements all backend functions needed
by the Panorama MFE to work.

[![PyPI](https://img.shields.io/pypi/v/panorama-openedx-backend.svg)](https://pypi.python.org/pypi/panorama-openedx-backend/)
[![CI](https://github.com/aulasneo/panorama-openedx-backend/workflows/Python%20CI/badge.svg?branch=main)](https://github.com/aulasneo/panorama-openedx-backend/actions)
[![Documentation](https://readthedocs.org/projects/panorama-openedx-backend/badge/?version=latest)](https://docs.openedx.org/projects/panorama-openedx-backend)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/panorama-openedx-backend.svg)](https://pypi.python.org/pypi/panorama-openedx-backend/)
[![License](https://img.shields.io/github/license/aulasneo/panorama-openedx-backend.svg)](https://github.com/aulasneo/panorama-openedx-backend/blob/main/LICENSE.txt)
![status-badge](https://img.shields.io/badge/Status-Maintained-brightgreen)

## Purpose

Django app that implements backend functions for Panorama MFE.

[Panorama](https://aulasneo.com/open-edx-analytics/) is the analytics system
for Open edX and more.

This code is not intended to be installed by itself. To install Panorama in
your Open edX instance, install the
[Panorama Tutor plugin](https://github.com/aulasneo/tutor-contrib-panorama).

## Getting Started With Development

The Tutor 22 / Verawood target uses Python 3.12 and Django 5.2. The checked
compatibility reference is edx-platform `release/verawood.1`, commit
`9e67d1429d5ab49a36fb9881a26457efeee0bb89`. The local platform checkout used for
source checks was `release/verawood` at `259473c5dfd1c82eac5e6c4d14bf6095cb25824d`;
these are different commits, with matching shared dependency pins.
[requirements/verawood.txt](requirements/verawood.txt) records the shared pins
from the exact release. They are compatibility baselines, not a claim that
they are the newest security fixes. Review newer fixes with the platform
maintainer; do not upgrade the LMS SDK independently or install development
locks into the LMS. Package requirements admit Verawood's AWS SDK without
the old forced downgrade to 1.40.62.

Use an isolated Python 3.12 environment:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r requirements/test.txt -e .
.venv/bin/pytest
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/pip check
```

To refresh the dependent locks together, run `pip-compile --constraint
requirements/verawood.txt --output-file requirements/NAME.txt
requirements/NAME.in` for `base`, `test`, `quality`, then `dev`, in that order.
Recheck the release constraints whenever the target platform commit changes.

## Verawood access and migration checks

Dashboard embedding now enforces the existing access endpoint's policy:
DEMO/FREE allow superusers; SAAS/CUSTOM allow explicit dashboard grants,
superusers, or authenticated learners when student view is enabled. Console
embedding additionally requires the explicit `AUTHOR` role, including for
superusers. Both embedding endpoints require HTTPS. Authentication failures
retain DRF's configured session/JWT behavior; denied grants return 403 before
any provider request. Provider timeouts return 504; malformed JSON, SDK and
connection failures return 502; missing configuration returns 400. Upstream
401/403 remain access errors, without leaking response bodies or credentials.
Successful response envelopes are unchanged.

Apply committed migration `0008_normalize_reader_role` with `migrate` (never
generate migrations during initialization). It changes only historical
`Reader` values to `READER` and updates the default. Inspect existing roles
before upgrading with `UserAccessConfiguration.objects.values('role').annotate(
count=Count('id'))` in the LMS shell (import `Count` from `django.db.models`).
Other unexpected spellings are left for explicit operator review. Reversing
this migration retains normalized data because the original spelling cannot
be reconstructed safely.

Student URL parameters `userId` and `lms` are client-controlled display
filters, **not authorization**. Before enabling student view, verify
dataset-side learner/tenant isolation with two students and tampered fragment
parameters. This repository cannot establish isolation for deployed datasets.

Local regression tests use SQLite and mocked providers. Staging still needs
the final Verawood LMS image's plugin discovery, URL inclusion, settings,
`migrate`, `pip check`, session/JWT login/expiry, real profile lookup, and
registered-user dashboard/console embedding. No external services are needed
for the local tests, and no local test proves production QuickSight isolation.

Please see the Open edX documentation for
[guidance on Python development](https://docs.openedx.org/en/latest/developers/how-tos/get-ready-for-python-dev.html)
in this repo.

## Deploying

To deploy for development, add a simple Tutor plugin with:

```python
from tutor import hooks as tutor_hooks

tutor_hooks.Filters.MOUNTED_DIRECTORIES.add_item(("openedx", "panorama-openedx-backend"))
```

Then use `tutor mounts` to mount your local copy of the repo.

## Getting Help

### Contact

Contact us at <https://aulasneo.com> if you need support.

## License

The code in this repository is licensed under the Not open source unless
otherwise noted.

Please see `LICENSE.txt` for details.

## Contributing

Contributions are very welcome.

This project is currently accepting all types of contributions, bug fixes,
security fixes, maintenance work, or new features. However, please make sure to
have a discussion about your new feature idea with the maintainers prior to
beginning development to maximize the chances of your change being accepted.
You can start a conversation by creating a new issue on this repo summarizing
your idea.

## Reporting Security Issues

Please do not report security issues in public. Please email
<info@aulasneo.com>.
