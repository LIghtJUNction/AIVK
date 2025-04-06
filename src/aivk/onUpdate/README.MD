# OPTIONAL 可选

aivk use this to update other modules

aivk-module don't need to implement this

simply use:
pip install --upgrade aivk-module
uv pip install --upgrade aivk-module

# # sub cli
aivk-update

see at pyproject.toml:
```toml
[project.scripts]
aivk-update = "aivk.cli.__main__:update"
```
terminal:
```bash
aivk-update
```
