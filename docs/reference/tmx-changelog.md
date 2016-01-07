---
# TMX Changelog #

Below are described the changes/additions that were made to the [TMX format](tmx-map-format.md) for recent versions of Tiled.

## Tiled 0.14 ##

* Added optional `offsetx` and `offsety` attributes to the `layer` and `objectgroup` elements. These specify an offset in pixels that is to be applied when rendering the layer. The default values are 0.

## Tiled 0.13 ##

* Added an optional `tilecount` attribute to the `tileset` element, which is written by Tiled to help parsers determine the amount of memory to allocate for tile data.

## Tiled 0.12 ##

* Previously tile objects never had `width` and `height` properties, though the format technically allowed this. Now these properties are used to store the size the image should be rendered at. The default values for these attributes are the dimensions of the tile image.

## Tiled 0.11 ##

* Added `hexagonal` to the supported values for the `orientation` attribute on the `map` element. This also adds `staggerindex` (`even` or `odd`) and `staggerdirection` (`rows` or `columns`) and `hexsidelength` (integer value) attributes to the `map` element, in order to support the many variations of staggered hexagonal. The `staggerindex` attribute is now also supported when using the `staggered` map orientation.
* Added an `id` attribute to the `object` element, which stores a map-unique ID of the object.

## Tiled 0.10 ##

* Tile objects can now be horizontally or vertically flipped. This is stored in the `gid` attribute using the same mechanism as for regular tiles. The image is expected to be flipped without affecting its position, same way as flipped tiles.

* Objects can be rotated freely. The rotation is stored in degrees as a `rotation` attribute, with positive rotation going clockwise.

* The render order of the tiles on tile layers can be configured in a number of ways through a new `renderorder` property on the `map` element. Valid values are `right-down` (the default), `right-up`, `left-down` and `left-up`. In all cases, the map is drawn row-by-row. This is only supported for orthogonal maps at the moment.

* The render order of objects on object layers can be configured to be either sorted by their y-coordinate (previous behavior and still the default) or simply the order of appearance in the map file. The latter enables manual control over the drawing order with actions that "Raise" and "Lower" selected objects. It is controlled by the `draworder` property on the `objectgroup` element, which can be either `topdown` (default) or `index`.

* Tiles can have an `objectgroup` child element, which can contain objects that define the collision shape to use for that tile. This information can be edited in the new Tile Collision Editor.

* Tiles can have a single looping animation associated with them using an `animation` child element. Each frame of the animation refers to a local tile ID from this tileset and defines the frame duration in milliseconds. Example:
```xml
<tileset ...>
    ...
    <tile id="[n]">
        <animation>
            <frame tileid="0" duration="100"/>
            <frame tileid="1" duration="100"/>
            <frame tileid="2" duration="100"/>
        </animation>
    </tile>
</tileset>
```

## Tiled 0.9 ##

* Per-object visibility flag is saved (defaults to 1):
```xml
<object visible="0|1">
```

* Terrain information was added to tileset definitions (this is generally not very relevant for games):
```xml
<tileset ...>
    ...
    <terraintypes>
        <terrain name="Name" tile="local_id"/>
    </terraintypes>
    <tile id="local_id" terrain="[n],[n],[n],[n]" probability="percentage"/>
    ...
</tileset>
```

* There is preliminary support for a "staggered" (isometric) projection (new value for the `orientation` attribute of the `map` element).

* A basic image layer type was added:
```xml
<imagelayer ...>
    <image source="..."/>
</imagelayer>
```

* Added ellipse object shape. Same parameters as rectangular objects, but marked as ellipse with a child element:
```xml
<object ...>
    <ellipse/>
</object>
```

* Added map property for specifying the background color:
```xml
<map ... backgroundcolor="#RRGGBB">
```

* Added initial (non-GUI) support for individual and/or embedded tile images (since there is no way to set this up in Tiled Qt but only in Tiled Java or with [pytmxlib](https://github.com/encukou/pytmxlib), this is not very important to support at the moment):
```xml
<tileset ...>
    <tile id="[n]">
        <!-- an embedded image -->
        <image format="png">
            <data encoding="base64">
                ...
            </data>
        </image>
    </tile>
    <tile id="[n]">
        <!-- an individually referenced image for a single tile -->
        <image source="file.png"/>
    </tile>
    ...
</tileset>
```

## Tiled 0.8 ##

* Tilesets can now have custom properties (using the `properties` child element, just like everything else).

* Tilesets now support defining a drawing offset in pixels, which is to be used when drawing any tiles from that tileset. Example:
```xml
<tileset name="perspective_walls" tilewidth="64" tileheight="64">
    <tileoffset x="-32" y="0"/>
    ...
</tileset>
```

* Support for tile rotation in 90-degree increments was added by using the third most significant bit in the global tile id. This new bit means "anti-diagonal flip", which swaps the x and y axis when rendering a tile.
