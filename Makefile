build:
	poerty build

tag:
	poetry version $(version)
	git add pyproject.toml
	git commit -m "Bump version to $(version)"
	git push origin master
	git tag -a $(version) -m "Bump version to $(version)"
	git push origin $(version)