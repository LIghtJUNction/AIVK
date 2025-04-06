#CORE
## onUninstall

# # TO UNINSTALL THE AIVK MODULES

aivk.uninstall -> pip uninstall // uv pip uninstall

# # sub cli

see at pyproject.toml:
```toml
[project.scripts]
aivk-uninstall = "aivk.cli.__main__:uninstall"
```
terminal:
```bash
aivk-uninstall
```
