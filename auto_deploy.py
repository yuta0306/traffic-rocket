import subprocess

def git_flow(repo: str, username: str, password: str, name: str, email: str, branch: str) -> None:
    res = subprocess.run(
        ['git', 'config', '--global', 'user.name', name]
    )
    res = subprocess.run(
        ['git', 'config', '--global', 'user.email', email]
    )
    res = subprocess.run(
        ['git', 'init']
    )
    res = subprocess.run(
        ['git', 'add', '.']
    )
    res = subprocess.run(
        ['git', 'commit', '-m', '"save json"']
    ) 
    res = subprocess.run(
        ['git', 'remote', 'add', 'origin', f'https://{username}:{password}@github.com/{username}/{repo}']
    )
    res = subprocess.run(
        ['git', 'push', '--force', 'origin', branch]
    )  
    