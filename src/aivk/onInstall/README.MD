# CORE
## onInstall

# TO INSTALL THE AIVK MODULES

aivk.install -> pip install // uv pip install

# sub cli

aivk-install 

see at pyproject.toml:
```toml
[project.scripts]
aivk-install = "aivk.cli.__main__:install"
```
terminal:
```bash
aivk-install
```