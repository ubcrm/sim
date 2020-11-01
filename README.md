# sim
Code for simulations in Blender

## Setup

Install the following addon for VSCode. It support fast script testing and debug functinoality for Blender in VSCode.

[Blender Development - Jacques Lucke](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development)

Follow the instructions for running a Blender instance, and launching the script. 


## Running from Command-line

```blender --background --python myscript.py```

```blender --python myscript.py```


## Auto complete Blender

See (rough) instructions here: [Using Microsoft Visual Studio Code as external IDE for writing Blender scripts/add-ons](https://b3d.interplanety.org/en/using-microsoft-visual-studio-code-as-external-ide-for-writing-blender-scripts-add-ons/)

Core steps: 
- Download repo with Blender Autocomplete:
- Search `python.autoComplete.extraPaths` in your settings (Workspace or user)
- Add the following:
```
    "python.autoComplete.extraPaths": [
    
        "/path_to/blender_autocomplete-master/2.90"    
    ],
    "python.linting.pylintArgs": [
        "--init-hook",
        "import sys; sys.path.append('/path_to/blender_autocomplete-master/2.90')"
    ],
```
