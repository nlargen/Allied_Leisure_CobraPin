BOOGIE GODOT PLAYFIELD — STARTER SCENE

Files:
- BoogiePlayfield.tscn : open this scene in Godot 4 and press F6 to run it.
- BoogiePlayfield.gd   : draws the dark frame, title, hotspot markers, and side legend.
- assets/boogie_playfield_photo.png : perspective-corrected/enhanced crop from your IMG_0544 playfield photo.
- assets/boogie_playfield_preview.png : small preview.

Install into your existing boogie-gmc project:
1. Extract this ZIP.
2. Copy BoogiePlayfield.tscn and BoogiePlayfield.gd into the root of the boogie-gmc project (next to project.godot).
3. Copy the assets folder into that same project root. Merge if an assets folder already exists; don't overwrite unrelated files.
4. In Godot's FileSystem panel, double-click BoogiePlayfield.tscn.
5. Press F6 (Run Current Scene). This does not replace your GMC main scene.

This is a stylized visual reference based on the uploaded Boogie playfield photo. It is not a physics simulation, does not control a ball, and is not connected to MPF events or hardware inputs yet. Marker locations are approximate and intended as clickable labels only.
