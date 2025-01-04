# The Nez-Oba game controller case

This directory includes CAD drawings of a case for the Nez-Oba
game controller board.


## 3D printing

The STL files can be sliced and 3D-printed. 

- `case-top-2.stl` and `case-bottom-2.stl` are the latest version of
  the case with wide top and bottom parts. The top part includes ten
  holes to host M3 threaded heat-set brass inserts, so that the bottom
  part can be screwed on to the top one. Once assembled, this case has
  a size of approximately 250x126x16 mm, which can be comfortably
  placed on your lap like a mini-keyboard.
  
- A previous design is available in two versions
  `case-{top,bottom}-wide.stl` and `case-{top,bottom}-narrow.stl`. The
  latter is only 207 mm wide, which means it is printable with most
  common consumer 3D printers (whose printable area is usually below
  210 mm). Another difference is that this variant hosts fewer
  heat-set inserts; as a result, the closed case might still show a
  little gap along the long edge; as a makeshift fix, you can print a
  few copies of `clip.stl` and use them to clamp onto the edge. The
  case remains fully usable, but it's not as nice as the other
  version.
  
Pictures `case_*.jpg` under [hw/pics](/hw/pics/) show the wider case
parts after 3D printing:

- The little hole in the bottom part allows you to reach the reset
  button of the Trinket microcontroller by simply using a pin, without
  having to unscrew the top.
  
- The solid ribs in the bottom part press onto the PCB to ensure that
  it does not move inside the case. They are not strictly needed, but
  they help get a tighter assembly.

I printed these in PETG material through
[Craftcloud](https://craftcloud3d.com/), a hub that dispatches 3D
print orders to providers in different countries.


## CAD sources

There are also fully editable Blender CAD sources (I created them with
Blender 3.6) of the two case design: `case-2.blend` is the latest,
wide design, whereas `case.blend` is the older design in two variants
(wide and narrow).

The overall model is built by combining various components using
Boolean modifiers (union and difference). If you want to modify any
parts of the model, you can find the various components hidden in the
list of objects.

Exporting the Blender model to `stl`format should give you the same
files as described in the [previous section](#3d-printing).


## 2D outlines

In this directory, you can also find other sketches I used to build
the 3D model of the case.

1. `footprints.svg` is a drawing exported from the [PCB
   schematics](/hw/kicad/) of the board, showing the footprints of the
   various components soldered onto the PCB. This is the starting
   point to figure out the design of the case.
   
2. `case-2.svg` is a vertical section of the case with dimension
   lines, showing the various holes and solids that make up the
   interior of the case. (As usual, `case.svg` is the slightly older
   design in two widths.)
   
3. `outlines-2.svg` takes `footprints.svg`, tweaks it, and adds the
   projections of the various elements that are present in the
   internal part of the case. (As usual, `outlines.svg` is the
   slightly older design in two widths.)
   
To create the Blender model, I imported `outlines-2.svg` and extruded
its bi-dimensional components to create three-dimensional shapes
following the dimension lines in `case-2.svg`.
