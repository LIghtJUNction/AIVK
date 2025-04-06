#CORE
## onLoad

# TO LOAD THE SYSTEM
aivk.load -> aivk-loader.load -> other_modules.load

# sub cli
aivk-load

see at pyproject.toml:
```toml
[project.scripts]
aivk-load = "aivk.cli.__main__:load"
```
terminal:
```bash
aivk-load
```
