# teleapp Release Flow

This project is released from GitHub tags. It does not require PyPI.

## Recommended flow

1. Update the version in `pyproject.toml`.
2. Run local verification.
3. Commit the release changes.
4. Create a Git tag like `v0.1.0`.
5. Push the branch and the tag to GitHub.
6. GitHub Actions builds the wheel and source archive, then attaches them to a GitHub Release.

## Local verification

Run tests:

```powershell
python -m unittest discover -s tests -v
```

Build artifacts:

```powershell
build_teleapp.bat
```

Optional install check in a fresh venv:

```powershell
python -m venv .venv-release-check
.venv-release-check\Scripts\pip install .\dist\teleapp-0.1.0-py3-none-any.whl
.venv-release-check\Scripts\teleapp init sample_app
```

## Tagging

Example:

```powershell
git add pyproject.toml README.md RELEASE.md .github/workflows/release.yml
git commit -m "Release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

If the GitHub repo default branch is not `main`, push the correct branch name instead.

## Installing a release

From a Git tag:

```powershell
python -m venv .venv
.venv\Scripts\pip install "git+https://github.com/kevincsl/teleapp.git@v0.1.0"
```

From GitHub release assets after downloading the wheel:

```powershell
python -m venv .venv
.venv\Scripts\pip install .\teleapp-0.1.0-py3-none-any.whl
```

## Notes

- Tags should match the version in `pyproject.toml`.
- Releasing the same tag twice is bad practice. Bump the version instead.
- The workflow triggers only on tags matching `v*`.
