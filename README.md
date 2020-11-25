# sim
Code for simulations in Blender

## Setup

Install the following addon for VSCode. It supports fast script testing and debug functionality for Blender in VSCode.

[Blender Development - Jacques Lucke](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development)

Follow the instructions for running a Blender instance, and launching the script. 

## Running from Command-line

Open the terminal at the root level of the project directory (i.e sim\\)

To run the file and setup the environment, run

```blender -P blender_scripts\blender_env.py```

To setup the environment and create render frames, run 

```blender -P blender_scripts\blender_env.py -- render```

Optionally, if you wish to run the entire process in the background without the UI, add the ```-b``` arg (it does not speedup runtime however)

```blender -b -P blender_scripts\blender_env.py -- render```

[Blender CLI args Documentation](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)

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
---
[Alternate auto-complete solution by installing a fake bpy module](https://youtu.be/IQgLBnPO2uo)

## Function Documentation

### Lighting

---

```BlenderEnv.make_lights(self, type_of_light,number_of_lights, base_power, power_variance,light_color='random',color_min=0, color_max=1)```

Populates ```self.lights_collection``` with Blender light objects. Lights are generated in the vicinity of the simulated arena.

<b>Parameters:</b>

<i>type_of_light (String)</i>: Determines which style of Blender light object to create.

Options: ```'Point'```,```'SPOT'```

<i>number_of_lights (Int)</i>: Determines the number of Blender light objects that the function generates.

<i>base_power (Float)</i>: Determines the minimum power (in Watts) of Blender light objects that the function generates.

<i>base_power (Float)</i>: Determines the maximum additional power (in Watts) on top of <i>base_power</i> that light objects can attain. Power values of lights are in the range (<i>base_power, base_power+power_variance</i>).

<i>light_color (3-Tuple of Floats between 0 and 1)</i>: Specifies the RGB values for the color of light objects. If no value is specified, colors are determined randomly.

<i>color_min (Float between 0 and 1)</i>: For random light colors, specifies the minimum value for RGB values.

<i>color_max (Float between 0 and 1)</i>: For random light colors, specifies the maximum value for the RGB values.

---

### Render functionality

---

All the configurations for rendering frames, including simulation variables and render output quality are at the top of render.py in a dict called ```render_configs```, adjust as necessary.

---
