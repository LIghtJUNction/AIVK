# CORE
## onUnload

# TO CLOSE THE SYSTEM

aivk.unload -> aivk-loader.unload -> other_modules.unload

# sub cli
aivk-unload

# see at pyproject.toml:
```toml
[project.scripts]
aivk-unload = "aivk.cli.__main__:unload"
```
terminal:
```bash
aivk-unload
```
