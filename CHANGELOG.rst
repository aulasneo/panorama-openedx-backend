Change Log
##########

..
   All enhancements and patches to panorama_openedx_backend will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

Unreleased
****************************

* fix: return student dashboards if the user is not listed in the access
  configuration and the student view is enabled.

Version 16.0.10 (2024-08-05)
****************************

* fix: Fix bug when retrieving the default user arn from the settings.
* fix: Fix allowed domain when generating embed url

Version 16.0.9 (2024-06-11)
***************************

* Manage nonexistent user access configuration

Version 16.0.8 (2024-06-11)
***************************

* Show "available to students" field in the "dashboard type"'s admin list.

Version 16.0.7 (2024-06-10)
***************************

* Increase timeout to 60 secs in api calls

Version 16.0.6 (2024-06-10)
***************************

* Add user role (dashboard_function) to the signed requests to the api.
  This allows for Author, AI and Student views in SaaS modes.

Version 16.0.5 (2024-06-08)
***************************

* Fix SigV4 calls

Version 16.0.4 (2024-06-06)
***************************

* Return "STUDENT" user role in SAAS and CUSTOM modes.
* Return PANORAMA_DEFAULT_USER_ARN if there is no user access configuration.

Version 16.0.3 (2024-06-05)
***************************

* Initial release
