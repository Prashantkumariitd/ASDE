import requests
from ...core.settings import Settings

def create_private_repository(name, description):
    token = Settings.github_provisioner_token

    if not token:
        raise RuntimeError("GitHub provisioner token missing")

    response = requests.post(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        json={
            "name": name,
            "description": description,
            "private": True,
            "auto_init": True
        },
        timeout=30
    )

    if response.status_code == 422:
        raise RuntimeError(
            "Repository already exists or name is invalid. "
            "Check existing repositories before creating another."
        )

    response.raise_for_status()

    data = response.json()

    return {
        "full_name": data["full_name"],
        "url": data["html_url"],
        "private": data["private"]
    }