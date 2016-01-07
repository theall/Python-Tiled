# Libraries and Frameworks

There are many libraries available for reading and/or writing maps stored in
the [TMX map format](../reference/tmx-map-format.md) as well as many development
frameworks that include support for TMX maps. This list is divided into two
sections:

- [Support by Language](#support-by-language)
- [Support by Framework](#support-by-framework)

First list is for developers who plan on implementing their own renderer. Second list is for developers already using (or considering) a particular game engine / graphics library who would rather pass on having to write their own tilemap renderer.

*For updates to this page please open a pull request or issue [on github](https://github.com/bjorn/tiled/issues), thanks!*

## Support by Language

These libraries typically include only a TMX parser, but no rendering support. They can be used universally and should not require a specific game engine or graphics library.

### C
* [TMX](https://github.com/baylej/tmx/) - XML and JSON map loader with Allegro5 and SDL2 examples (BSD).

### C++
* [C++/Boost](http://www.catnapgames.com/blog/2011/10/10/simple-tmx-tilemap-parser.html) by Tomas Andrle (limited functionality, single cpp file)
* [C++/TinyXML based tmx-parser](https://github.com/andrewrk/tmxparser) (BSD)
  - [Original version](http://code.google.com/p/tmx-parser/) by KonoM is discontinued.
* C++/Qt based libtiled, used by Tiled itself and included at [src/libtiled](https://github.com/bjorn/tiled/tree/master/src/libtiled) (BSD)
* [C++11x/TinyXml2 libtmx-parser](https://github.com/halsafar/libtmx-parser) by halsafar. (zlib/tinyxml2)
* [C++11/TinyXml2 libtmx](https://github.com/jube/libtmx) by jube, for reading only (ISC licence). See [documentation](http://jube.github.io/libtmx/index.html).
* [TMXParser](https://github.com/solar-storm-studios/TMXParser) General *.tmx tileset data loader. Intended to be used with TSXParser for external tileset loading. (No internal tileset support)
* [TSXParser](https://github.com/solar-storm-studios/TSXParser) General *.tsx tileset data loader. Intended to be used with TMXParser.

### C#/.NET ###
* [XNA map loader](https://github.com/zachmu/tiled-xna) by Kevin Gadd, extended by Stephen Belanger and Zach Musgrave (has dependency on XNA but supposedly can be turned into a standalone parser easily)
* [TiledSharp](https://github.com/marshallward/TiledSharp): Yet another C# TMX importer library, with Tiled 0.11 support. TiledSharp is a generic parser which can be used in any framework, but it cannot be used to render the maps. Available via NuGet.
* [NTiled](https://github.com/patriksvensson/ntiled): Generic parser for 0.9.1 tiled maps. Available via NuGet.
* [TmxCSharp](https://github.com/gwicksted/TmxCSharp): Useful for multi-layer orthographic tile engines. No framework dependencies, used with a custom OpenTK tile engine soon to be open source, tested with Tiled 0.8.1 (multiple output formats). MIT license.
* [tmx-mapper-pcl](https://github.com/aalmik/tmx-mapper-pcl): PCL library for parsing Tiled map TMX files. This library could be used with MonoGame and Windows Runtime Universal apps.

### D
* [tiledMap.d](https://gist.github.com/gdm85/9896961) simple single-layer and single-tileset example to load a map and its tileset in [D language](http://dlang.org/). It also contains basic rendering logic using [DSFML](https://github.com/Jebbs/DSFML/)

### Go

* [github.com/salviati/go-tmx/tmx](https://github.com/salviati/go-tmx)

### Haskell
* [htiled](http://hackage.haskell.org/package/htiled) by [Christian Rødli Amble](https://github.com/chrra).

### Java
* A library for loading TMX files is included with Tiled at [util/java/libtiled-java](https://github.com/bjorn/tiled/tree/master/util/java/libtiled-java).
* Android-Specific:
    - [AndroidTMXLoader](https://github.com/davidmi/Android-TMX-Loader) loads TMX data into an object and renders to an Android Bitmap (limited functionality)
    - [libtiled-java port](http://chiselapp.com/user/devnewton/repository/libtiled-android/index) is a port of the libtiled-java to be used on Android phones.

### Objective-C & Swift
* [TilemapKit](http://tilemapkit.com) is an actively maintained TMX loader and hierarchical tilemap object model for use with iOS projects. Can be integrated with any C/C++/Objective-C/Swift codebase and used for custom renderers.

### PHP
* [PHP TMX Viewer](https://github.com/sebbu2/php-tmx-viewer) by sebbu : render the map as an image (allow some modifications as well)

### Pike
* [TMX parser](https://gitorious.org/tmx-parser): a simple loader for TMX maps (CSV format only).

### Python
* [pytmxlib](http://pytmxlib.readthedocs.org/en/latest/): library for programmatic manipulation of TMX maps
* [python-tmx](http://python-tmx.nongnu.org): a simple library for reading and writing TMX files.

### Ruby
* [tmx gem](https://github.com/shawn42/tmx) by erisdiscord

### Vala
* [librpg](https://github.com/JumpLink/librpg) A library to load and handle spritesets (own format) and orthogonal TMX maps.

## Support by Framework

Following entries are integrated solutions for specific game engines. They are typically of little to no use if you're not using said game engine.

### AndEngine
* [AndEngine](http://www.andengine.org/) by Nicolas Gramlich supports [rendering TMX maps](http://www.andengine.org/blog/2010/07/andengine-tiledmaps-in-the-tmx-format/)

### Allegro
* [allegro_tiled](https://github.com/dradtke/allegro_tiled) integrates Tiled support with [Allegro 5](http://alleg.sourceforge.net/).

### cocos2d
* [cocos2d (Python)](http://python.cocos2d.org/) supports loading [Tiled maps](http://python.cocos2d.org/doc/programming_guide/tiled_map.html) through its `cocos.tiles` module.
* [cocos2d-x (C++)](http://www.cocos2d-x.org/) supports loading TMX maps through the [CCTMXTiledMap](http://www.cocos2d-x.org/reference/native-cpp/V2.1.4/da/d68/classcocos2d_1_1_c_c_t_m_x_tiled_map.html) class.
* [cocos2d-objc (Objective-C, Swift)](http://www.cocos2d-objc.org/) (previously known as: cocos2d-iphone, cocos2d-swift, cocos2d-spritebuilder) supports loading TMX maps through [CCTiledMap](http://cocos2d.spritebuilder.com/docs/api/Classes/CCTiledMap.html)
* [TilemapKit](http://tilemapkit.com) is an actively maintained tilemapping framework for Cocos2D. It supports all TMX tilemap types, including staggered iso and all hex variations.

### Construct 2 - Scirra
* [Construct 2](http://www.scirra.com), since the Beta Release 149, officially supports TMX maps, and importing it by simple dragging the file inside the editor. [Official Note](https://www.scirra.com/construct2/releases/r149)

### Corona SDK

* [Lime](https://github.com/OutlawGameTools/Lime2DTileEngine) is a 2D engine for making tile-based games with Corona SDK and Tiled

### Flixel
* Lithander demonstrated his [Flash TMX parser combined with Flixel rendering](http://blog.pixelpracht.net/?p=59)

### Game Maker
* [Tiled2GM Converter](http://gmc.yoyogames.com/index.php?showtopic=539494) by Dmi7ry

### Haxe
* [HaxePunk](https://github.com/HaxePunk/tiled) Tiled Loader for HaxePunk
* [HaxeFlixel](https://github.com/HaxeFlixel/flixel-addons/tree/dev/flixel/addons/editors/tiled)
* [OpenFL](https://github.com/Kasoki/openfl-tiled) "openfl-tiled" is a library, which gives OpenFL developers the ability to use the Tiled Map Editor.
* [OpenFL + Tiled + Flixel](https://github.com/kasoki/openfl-tiled-flixel) Experimental glue to use "openfl-tiled" with HaxeFlixel

### HTML5 (multiple engines)
* [Canvas Engine](http://canvasengine.net) A framework to create video games in HTML5 Canvas
* [chesterGL](https://github.com/funkaster/ChesterGL) A simple WebGL/canvas game library
* [KineticJs-Ext](https://github.com/Wappworks/kineticjs-ext) A multi-canvas based game rendering library
* [melonJS](http://www.melonjs.org) A lightweight HTML5 game engine
* [Platypus Engine](https://github.com/PBS-KIDS/Platypus/) A robust orthogonal tile game engine with game entity library.
* [sprite.js](https://github.com/batiste/sprite.js) A game framework for image sprites.
* [TMXjs](https://github.com/cdmckay/tmxjs) A JavaScript, jQuery and RequireJS-based TMX (Tile Map XML) parser and renderer.
* [chem-tmx](https://github.com/andrewrk/chem-tmx) Plugin for [chem](https://github.com/andrewrk/chem/) game engine.
* [GameJs](http://gamejs.org) JavaScript library for game programming; a thin wrapper to draw on HTML5 canvas and other useful modules for game development
* [Crafty](http://craftyjs.com) JavaScript HTML5 Game Engine; supports loading Tiled maps through an external component [TiledMapBuilder](https://github.com/Kibo/TiledMapBuilder).
* [Phaser](http://www.phaser.io) A fast, free and fun open source framework supporting both JavaScript and TypeScript ([Tiled tutorial](http://www.gamedevacademy.org/html5-phaser-tutorial-top-down-games-with-tiled/))

### indielib-crossplatform
* [indielib cross-platform](http://www.indielib.com) supports loading TMX maps through the [C++/TinyXML based tmx-parser](http://code.google.com/p/tmx-parser/) by KonoM (BSD)

### LibGDX
* [libgdx](http://libgdx.badlogicgames.com/), a Java-based Android/desktop/HTML5 game library, [provides](https://github.com/libgdx/libgdx/wiki/Tile-maps) a packer, loader and renderer for TMX maps

### LÖVE
* [Simple Tiled Implementation](https://github.com/Karai17/Simple-Tiled-Implementation) Lua loader for the LÖVE (Love2d) game framework.

### MOAI SDK
* [Hanappe](https://github.com/makotok/Hanappe) Framework for MOAI SDK.
* [Rapanui](https://github.com/ymobe/rapanui) Framework for MOAI SDK.

### Monkey X
* [bit.tiled](https://github.com/bitJericho/bit.tiled) Loads TMX file as objects. Aims to be fully compatible with native TMX files.
* [Diddy](https://code.google.com/p/diddy/) is an extensive framework for Monkey X that contains a module for loading and rendering TMX files.  Supports orthogonal and isometric maps as both CSV and Base64 (uncompressed).

### Node.js
* [node-tmx-parser](https://github.com/andrewrk/node-tmx-parser) - loads the TMX file into a JavaScript object

### Pygame
* [Pygame map loader](http://www.pygame.org/project/1158/) by dr0id
* [PyTMX](https://github.com/bitcraft/PyTMX) by Leif Theden (bitcraft)
* [tmx.py](https://bitbucket.org/r1chardj0n3s/pygame-tutorial/src/a383dd24790d/tmx.py) by Richard Jones, from his [2012 PyCon 'Introduction to Game Development' talk](http://pyvideo.org/video/615/introduction-to-game-development).
* [TMX](https://github.com/renfredxh/tmx), a fork of tmx.py and a port to Python3.  A demo called pylletTown can be found [here](https://github.com/renfredxh/pylletTown).

### Pyglet
* [JSON map loader/renderer for pyglet](https://github.com/reidrac/pyglet-tiled-json-map) by Juan J. Martínez (reidrac)
* [PyTMX](https://github.com/bitcraft/PyTMX) by Leif Theden (bitcraft)

### PySDL2
* [PyTMX](https://github.com/bitcraft/PyTMX) by Leif Theden (bitcraft)

### SDL
* [C++/TinyXML/SDL based loader](http://usefulgamedev.weebly.com/c-tiled-map-loader.html) example by Rohin Knight (limited functionality)

### SFML
* [STP](https://github.com/edoren/STP) (SFML TMX Parser) by edoren
* [C++/SFML Tiled map loader](http://trederia.blogspot.co.uk/2013/05/tiled-map-loader-for-sfml.html) by fallahn. (Zlib/libpng)
* [C++/SfTileEngine](https://github.com/Tresky/sf_tile_engine) by Tresky (currently limited functionality)

### Slick2D
* [Slick2D](http://slick.ninjacave.com) supports loading TMX maps through [TiledMap](http://slick.ninjacave.com/javadoc/org/newdawn/slick/tiled/TiledMap.html).

### Sprite Kit Framework
* [TilemapKit](http://tilemapkit.com) is an actively maintained tilemapping framework for Sprite Kit. It supports all TMX tilemap types, including staggered iso and all hex variations.
* [JSTileMap](https://github.com/slycrel/JSTileMap) is a lightweight SpriteKit implementation of the TMX format supporting iOS 7 and OS X 10.9 and above.

### TERRA Engine (Delphi/Pascal)
* [TERRA Engine](http://pascalgameengine.com/) supports loading and rendering of TMX maps.

### Unity 3D
* [Orthello Pro](http://www.wyrmtale.com/products/unity3d-components/orthello-pro) (2D framework) offers [Tiled map support](http://www.wyrmtale.com/orthello-pro/tilemaps).
* [Tiled Tilemaps](http://karnakgames.com/wp/unity-tiled-tilemaps/) library by Karnak Games adds support for Orthogonal TMX maps to Unity, with automatic collision detection.
* [Tiled To Unity](https://www.assetstore.unity3d.com/#/content/17260/) is a 3D pipeline for Tiled maps. It uses prefabs as tiles, and can place decorations dynamically on tiles. Supports multiple layers (including object layers).
* [Tiled2Unity](http://www.seanba.com/introtiled2unity.html) exports TMX files to Unity with support for (non-simple) collisions.
* [UniTMX](https://bitbucket.org/PolCPP/unitmx/overview) imports TMX files into a mesh.
* [X-UniTMX](https://bitbucket.org/Chaoseiro/x-unitmx) supports almost all Tiled 0.10 features. Imports TMX/XML files into Sprite Objects or Meshes.

### Unreal Engine 4
* [Paper2D](https://forums.unrealengine.com/showthread.php?3539-Project-Paper2D) provides built-in support for tile maps and tile sets, importing JSON exported from Tiled.

### Urho3D
* [Urho3D](http://urho3d.github.io/) natively supports loading Tiled maps as part of the [Urho2D](http://urho3d.github.io/documentation/1.4/_urho2_d.html) sublibrary ([Documentation](http://urho3d.github.io/documentation/1.4/class_urho3_d_1_1_tile_map2_d.html), [HTML5 example](http://urho3d.github.io/samples/36_Urho2DTileMap.html)).

### XNA
* [FlatRedBall Engine TMXGlue tool](http://www.flatredball.com/frb/docs/index.php?title=Kain%27s_Tavern#Tiled_Map_Editor.2C_TMX.2C_Glue_and_you.) by Domenic Datti loads TMX maps into the FlatRedBall engine, complete with node networks, pathfinding, and shapecollection support via object layers.
* [TiledMax](http://tiledmax.xpod.be/) by Aimee Bailey, a .NET library for parsing TMX maps without dependencies on Windows or XNA
* [XTiled](https://bitbucket.org/vinull/xtiled) by Michael C. Neel and Dylan Wolf, XNA library for loading and rendering TMX maps
* [XNA map loader](https://github.com/zachmu/tiled-xna) by Kevin Gadd, extended by Stephen Belanger and Zach Musgrave
