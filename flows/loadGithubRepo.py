from prefect_github.repository import GitHubRepository

github_repository_block = GitHubRepository.load("dp-off-gitrepo")

print(github_repository_block)