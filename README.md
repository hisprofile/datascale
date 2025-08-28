# Data Scale
## Introduction
Data Scale offers a quick way to inspect the size of selected IDs such as objects, textures, shaders, etc. Whether it's to help artists optimize their work, or to show new users how additions can impact the resulting file, it sure is interesting to see what makes up for size in a .blend file.

Data Scale registers two operators: `Weigh IDs` and `Export Selected IDs as Library`

## Weigh IDs Operator
### Parameters
- Compress
  - Choose whether or not to compress the final result. This parameter is available in the preferences, and the Outliner or Properties Context Menu.
### How To Use
This operator is accessible from:
- The 3D Viewport via `Object -> Weigh IDs`
- Outliner via `Context Menu (right click) -> Data Scale Operators -> Weigh IDs`
- Properties via `Context Menu (right click) -> Data Scale Operators -> Weigh IDs`
  
In the Outliner and Viewport, you may select however many objects to weigh. However, using `Weigh IDs` through the Outliner does not limit you in what types of IDs you can weigh.

In the Properties panel, you may only weigh One ID, and that is according to what tab is active.

After using the `Weigh IDs` tool, the resulting file size will be reported to you at the bottom of the screen.

## Export Selected IDs as Library Operator
### Parameters
- Compress
  - Choose whether or not to compress the final result.
- Library Path Remap
  - Remap the paths for used libraries. By default, `RELATIVE_ALL` is used.
- Fake User
  - Add Fake Users to the IDs to ensure their persistence.
- Create Default Scene
  - Creates a default scene to link IDs to, ensuring they are viewable on first open. Otherwise, you will have to link them to a scene yourself.
### How To Use
This operator is accessible from:
- File -> Export
- Outliner via `Context Menu (right click) -> Data Scale Operators -> Export Selected IDs as Library`
- Properties via `Context Menu (right click) -> Data Scale Operators -> Export Selected IDs as Library`
  
The former rules apply to what you may and may not select depending where you use the operator from. The `File -> Export` option only exports selected objects in the viewport.

When using the operator, a file select menu will pop-up allowing you to find a destination to export the selected IDs to. When you have confirmed, a new .blend file will be written containing only the IDs you have selected.

# Credits
HAYTAM14 for coining the name
