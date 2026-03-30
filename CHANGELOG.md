# Changelog

All notable changes to `panorama_openedx_backend` are documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## Version 20.0.3 (2026-03-30)

- Pass the learner full name as `p.userFullName` in student dashboard embed URLs, using `userprofile.name` with fallback to `user.username`.

## Version 20.0.2 (2026-03-30)

- Pass the numeric Django `user.id` as the `p.userId` learner parameter in student dashboard embed URLs.
- Remove the legacy `AI_AUTHOR` role option and migrate existing assignments to `AUTHOR`.
- Convert the project changelog from reStructuredText to Markdown and update packaging and docs references accordingly.

## 20.0.1 - 2026-03-24

- Pass `userId` and `lms` learner parameters to student dashboard embed URLs in custom mode.
- Update GitHub Actions workflows to Node 20 compatible action and reusable workflow versions.

## 20.0.0 - 2026-03-16

- Align packaging, tox, CI, and pinned requirements with the Open edX Teak Python 3.11 baseline.

## 16.0.15 - 2026-03-04

- Return the default user ARN when the configured ARN is missing.
- Make the `UserAccessConfiguration` ARN field optional.
- Use a user lookup widget in the Django admin for the user access configuration.
- Update tox to test against Django >= 4.2.

## 16.0.14 - 2026-03-04

- Take the default user ARN if not specified in the user access configuration (valid for custom mode only).

## 16.0.13 - 2025-12-02

- Fix dashboard views for author users.

## 16.0.12 - 2024-08-09

- fix: Support `STUDENT` role.

## 16.0.11 - 2024-08-09

- fix: return student dashboards if the user is not listed in the access configuration and the student view is enabled.

## 16.0.10 - 2024-08-05

- fix: Fix bug when retrieving the default user ARN from the settings.
- fix: Fix allowed domain when generating embed URL.

## 16.0.9 - 2024-06-11

- Manage nonexistent user access configuration.

## 16.0.8 - 2024-06-11

- Show "available to students" field in the "dashboard type"'s admin list.

## 16.0.7 - 2024-06-10

- Increase timeout to 60 secs in API calls.

## 16.0.6 - 2024-06-10

- Add user role (`dashboard_function`) to the signed requests to the API.
  This allows for Author, AI and Student views in SaaS modes.

## 16.0.5 - 2024-06-08

- Fix SigV4 calls.

## 16.0.4 - 2024-06-06

- Return `STUDENT` user role in SAAS and CUSTOM modes.
- Return `PANORAMA_DEFAULT_USER_ARN` if there is no user access configuration.

## 16.0.3 - 2024-06-05

- Initial release.
