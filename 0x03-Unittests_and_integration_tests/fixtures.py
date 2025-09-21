#!/usr/bin/env python3
"""
Test fixtures for integration tests
"""

# Organization payload fixture
org_payload = {
    "login": "google",
    "id": 1342004,
    "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
    "url": "https://api.github.com/orgs/google",
    "repos_url": "https://api.github.com/orgs/google/repos",
    "events_url": "https://api.github.com/orgs/google/events",
    "hooks_url": "https://api.github.com/orgs/google/hooks",
    "issues_url": "https://api.github.com/orgs/google/issues",
    "members_url": "https://api.github.com/orgs/google/members{/member}",
    "public_members_url": "https://api.github.com/orgs/google/public_members{/member}",
    "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
    "description": "Google ❤️ Open Source",
}

# Repositories payload fixture
repos_payload = [
    {
        "id": 7697149,
        "node_id": "MDEwOlJlcG9zaXRvcnk3Njk3MTQ5",
        "name": "episodes.dart",
        "full_name": "google/episodes.dart",
        "private": False,
        "owner": {
            "login": "google",
            "id": 1342004,
        },
        "html_url": "https://github.com/google/episodes.dart",
        "description": "A framework for timing performance of web apps.",
        "fork": False,
        "url": "https://api.github.com/repos/google/episodes.dart",
        "created_at": "2013-01-19T00:31:37Z",
        "updated_at": "2019-09-23T11:53:58Z",
        "pushed_at": "2014-10-09T21:39:33Z",
        "git_url": "git://github.com/google/episodes.dart.git",
        "ssh_url": "git@github.com:google/episodes.dart.git",
        "clone_url": "https://github.com/google/episodes.dart.git",
        "size": 191,
        "stargazers_count": 12,
        "watchers_count": 12,
        "language": "Dart",
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_pages": False,
        "forks_count": 22,
        "archived": False,
        "disabled": False,
        "open_issues_count": 0,
        "license": {
            "key": "bsd-3-clause",
            "name": "BSD 3-Clause \"New\" or \"Revised\" License",
            "spdx_id": "BSD-3-Clause",
            "url": "https://api.github.com/licenses/bsd-3-clause",
            "node_id": "MDc6TGljZW5zZW9ic2Q="
        },
        "forks": 22,
        "open_issues": 0,
        "watchers": 12,
        "default_branch": "master",
    },
    {
        "id": 8566972,
        "node_id": "MDEwOlJlcG9zaXRvcnk4NTY2OTcy",
        "name": "kratu",
        "full_name": "google/kratu",
        "private": False,
        "owner": {
            "login": "google",
            "id": 1342004,
        },
        "html_url": "https://github.com/google/kratu",
        "description": "An HTML5 visualization library for web apps.",
        "fork": False,
        "url": "https://api.github.com/repos/google/kratu",
        "created_at": "2013-03-04T22:52:33Z",
        "updated_at": "2019-11-15T22:22:16Z",
        "pushed_at": "2013-06-05T16:25:31Z",
        "git_url": "git://github.com/google/kratu.git",
        "ssh_url": "git@github.com:google/kratu.git",
        "clone_url": "https://github.com/google/kratu.git",
        "size": 248,
        "stargazers_count": 32,
        "watchers_count": 32,
        "language": "JavaScript",
        "has_issues": True,
        "has_projects": True,
        "has_wiki": True,
        "has_pages": False,
        "forks_count": 11,
        "archived": False,
        "disabled": False,
        "open_issues_count": 0,
        "license": {
            "key": "apache-2.0",
            "name": "Apache License 2.0",
            "spdx_id": "Apache-2.0",
            "url": "https://api.github.com/licenses/apache-2.0",
            "node_id": "MDc6TGljZW5zZW9wYWNoZS0yLjA="
        },
        "forks": 11,
        "open_issues": 0,
        "watchers": 32,
        "default_branch": "master",
    },
]

# Expected repositories (names only)
expected_repos = ["episodes.dart", "kratu"]

# Apache 2.0 licensed repositories
apache2_repos = ["kratu"]