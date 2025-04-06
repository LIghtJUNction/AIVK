# CORE

# MAIN CLI

pyproject.toml:
```toml
[project.scripts]
aivk = "aivk.cli.__main__:main"
```
terminal:
```bash
aivk
```

use
```bash
aivk <load/unload/install/uninstall> <args...>
```
equal to
```bash
aivk-<sub clis: update | load | unload | install | uninstall> <args...>
```

