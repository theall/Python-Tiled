<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="bg">
<context>
    <name>AboutDialog</name>
    <message>
        <location filename="../src/tiled/aboutdialog.ui" line="+14"/>
        <source>About Tiled</source>
        <translation>Относно Tiled</translation>
    </message>
    <message>
        <location line="+83"/>
        <source>Donate</source>
        <translation>Дарение</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>OK</source>
        <translation>Добре</translation>
    </message>
    <message>
        <location filename="../src/tiled/aboutdialog.cpp" line="+36"/>
        <source>&lt;p align=&quot;center&quot;&gt;&lt;font size=&quot;+2&quot;&gt;&lt;b&gt;Tiled Map Editor&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&lt;i&gt;Version %1&lt;/i&gt;&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;Copyright 2008-2015 Thorbj&amp;oslash;rn Lindeijer&lt;br&gt;(see the AUTHORS file for a full list of contributors)&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;You may modify and redistribute this program under the terms of the GPL (version 2 or later). A copy of the GPL is contained in the &apos;COPYING&apos; file distributed with Tiled.&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;&lt;a href=&quot;http://www.mapeditor.org/&quot;&gt;http://www.mapeditor.org/&lt;/a&gt;&lt;/p&gt;
</source>
        <translation>&lt;p align=&quot;center&quot;&gt;&lt;font size=&quot;+2&quot;&gt;&lt;b&gt;Редактор за карти Tiled&lt;/b&gt;&lt;/font&gt;&lt;br&gt;&lt;i&gt;Версия %1&lt;/i&gt;&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;© 2008-2015 Thorbj&amp;oslash;rn Lindeijer&lt;br&gt;(вижте файла AUTHORS за пълен списък на хората с принос)&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;Можете да променяте и разпространявате тази програма според условията на ОПЛ на ГНУ (версия 2 или по-нова). Във файла „COPYING“, който се разпространява с Tiled, има копие на ОПЛ.&lt;/p&gt;
&lt;p align=&quot;center&quot;&gt;&lt;a href=&quot;http://www.mapeditor.org/&quot;&gt;http://www.mapeditor.org/&lt;/a&gt;&lt;/p&gt;
</translation>
    </message>
</context>
<context>
    <name>Command line</name>
    <message>
        <location filename="../src/tiled/main.cpp" line="+214"/>
        <source>Export syntax is --export-map [format] &lt;tmx file&gt; &lt;target file&gt;</source>
        <translation>Синтаксисът за извличане е: --export-map [формат] &lt;tmx файл&gt; &lt;целеви файл&gt;</translation>
    </message>
    <message>
        <location line="+23"/>
        <source>Format not recognized (see --export-formats)</source>
        <translation>Форматът не беше разпознат (вижте --export-formats)</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Non-unique file extension. Can&apos;t determine correct export format.</source>
        <translation>Файловото разширение не е уникално. Правилният формат за извличане не може да бъде определен.</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>No exporter found for target file.</source>
        <translation>Не е открит износител за целевия файл.</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Failed to load source map.</source>
        <translation>Неуспешно зареждане на изходната карта.</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Failed to export map to target file.</source>
        <translation>Неуспешно изнасяне на картата в целевия файл.</translation>
    </message>
</context>
<context>
    <name>CommandDialog</name>
    <message>
        <location filename="../src/tiled/commanddialog.ui" line="+14"/>
        <source>Properties</source>
        <translation>Свойства</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>&amp;Save map before executing</source>
        <translation>&amp;Запазване на картата преди изпълнение</translation>
    </message>
</context>
<context>
    <name>CommandLineHandler</name>
    <message>
        <location filename="../src/tiled/main.cpp" line="-184"/>
        <source>Display the version</source>
        <translation>Показва версията</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Only check validity of arguments</source>
        <translation>Извършва само проверка на аргументите</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Disable hardware accelerated rendering</source>
        <translation>Изключва хардуерното ускорение на изчертаването</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Export the specified tmx file to target</source>
        <translation>Изнася посочения tmx файл към зададената цел</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Print a list of supported export formats</source>
        <translation>Извежда списък от поддържаните формати за изнасяне</translation>
    </message>
    <message>
        <location line="+32"/>
        <source>Export formats:</source>
        <translation>Формати за изнасяне:</translation>
    </message>
</context>
<context>
    <name>CommandLineParser</name>
    <message>
        <location filename="../src/tiled/commandlineparser.cpp" line="+75"/>
        <source>Bad argument %1: lonely hyphen</source>
        <translation>Грешен аргумент %1: само тире</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Unknown long argument %1: %2</source>
        <translation>Непознат дълъг аргумент %1: %2</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Unknown short argument %1.%2: %3</source>
        <translation>Непознат кратък аргумент %1.%2: %3</translation>
    </message>
    <message>
        <location line="+17"/>
        <source>Usage:
  %1 [options] [files...]</source>
        <translation>Използване:
  %1 [опции] [файлове...]</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Options:</source>
        <translation>Опции:</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Display this help</source>
        <translation>Показва това помощно съобщение</translation>
    </message>
</context>
<context>
    <name>ConverterDataModel</name>
    <message>
        <location filename="../src/automappingconverter/converterdatamodel.cpp" line="+75"/>
        <source>File</source>
        <translation>Файл</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Version</source>
        <translation>Версия</translation>
    </message>
</context>
<context>
    <name>ConverterWindow</name>
    <message>
        <location filename="../src/automappingconverter/converterwindow.cpp" line="+36"/>
        <source>Save all as %1</source>
        <translation>Запазване на всичко като %1</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>All Files (*)</source>
        <translation>Всички файлове (*)</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Tiled map files (*.tmx)</source>
        <translation>Файлове с карти на Tiled (*.tmx)</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Open Map</source>
        <translation>Отваряне на карта</translation>
    </message>
</context>
<context>
    <name>Csv::CsvPlugin</name>
    <message>
        <location filename="../src/plugins/csv/csvplugin.cpp" line="+55"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+75"/>
        <source>CSV files (*.csv)</source>
        <translation>Файлове с разделители (*.csv)</translation>
    </message>
</context>
<context>
    <name>Droidcraft::DroidcraftPlugin</name>
    <message>
        <location filename="../src/plugins/droidcraft/droidcraftplugin.cpp" line="+57"/>
        <source>This is not a valid Droidcraft map file!</source>
        <translation>Това не е файл с карта на Droidcraft!</translation>
    </message>
    <message>
        <location line="+44"/>
        <source>The map needs to have exactly one tile layer!</source>
        <translation>Картата трябва да има точно един слой!</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>The layer must have a size of 48 x 48 tiles!</source>
        <translation>Слоят трябва да е с размер 48 х 48 плочки!</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>Droidcraft map files (*.dat)</source>
        <translation>Файлове с карти на Droidcraft (*.dat)</translation>
    </message>
</context>
<context>
    <name>EditTerrainDialog</name>
    <message>
        <location filename="../src/tiled/editterraindialog.ui" line="+14"/>
        <source>Edit Terrain Information</source>
        <translation>Редактиране на теренната информация</translation>
    </message>
    <message>
        <location line="+11"/>
        <location line="+3"/>
        <source>Undo</source>
        <translation>Отмяна</translation>
    </message>
    <message>
        <location line="+20"/>
        <location line="+3"/>
        <source>Redo</source>
        <translation>Повторение</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Erase</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location line="+89"/>
        <source>Add Terrain Type</source>
        <translation>Добавяне на теренен тип</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Add</source>
        <translation>Добавяне</translation>
    </message>
    <message>
        <location line="+17"/>
        <source>Remove Terrain Type</source>
        <translation>Премахване на теренен тип</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Remove</source>
        <translation>Премахване</translation>
    </message>
</context>
<context>
    <name>ExportAsImageDialog</name>
    <message>
        <location filename="../src/tiled/exportasimagedialog.ui" line="+14"/>
        <source>Export As Image</source>
        <translation>Изнасяне като изображение</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Location</source>
        <translation>Местоположение</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Name:</source>
        <translation>Име:</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>&amp;Browse...</source>
        <translation>&amp;Разглеждане...</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Settings</source>
        <translation>Настройки</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Only include &amp;visible layers</source>
        <translation>Само &amp;видимите слоеве</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Use current &amp;zoom level</source>
        <translation>Да се използва текущата степен на &amp;приближение</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>&amp;Draw tile grid</source>
        <translation>Да се &amp;изчертае решетката на плочките</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>&amp;Include background color</source>
        <translation>Да се включи цвета на &amp;фона</translation>
    </message>
</context>
<context>
    <name>Flare::FlarePlugin</name>
    <message>
        <location filename="../src/plugins/flare/flareplugin.cpp" line="+52"/>
        <source>Could not open file for reading.</source>
        <translation>Неуспешно отваряне на файла за четене.</translation>
    </message>
    <message>
        <location line="+79"/>
        <source>Error loading tileset %1, which expands to %2. Path not found!</source>
        <translation>Грешка при зареждането на плочен набор %1 от %2. Файлът липсва!</translation>
    </message>
    <message>
        <location line="+18"/>
        <source>No tilesets section found before layer section.</source>
        <translation>Не е открит раздел за плочни набори преди раздела за слоя.</translation>
    </message>
    <message>
        <location line="+28"/>
        <source>Error mapping tile id %1.</source>
        <translation>Грешка при напасване на ид. на плочка %1.</translation>
    </message>
    <message>
        <location line="+70"/>
        <source>This seems to be no valid flare map. A Flare map consists of at least a header section, a tileset section and one tile layer.</source>
        <translation>Това не изглежда като правилно оформена карта на flare. Картите на Flare имат заглавен раздел, раздел за плочни набори и един слой плочки.</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>Flare map files (*.txt)</source>
        <translation>Файлове с карти на Flare (*.txt)</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
</context>
<context>
    <name>Json::JsonMapFormat</name>
    <message>
        <location filename="../src/plugins/json/jsonplugin.cpp" line="+53"/>
        <source>Could not open file for reading.</source>
        <translation>Неуспешно отваряне на файла за четене.</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Error parsing file.</source>
        <translation>Грешка при разбора на файла.</translation>
    </message>
    <message>
        <location line="+18"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+36"/>
        <source>Error while writing file:
%1</source>
        <translation>Грешка при записа на файла:
%1</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>Json map files (*.json)</source>
        <translation>Файлове с карти във формата json (*.json)</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>JavaScript map files (*.js)</source>
        <translation>Файлове с карти на езика JavaScript (*.js)</translation>
    </message>
</context>
<context>
    <name>Json::JsonTilesetFormat</name>
    <message>
        <location line="+27"/>
        <source>Could not open file for reading.</source>
        <translation>Неуспешно отваряне на файла за четене.</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Error parsing file.</source>
        <translation>Грешка при разбора на файла.</translation>
    </message>
    <message>
        <location line="+27"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Error while writing file:
%1</source>
        <translation>Грешка при записа на файла:
%1</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Json tileset files (*.json)</source>
        <translation>Файлове с плочни набори във формата json (*.json)</translation>
    </message>
</context>
<context>
    <name>Lua::LuaPlugin</name>
    <message>
        <location filename="../src/plugins/lua/luaplugin.cpp" line="+58"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+26"/>
        <source>Lua files (*.lua)</source>
        <translation>Файлове с код на Lua (*.lua)</translation>
    </message>
</context>
<context>
    <name>MainWindow</name>
    <message>
        <location filename="../src/tiled/mainwindow.ui" line="+46"/>
        <source>&amp;File</source>
        <translation>&amp;Файл</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>&amp;Recent Files</source>
        <translation>&amp;Скорошни файлове</translation>
    </message>
    <message>
        <location line="+26"/>
        <source>&amp;Edit</source>
        <translation>&amp;Редактиране</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>&amp;Help</source>
        <translation>&amp;Помощ</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;Map</source>
        <translation>&amp;Карта</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>&amp;View</source>
        <translation>&amp;Изглед</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Show Object &amp;Names</source>
        <translation>Показване на &amp;имената на обектите</translation>
    </message>
    <message>
        <location line="+27"/>
        <source>Main Toolbar</source>
        <translation>Основна лента с инструменти</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>Tools</source>
        <translation>Инструменти</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>&amp;Open...</source>
        <translation>&amp;Отваряне...</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;Save</source>
        <translation>&amp;Запазване</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;Quit</source>
        <translation>Из&amp;ход</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>&amp;Copy</source>
        <translation>&amp;Копиране</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>&amp;Paste</source>
        <translation>&amp;Поставяне</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;About Tiled</source>
        <translation>&amp;Относно Tiled</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>About Qt</source>
        <translation>Относно Qt</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>&amp;Resize Map...</source>
        <translation>П&amp;реоразмеряване на картата...</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Map &amp;Properties</source>
        <translation>&amp;Свойства на картата</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>AutoMap</source>
        <translation>АвтоКартиране</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>A</source>
        <translation>A</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Show &amp;Grid</source>
        <translation>Показване на &amp;решетката</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+G</source>
        <translation>Ctrl+G</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Save &amp;As...</source>
        <translation>Запазване &amp;като...</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;New...</source>
        <translation>&amp;Нова...</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>New &amp;Tileset...</source>
        <translation>Нов &amp;плочен набор...</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>&amp;Close</source>
        <translation>З&amp;атваряне</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Zoom In</source>
        <translation>Приближаване</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Zoom Out</source>
        <translation>Отдалечаване</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Normal Size</source>
        <translation>Нормален размер</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+0</source>
        <translation>Ctrl+0</translation>
    </message>
    <message>
        <location line="+142"/>
        <source>Become a Patron</source>
        <translation>Станете патрон</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Save All</source>
        <translation>Запазване на всичко</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Documentation</source>
        <translation>Документация</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>&amp;Never</source>
        <translation>На &amp;никои</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>For &amp;Selected Objects</source>
        <translation>На &amp;избраните обекти</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>For &amp;All Objects</source>
        <translation>На &amp;всички обекти</translation>
    </message>
    <message>
        <location line="-162"/>
        <source>Cu&amp;t</source>
        <translation>&amp;Изрязване</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>&amp;Offset Map...</source>
        <translation>&amp;Отместване на картата...</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Offsets everything in a layer</source>
        <translation>Отмества всичко в даден слой</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Pre&amp;ferences...</source>
        <translation>На&amp;стройки...</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Clear Recent Files</source>
        <translation>Изчистване на скорошните файлове</translation>
    </message>
    <message>
        <location line="+87"/>
        <source>Ctrl+R</source>
        <translation>Ctrl+R</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>&amp;Export</source>
        <translation>Изнас&amp;яне</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+E</source>
        <translation>Ctrl+E</translation>
    </message>
    <message>
        <location line="-82"/>
        <source>&amp;Add External Tileset...</source>
        <translation>&amp;Добавяне на външен плочен набор...</translation>
    </message>
    <message>
        <location line="-50"/>
        <source>Export As &amp;Image...</source>
        <translation>Изнасяне като изо&amp;бражение...</translation>
    </message>
    <message>
        <location line="+42"/>
        <source>E&amp;xport As...</source>
        <translation>Изнасяне ка&amp;то...</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+Shift+E</source>
        <translation>Ctrl+Shift+E</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>&amp;Snap to Grid</source>
        <translation>&amp;Прилепване към мрежата</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>C&amp;lose All</source>
        <translation>Зат&amp;варяне на всичко</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+Shift+W</source>
        <translation>Ctrl+Shift+W</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>&amp;Delete</source>
        <translation>Изтрива&amp;не</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Delete</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>&amp;Highlight Current Layer</source>
        <translation>&amp;Осветяване на текущия слой</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>H</source>
        <translation>H</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Show Tile Object &amp;Outlines</source>
        <translation>Показване на &amp;контурите на обектите</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Snap to &amp;Fine Grid</source>
        <translation>Прилепване към &amp;фината решетка</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Show Tile Animations</source>
        <translation>Показване на анимациите на плочките</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Reload</source>
        <translation>Презареждане</translation>
    </message>
    <message>
        <location filename="../src/automappingconverter/converterwindow.ui" line="+14"/>
        <source>Tiled Automapping Rule Files Converter</source>
        <translation>Преобразувател на файлове с правила за автокартиране на Tiled</translation>
    </message>
    <message>
        <location line="+25"/>
        <source>Add new Automapping rules</source>
        <translation>Добавяне на нови правила за автокартиране</translation>
    </message>
</context>
<context>
    <name>MapReader</name>
    <message>
        <location filename="../src/libtiled/mapreader.cpp" line="+141"/>
        <source>Not a map file.</source>
        <translation>Това не е файл с карта.</translation>
    </message>
    <message>
        <location line="+19"/>
        <source>Not a tileset file.</source>
        <translation>Това не е файл с плочен набор.</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>%3

Line %1, column %2</source>
        <translation>%3

Ред %1, колона %2</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>File not found: %1</source>
        <translation>Файлът не е открит: %1</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Unable to read file: %1</source>
        <translation>Неуспешно прочитане на файла: %1</translation>
    </message>
    <message>
        <location line="+37"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+58"/>
        <source>Unsupported map orientation: &quot;%1&quot;</source>
        <translation>Неподдържана ориентация на картата: &quot;%1&quot;</translation>
    </message>
    <message>
        <location line="+83"/>
        <location line="+19"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+110"/>
        <source>Invalid tileset parameters for tileset &apos;%1&apos;</source>
        <translation>Грешни параметри на плочния набор „%1“</translation>
    </message>
    <message>
        <location line="+20"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-19"/>
        <source>Error while loading tileset &apos;%1&apos;: %2</source>
        <translation>Грешка при зареждане на плочен набор „%1“: %2</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Invalid tile ID: %1</source>
        <translation>Грешен ид. на плочка: %1</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Tile ID does not exist in tileset image: %1</source>
        <translation>Няма такъв ид. на плочка в изображението с плочния набор: %1</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Invalid (nonconsecutive) tile ID: %1</source>
        <translation>Грешен (непоследователен) ид. на плочка: %1</translation>
    </message>
    <message>
        <location line="+89"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+38"/>
        <source>Error loading tileset image:
&apos;%1&apos;</source>
        <translation>Грешка при зареждане на изображение с плочен набор:
„%1“</translation>
    </message>
    <message>
        <location line="+33"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+329"/>
        <source>Error loading image:
&apos;%1&apos;</source>
        <translation>Грешка при зареждане на изабражение:
„%1“</translation>
    </message>
    <message>
        <location line="+117"/>
        <source>Too many &lt;tile&gt; elements</source>
        <translation>Твърде много елементи &lt;tile&gt;</translation>
    </message>
    <message>
        <location line="+44"/>
        <location line="+43"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-120"/>
        <source>Invalid tile: %1</source>
        <translation>Грешна плочка: %1</translation>
    </message>
    <message>
        <location line="+29"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+34"/>
        <source>Invalid draw order: %1</source>
        <translation>Грешен ред на изчертаване: %1</translation>
    </message>
    <message>
        <location line="+62"/>
        <source>Error loading image layer image:
&apos;%1&apos;</source>
        <translation>Грешка при зареждането на изображение от слоя с изображения:
„%1“</translation>
    </message>
    <message>
        <location line="+98"/>
        <source>Invalid points data for polygon</source>
        <translation>Грешни данни за точките на многоъгълник</translation>
    </message>
    <message>
        <location line="-290"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-90"/>
        <source>Unknown encoding: %1</source>
        <translation>Непознато кодиране: %1</translation>
    </message>
    <message>
        <location line="-5"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-4"/>
        <source>Compression method &apos;%1&apos; not supported</source>
        <translation>Методът за компресия „%1“ не се поддържа</translation>
    </message>
    <message>
        <location line="+57"/>
        <location line="+19"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+15"/>
        <location line="+39"/>
        <source>Corrupt layer data for layer &apos;%1&apos;</source>
        <translation>Повредени данни за слой „%1“</translation>
    </message>
    <message>
        <location line="+12"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-28"/>
        <source>Unable to parse tile at (%1,%2) on layer &apos;%3&apos;</source>
        <translation>Неуспешен прочит на плочка на (%1,%2) от слой „%3“</translation>
    </message>
    <message>
        <location line="-28"/>
        <location line="+44"/>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="+31"/>
        <source>Tile used but no tilesets specified</source>
        <translation>Плочката е използвана без да е зададен плочен набор</translation>
    </message>
    <message>
        <location filename="../src/libtiled/mapwriter.cpp" line="+106"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location filename="../src/libtiled/varianttomapconverter.cpp" line="-184"/>
        <source>Tileset tile index negative:
&apos;%1&apos;</source>
        <translation>Отрицателен номер на плочка в плочен набор:
&apos;%1&apos;</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Tileset tile index too high:
&apos;%1&apos;</source>
        <translation>Твърде голям номер на плочка в плочен набор:
&apos;%1&apos;</translation>
    </message>
</context>
<context>
    <name>NewMapDialog</name>
    <message>
        <location filename="../src/tiled/newmapdialog.ui" line="+14"/>
        <source>New Map</source>
        <translation>Нова карта</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Map size</source>
        <translation>Размер на картата</translation>
    </message>
    <message>
        <location line="+6"/>
        <location line="+68"/>
        <source>Width:</source>
        <translation>Ширина:</translation>
    </message>
    <message>
        <location line="-58"/>
        <location line="+26"/>
        <source> tiles</source>
        <extracomment>Remember starting with a space.</extracomment>
        <translation> плочки</translation>
    </message>
    <message>
        <location line="-10"/>
        <location line="+68"/>
        <source>Height:</source>
        <translation>Височина:</translation>
    </message>
    <message>
        <location line="-32"/>
        <source>Tile size</source>
        <translation>Размер на плочката</translation>
    </message>
    <message>
        <location line="+16"/>
        <location line="+26"/>
        <source> px</source>
        <extracomment>Remember starting with a space.</extracomment>
        <translation> пкс</translation>
    </message>
    <message>
        <location line="+55"/>
        <source>Map</source>
        <translation>Карта</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Orientation:</source>
        <translation>Ориентация:</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Tile layer format:</source>
        <translation>Формат на слоевете:</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Tile render order:</source>
        <translation>Ред на изчертаване на плочките:</translation>
    </message>
</context>
<context>
    <name>NewTilesetDialog</name>
    <message>
        <location filename="../src/tiled/newtilesetdialog.ui" line="+14"/>
        <source>New Tileset</source>
        <translation>Нов плочен набор</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>Tileset</source>
        <translation>Плочен набор</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Based on Tileset Image</source>
        <translation>Основан на изображение с плочен набор</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Collection of Images</source>
        <translation>Набор от изображения</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Type:</source>
        <translation>Тип:</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>&amp;Name:</source>
        <translation>&amp;Име:</translation>
    </message>
    <message>
        <location line="+51"/>
        <source>&amp;Browse...</source>
        <translation>&amp;Разглеждане...</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Use transparent color:</source>
        <translation>Използване на цвят за прозрачност:</translation>
    </message>
    <message>
        <location line="+129"/>
        <source>Tile width:</source>
        <translation>Ширина на плочката:</translation>
    </message>
    <message>
        <location line="-100"/>
        <location line="+42"/>
        <location line="+26"/>
        <location line="+16"/>
        <source> px</source>
        <extracomment>Remember starting with a space.</extracomment>
        <translation> пкс</translation>
    </message>
    <message>
        <location line="-142"/>
        <source>Image</source>
        <translation>Изображение</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>Source:</source>
        <translation>Източник:</translation>
    </message>
    <message>
        <location line="+101"/>
        <source>The space at the edges of the tileset.</source>
        <translation>Разстоянието по ръба на плочния набор.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Margin:</source>
        <translation>Кант:</translation>
    </message>
    <message>
        <location line="-45"/>
        <source>Tile height:</source>
        <translation>Височина на плочката:</translation>
    </message>
    <message>
        <location line="+91"/>
        <source>The space between the tiles.</source>
        <translation>Разстоянието между плочките.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Spacing:</source>
        <translation>Отстояние:</translation>
    </message>
</context>
<context>
    <name>ObjectTypes</name>
    <message>
        <location filename="../src/tiled/objecttypes.cpp" line="+38"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+39"/>
        <source>Could not open file.</source>
        <translation>Неуспешно отваряне на файла.</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>File doesn&apos;t contain object types.</source>
        <translation>Файлът не съдържа типове обекти.</translation>
    </message>
    <message>
        <location line="+18"/>
        <source>%3

Line %1, column %2</source>
        <translation>%3

Ред %1, колона %2</translation>
    </message>
</context>
<context>
    <name>OffsetMapDialog</name>
    <message>
        <location filename="../src/tiled/offsetmapdialog.ui" line="+17"/>
        <source>Offset Map</source>
        <translation>Отместване на картата</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Offset Contents of Map</source>
        <translation>Отместване на съдържанието на картата</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>X:</source>
        <translation>X:</translation>
    </message>
    <message>
        <location line="+23"/>
        <location line="+43"/>
        <source>Wrap</source>
        <translation>Превъртане</translation>
    </message>
    <message>
        <location line="-36"/>
        <source>Y:</source>
        <translation>Y:</translation>
    </message>
    <message>
        <location line="+43"/>
        <source>Layers:</source>
        <translation>Слоеве:</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>All Visible Layers</source>
        <translation>Всички видими слоеве</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>All Layers</source>
        <translation>Всички слоеве</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Selected Layer</source>
        <translation>Избрания слой</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Bounds:</source>
        <translation>Граници:</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Whole Map</source>
        <translation>Цялата карта</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Current Selection</source>
        <translation>Текущо избраното</translation>
    </message>
</context>
<context>
    <name>PatreonDialog</name>
    <message>
        <location filename="../src/tiled/patreondialog.ui" line="+14"/>
        <source>Become a Patron</source>
        <translation>Станете патрон</translation>
    </message>
    <message>
        <location line="+18"/>
        <source>Visit https://www.patreon.com/bjorn</source>
        <translation>Към https://www.patreon.com/bjorn</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>I&apos;m already a patron!</source>
        <translation>Аз вече съм патрон!</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Maybe later</source>
        <translation>Може би по-късно</translation>
    </message>
</context>
<context>
    <name>PreferencesDialog</name>
    <message>
        <location filename="../src/tiled/preferencesdialog.ui" line="+14"/>
        <source>Preferences</source>
        <translation>Настройки</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>General</source>
        <translation>Общи</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Saving and Loading</source>
        <translation>Запазване и зареждане</translation>
    </message>
    <message>
        <location filename="../src/tiled/newmapdialog.cpp" line="+62"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+84"/>
        <source>XML</source>
        <translation>XML</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Base64 (uncompressed)</source>
        <translation>Base64 (некомпресиран)</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Base64 (gzip compressed)</source>
        <translation>Base64 (компресиран чрез gzip)</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Base64 (zlib compressed)</source>
        <translation>Base64 (компресиран чрез zlib)</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>CSV</source>
        <translation>CSV</translation>
    </message>
    <message>
        <location line="+2"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+2"/>
        <source>Right Down</source>
        <translation>Надясно-надолу</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Right Up</source>
        <translation>Надясно-нагоре</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Left Down</source>
        <translation>Наляво-надолу</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Left Up</source>
        <translation>Наляво-нагоре</translation>
    </message>
    <message>
        <location filename="../src/tiled/preferencesdialog.ui" line="+6"/>
        <source>&amp;Reload tileset images when they change</source>
        <translation>&amp;Презареждане на изображенията с плочни набори след промяна</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Not enabled by default since a reference to an external DTD is known to cause problems with some XML parsers.</source>
        <translation>Не е включено по подразбиране, тъй като връзката към външно ОТД (DTD) предизвиква проблеми с някои анализатори на XML.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Include &amp;DTD reference in saved maps</source>
        <translation>Включване на &amp;ОТД (DTD) в запазените карти</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Interface</source>
        <translation>Потребителски интерфейс</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>&amp;Language:</source>
        <translation>&amp;Език:</translation>
    </message>
    <message>
        <location line="+220"/>
        <source>Automapping</source>
        <translation>Автокартиране</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Use Automapping, when drawing into layers</source>
        <translation>Използване на автокартиране при чертане в слоевете</translation>
    </message>
    <message>
        <location line="-239"/>
        <source>Hardware &amp;accelerated drawing (OpenGL)</source>
        <translation>&amp;Хардуерно ускорено изчертаване (OpenGL)</translation>
    </message>
    <message>
        <location line="-19"/>
        <source>Open last files on startup</source>
        <translation>Отваряне на предишните файлове при стартиране</translation>
    </message>
    <message>
        <location line="+36"/>
        <source>Grid color:</source>
        <translation>Цвят на решетката:</translation>
    </message>
    <message>
        <location line="+29"/>
        <source>Fine grid divisions:</source>
        <translation>Деления на фината решетка</translation>
    </message>
    <message>
        <location line="+20"/>
        <source> pixels</source>
        <translation> пиксела</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>Object line width:</source>
        <translation>Дебелина на обектния контур:</translation>
    </message>
    <message>
        <location line="+27"/>
        <location line="+6"/>
        <source>Object Types</source>
        <translation>Обектни типове</translation>
    </message>
    <message>
        <location line="+30"/>
        <source>Add Object Type</source>
        <translation>Добавяне на обектен тип</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Add</source>
        <translation>Добавяне</translation>
    </message>
    <message>
        <location line="+17"/>
        <source>Remove Selected Object Types</source>
        <translation>Премахване на избраните обектни типове</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Remove</source>
        <translation>Премахване</translation>
    </message>
    <message>
        <location line="+33"/>
        <source>Import...</source>
        <translation>Внасяне...</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Export...</source>
        <translation>Изнасяне...</translation>
    </message>
</context>
<context>
    <name>Python::PythonMapFormat</name>
    <message>
        <location filename="../src/plugins/python/pythonplugin.cpp" line="+268"/>
        <source>-- Using script %1 to read %2</source>
        <translation>-- Използване на скрипта %1 за прочит на %2</translation>
    </message>
    <message>
        <location line="+28"/>
        <source>-- Using script %1 to write %2</source>
        <translation>-- Използване на скрипта %1 за запис на %2</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>Uncaught exception in script. Please check console.</source>
        <translation>В скрипта беше хвърлено неприхванато изключение. Моля, проверете конзолата.</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Script returned false. Please check console.</source>
        <translation>Скриптът върна като резултат „невярно“. Моля, проверете конзолата.</translation>
    </message>
</context>
<context>
    <name>Python::PythonPlugin</name>
    <message>
        <location line="-164"/>
        <source>Reloading Python scripts</source>
        <translation>Презареждането на скриптовете на Python</translation>
    </message>
</context>
<context>
    <name>QObject</name>
    <message>
        <location filename="../src/automappingconverter/convertercontrol.h" line="+33"/>
        <source>v0.8 and before</source>
        <translation>в. 0.8 или по-стара</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>v0.9 and later</source>
        <translation>в. 0.9 или по-нова</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>unknown</source>
        <translation>непознато</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>not a map</source>
        <translation>не е карта</translation>
    </message>
</context>
<context>
    <name>QtBoolEdit</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertybrowserutils.cpp" line="+233"/>
        <location line="+10"/>
        <location line="+25"/>
        <source>True</source>
        <translation>Да</translation>
    </message>
    <message>
        <location line="-25"/>
        <location line="+25"/>
        <source>False</source>
        <translation>Не</translation>
    </message>
</context>
<context>
    <name>QtBoolPropertyManager</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertymanager.cpp" line="+1696"/>
        <source>True</source>
        <translation>Да</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>False</source>
        <translation>Не</translation>
    </message>
</context>
<context>
    <name>QtCharEdit</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qteditorfactory.cpp" line="+1700"/>
        <source>Clear Char</source>
        <translation>Изчистване на символа</translation>
    </message>
</context>
<context>
    <name>QtColorEditWidget</name>
    <message>
        <location line="+614"/>
        <source>...</source>
        <translation>...</translation>
    </message>
</context>
<context>
    <name>QtColorPropertyManager</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertymanager.cpp" line="+4724"/>
        <source>Red</source>
        <translation>Червено</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Green</source>
        <translation>Зелено</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Blue</source>
        <translation>Синьо</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Alpha</source>
        <translation>Плътност</translation>
    </message>
</context>
<context>
    <name>QtCursorDatabase</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertybrowserutils.cpp" line="-210"/>
        <source>Arrow</source>
        <translation>Стрелка</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Up Arrow</source>
        <translation>Стрелка нагоре</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Cross</source>
        <translation>Кръст</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Wait</source>
        <translation>Изчакване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>IBeam</source>
        <translation>Текстов курсор</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Size Vertical</source>
        <translation>Вертикално оразмеряване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Size Horizontal</source>
        <translation>Хоризонтално оразмеряване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Size Backslash</source>
        <translation>Ляво диагонално оразмеряване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Size Slash</source>
        <translation>Дясно диагонално оразмеряване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Size All</source>
        <translation>Цялостно оразмеряване</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Blank</source>
        <translation>Празно</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Split Vertical</source>
        <translation>Вертикално разделяне</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Split Horizontal</source>
        <translation>Хоризонтално разделяне</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Pointing Hand</source>
        <translation>Посочваща ръка</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Forbidden</source>
        <translation>Забранено</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Open Hand</source>
        <translation>Отворена ръка</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Closed Hand</source>
        <translation>Затворена ръка</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>What&apos;s This</source>
        <translation>Какво е това</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Busy</source>
        <translation>Заето</translation>
    </message>
</context>
<context>
    <name>QtFontEditWidget</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qteditorfactory.cpp" line="+209"/>
        <source>...</source>
        <translation>...</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Select Font</source>
        <translation>Изберете шрифт</translation>
    </message>
</context>
<context>
    <name>QtFontPropertyManager</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertymanager.cpp" line="-350"/>
        <source>Family</source>
        <translation>Семейство</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Point Size</source>
        <translation>Размер</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Bold</source>
        <translation>Получер</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Italic</source>
        <translation>Курсив</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Underline</source>
        <translation>Подчертан</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Strikeout</source>
        <translation>Зачертан</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Kerning</source>
        <translation>Припокриване</translation>
    </message>
</context>
<context>
    <name>QtKeySequenceEdit</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertybrowserutils.cpp" line="+234"/>
        <source>Clear Shortcut</source>
        <translation>Изчистване на комбинацията</translation>
    </message>
</context>
<context>
    <name>QtLocalePropertyManager</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertymanager.cpp" line="-3533"/>
        <source>%1, %2</source>
        <translation>%1, %2</translation>
    </message>
    <message>
        <location line="+53"/>
        <source>Language</source>
        <translation>Език</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Country</source>
        <translation>Държава</translation>
    </message>
</context>
<context>
    <name>QtPointFPropertyManager</name>
    <message>
        <location line="+409"/>
        <source>(%1, %2)</source>
        <translation>(%1, %2)</translation>
    </message>
    <message>
        <location line="+71"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
</context>
<context>
    <name>QtPointPropertyManager</name>
    <message>
        <location line="-319"/>
        <source>(%1, %2)</source>
        <translation>(%1, %2)</translation>
    </message>
    <message>
        <location line="+37"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
</context>
<context>
    <name>QtPropertyBrowserUtils</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertybrowserutils.cpp" line="-141"/>
        <source>[%1, %2, %3] (%4)</source>
        <translation>[%1, %2, %3] (%4)</translation>
    </message>
    <message>
        <location line="+27"/>
        <source>[%1, %2]</source>
        <translation>[%1, %2]</translation>
    </message>
</context>
<context>
    <name>QtRectFPropertyManager</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qtpropertymanager.cpp" line="+1701"/>
        <source>[(%1, %2), %3 x %4]</source>
        <translation>[(%1, %2), %3 х %4]</translation>
    </message>
    <message>
        <location line="+156"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Width</source>
        <translation>Ширина</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Height</source>
        <translation>Височина</translation>
    </message>
</context>
<context>
    <name>QtRectPropertyManager</name>
    <message>
        <location line="-611"/>
        <source>[(%1, %2), %3 x %4]</source>
        <translation>[(%1, %2), %3 x %4]</translation>
    </message>
    <message>
        <location line="+120"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Width</source>
        <translation>Ширина</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Height</source>
        <translation>Височина</translation>
    </message>
</context>
<context>
    <name>QtSizeFPropertyManager</name>
    <message>
        <location line="-534"/>
        <source>%1 x %2</source>
        <translation>%1 х %2</translation>
    </message>
    <message>
        <location line="+130"/>
        <source>Width</source>
        <translation>Ширина</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Height</source>
        <translation>Височина</translation>
    </message>
</context>
<context>
    <name>QtSizePolicyPropertyManager</name>
    <message>
        <location line="+1704"/>
        <location line="+1"/>
        <source>&lt;Invalid&gt;</source>
        <translation>&lt;Неправилно&gt;</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>[%1, %2, %3, %4]</source>
        <translation>[%1, %2, %3, %4]</translation>
    </message>
    <message>
        <location line="+45"/>
        <source>Horizontal Policy</source>
        <translation>Хоризонтално поведение</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Vertical Policy</source>
        <translation>Вертикално поведение</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Horizontal Stretch</source>
        <translation>Хоризонтално разтягане</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Vertical Stretch</source>
        <translation>Вертикално разтягане</translation>
    </message>
</context>
<context>
    <name>QtSizePropertyManager</name>
    <message>
        <location line="-2280"/>
        <source>%1 x %2</source>
        <translation>%1 х %2</translation>
    </message>
    <message>
        <location line="+96"/>
        <source>Width</source>
        <translation>Ширина</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Height</source>
        <translation>Височина</translation>
    </message>
</context>
<context>
    <name>QtTreePropertyBrowser</name>
    <message>
        <location filename="../src/qtpropertybrowser/src/qttreepropertybrowser.cpp" line="+478"/>
        <source>Property</source>
        <translation>Свойство</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Value</source>
        <translation>Стойност</translation>
    </message>
</context>
<context>
    <name>ReplicaIsland::ReplicaIslandPlugin</name>
    <message>
        <location filename="../src/plugins/replicaisland/replicaislandplugin.cpp" line="+59"/>
        <source>Cannot open Replica Island map file!</source>
        <translation>Неуспешно отваряне на файл с карта на Replica Island!</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>Can&apos;t parse file header!</source>
        <translation>Заглавната част на файла не може да бъде прочетена!</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Can&apos;t parse layer header!</source>
        <translation>Заглавната част на слоя не може да бъде прочетена!</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>Inconsistent layer sizes!</source>
        <translation>Размерите на слоевете са несъвместими!</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>File ended in middle of layer!</source>
        <translation>Файлът свършва по средата на слой!</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Unexpected data at end of file!</source>
        <translation>Неочаквани данни в края на файла!</translation>
    </message>
    <message>
        <location line="+64"/>
        <source>Replica Island map files (*.bin)</source>
        <translation>Файлове с карти на Replica Island (*.bin)</translation>
    </message>
    <message>
        <location line="+32"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>You must define a background_index property on the map!</source>
        <translation>Трябва да определите свойство „background_index“ в картата!</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Can&apos;t save non-tile layer!</source>
        <translation>Слой без плочки не може да бъде запазен!</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>You must define a type property on each layer!</source>
        <translation>Трябва да определите свойство „type“ във всеки слой!</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>You must define a tile_index property on each layer!</source>
        <translation>Трябва да определите свойство „tile_index“ във всеки слой!</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>You must define a scroll_speed property on each layer!</source>
        <translation>Трябва да определите свойство „scroll_speed“ във всеки слой!</translation>
    </message>
</context>
<context>
    <name>ResizeDialog</name>
    <message>
        <location filename="../src/tiled/resizedialog.ui" line="+14"/>
        <source>Resize</source>
        <translation>Преоразмеряване</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Size</source>
        <translation>Размер</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Width:</source>
        <translation>Ширина:</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Height:</source>
        <translation>Височина:</translation>
    </message>
    <message>
        <location line="+23"/>
        <source>Offset</source>
        <translation>Отместване</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>X:</source>
        <translation>X:</translation>
    </message>
    <message>
        <location line="+20"/>
        <source>Y:</source>
        <translation>Y:</translation>
    </message>
</context>
<context>
    <name>Tengine::TenginePlugin</name>
    <message>
        <location filename="../src/plugins/tengine/tengineplugin.cpp" line="+49"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+246"/>
        <source>T-Engine4 map files (*.lua)</source>
        <translation>Файлове с карти на T-Engine4 (*.lua)</translation>
    </message>
</context>
<context>
    <name>TileAnimationEditor</name>
    <message>
        <location filename="../src/tiled/tileanimationeditor.ui" line="+14"/>
        <source>Tile Animation Editor</source>
        <translation>Редактор на плочни анимации</translation>
    </message>
    <message>
        <location line="+99"/>
        <location filename="../src/tiled/tileanimationeditor.cpp" line="+507"/>
        <source>Preview</source>
        <translation>Преглед</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::AbstractObjectTool</name>
    <message numerus="yes">
        <location filename="../src/tiled/abstractobjecttool.cpp" line="+182"/>
        <source>Duplicate %n Object(s)</source>
        <translation>
            <numerusform>Копиране на обекта</numerusform>
            <numerusform>Копиране на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+2"/>
        <source>Remove %n Object(s)</source>
        <translation>
            <numerusform>Премахване на обекта</numerusform>
            <numerusform>Премахване на %n обекта</numerusform>
        </translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Flip Horizontally</source>
        <translation>Хоризонтално обръщане</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Flip Vertically</source>
        <translation>Вертикално обръщане</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Raise Object</source>
        <translation>Преместване на обекта нагоре</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>PgUp</source>
        <translation>PgUp</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Lower Object</source>
        <translation>Преместване на обекта надолу</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>PgDown</source>
        <translation>PgDown</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Raise Object to Top</source>
        <translation>Преместване на обекта най-отгоре</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>Home</source>
        <translation>Home</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Lower Object to Bottom</source>
        <translation>Преместване на обекта най-отдолу</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>End</source>
        <translation>End</translation>
    </message>
    <message numerus="yes">
        <location line="+5"/>
        <source>Move %n Object(s) to Layer</source>
        <translation>
            <numerusform>Преместване на обекта в слой</numerusform>
            <numerusform>Преместване на %n обекта в слой</numerusform>
        </translation>
    </message>
    <message>
        <location line="+11"/>
        <source>Object &amp;Properties...</source>
        <translation>&amp;Свойства на обекта...</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::AbstractTileTool</name>
    <message>
        <location filename="../src/tiled/abstracttiletool.cpp" line="+124"/>
        <source>empty</source>
        <translation>празно</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::AutoMapper</name>
    <message>
        <location filename="../src/tiled/automapper.cpp" line="+115"/>
        <source>&apos;%1&apos;: Property &apos;%2&apos; = &apos;%3&apos; does not make sense. Ignoring this property.</source>
        <translation>„%1“: Свойство „%2“ = „%3“ няма смисъл. Това свойство се пренебрегва.</translation>
    </message>
    <message>
        <location line="+71"/>
        <source>Did you forget an underscore in layer &apos;%1&apos;?</source>
        <translation>Забравихте ли подчертаващото тире в слоя „%1“?</translation>
    </message>
    <message>
        <location line="+62"/>
        <source>Layer &apos;%1&apos; is not recognized as a valid layer for Automapping.</source>
        <translation>Слоят „%1“ не е разпознат като подходящ слой за автокартиране.</translation>
    </message>
    <message>
        <location line="-105"/>
        <source>&apos;regions_input&apos; layer must not occur more than once.</source>
        <translation>Слоят „regions_input“ не трябва да присъства повече от веднъж.</translation>
    </message>
    <message>
        <location line="+6"/>
        <location line="+13"/>
        <source>&apos;regions_*&apos; layers must be tile layers.</source>
        <translation>Слоевете от вида „regions_*“ трябва да бъдат слоеве с плочки.</translation>
    </message>
    <message>
        <location line="-6"/>
        <source>&apos;regions_output&apos; layer must not occur more than once.</source>
        <translation>Слоят „regions_output“ не трябва да присъства повече от веднъж.</translation>
    </message>
    <message>
        <location line="+41"/>
        <source>&apos;input_*&apos; and &apos;inputnot_*&apos; layers must be tile layers.</source>
        <translation>Слоевете от вида „input_*“ и „inputnot_*“ трябва да бъдат слоеве с плочки.</translation>
    </message>
    <message>
        <location line="+56"/>
        <source>No &apos;regions&apos; or &apos;regions_input&apos; layer found.</source>
        <translation>Не е открит слой „regions“ или „regions_input“.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>No &apos;regions&apos; or &apos;regions_output&apos; layer found.</source>
        <translation>Не е открит слой „regions“ или „regions_output“.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>No input_&lt;name&gt; layer found!</source>
        <translation>Не е открит слой „input_&lt;име&gt;“!</translation>
    </message>
    <message>
        <location line="+173"/>
        <source>Tile</source>
        <translation>Плочка</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::AutomappingManager</name>
    <message>
        <location filename="../src/tiled/automappingmanager.cpp" line="+103"/>
        <source>Apply AutoMap rules</source>
        <translation>Прилагане на правилата на автокартирането</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>No rules file found at:
%1</source>
        <translation>Не може да бъде открит файл с правила:
%1</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Error opening rules file:
%1</source>
        <translation>Грешка при отварянето на файла с правила:
%1</translation>
    </message>
    <message>
        <location line="+19"/>
        <source>File not found:
%1</source>
        <translation>Файлът не е открит:
%1</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Opening rules map failed:
%1</source>
        <translation>Отварянето на картата с правила беше неуспешно:
%1</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::BucketFillTool</name>
    <message>
        <location filename="../src/tiled/bucketfilltool.cpp" line="+40"/>
        <location line="+175"/>
        <source>Bucket Fill Tool</source>
        <translation>Запълване</translation>
    </message>
    <message>
        <location line="-172"/>
        <location line="+173"/>
        <source>F</source>
        <translation>F</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ClipboardManager</name>
    <message>
        <location filename="../src/tiled/clipboardmanager.cpp" line="+166"/>
        <source>Paste Objects</source>
        <translation>Поставяне на обекти</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CommandButton</name>
    <message>
        <location filename="../src/tiled/commandbutton.cpp" line="+130"/>
        <source>Execute Command</source>
        <translation>Изпълнение на команда</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>F5</source>
        <translation>F5</translation>
    </message>
    <message>
        <location line="-67"/>
        <source>Error Executing Command</source>
        <translation>Грешка при изпълнението на команда</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>You do not have any commands setup.</source>
        <translation>Нямате никакви настроени команди.</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Edit commands...</source>
        <translation>Редактиране на командите...</translation>
    </message>
    <message>
        <location line="+44"/>
        <source>Edit Commands...</source>
        <translation>Редактиране на командите...</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CommandDataModel</name>
    <message>
        <location filename="../src/tiled/commanddatamodel.cpp" line="+60"/>
        <source>Open in text editor</source>
        <translation>Отваряне в текстов редактор</translation>
    </message>
    <message>
        <location line="+92"/>
        <location line="+69"/>
        <source>&lt;new command&gt;</source>
        <translation>&lt;нова команда&gt;</translation>
    </message>
    <message>
        <location line="-61"/>
        <source>Set a name for this command</source>
        <translation>Задайте име за тази команда</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Set the shell command to execute</source>
        <translation>Задайте командата, която да се изпълнява</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Show or hide this command in the command list</source>
        <translation>Показване или скриване на тази команда в списъка с команди</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Add a new command</source>
        <translation>Добавяне на нова команда</translation>
    </message>
    <message>
        <location line="+107"/>
        <source>Name</source>
        <translation>Име</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Command</source>
        <translation>Команда</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Enable</source>
        <translation>Включена</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Move Up</source>
        <translation>Преместване нагоре</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Move Down</source>
        <translation>Преместване надолу</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Execute</source>
        <translation>Изпълнение</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Execute in Terminal</source>
        <translation>Изпълнение в терминал</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>Delete</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location line="+84"/>
        <source>%1 (copy)</source>
        <translation>%1 (копие)</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>New command</source>
        <translation>Нова команда</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CommandDialog</name>
    <message>
        <location filename="../src/tiled/commanddialog.cpp" line="+44"/>
        <source>Edit Commands</source>
        <translation>Редактиране на командите</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CommandProcess</name>
    <message>
        <location filename="../src/tiled/command.cpp" line="+132"/>
        <source>Unable to create/open %1</source>
        <translation>Неуспешно създаване/отваряне на %1</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Unable to add executable permissions to %1</source>
        <translation>Неуспешно добавяне на права за изпълнение на %1</translation>
    </message>
    <message>
        <location line="+26"/>
        <source>The command failed to start.</source>
        <translation>Командата не успя да стартира.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>The command crashed.</source>
        <translation>Командата завърши със срив.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>The command timed out.</source>
        <translation>Командата отне твърде дълго време и беше прекратена.</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>An unknown error occurred.</source>
        <translation>Възникна непозната грешка.</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Error Executing %1</source>
        <translation>Грешка при изпълнението на %1</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ConsoleDock</name>
    <message>
        <location filename="../src/tiled/consoledock.cpp" line="+36"/>
        <source>Debug Console</source>
        <translation>Конзола за отстраняване на грешки</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreateEllipseObjectTool</name>
    <message>
        <location filename="../src/tiled/createellipseobjecttool.cpp" line="+39"/>
        <source>Insert Ellipse</source>
        <translation>Елипса</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>C</source>
        <translation>C</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreateObjectTool</name>
    <message>
        <location filename="../src/tiled/createobjecttool.cpp" line="+46"/>
        <source>O</source>
        <translation>O</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreatePolygonObjectTool</name>
    <message>
        <location filename="../src/tiled/createpolygonobjecttool.cpp" line="+39"/>
        <source>Insert Polygon</source>
        <translation>Многоъгълник</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>P</source>
        <translation>P</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreatePolylineObjectTool</name>
    <message>
        <location filename="../src/tiled/createpolylineobjecttool.cpp" line="+39"/>
        <source>Insert Polyline</source>
        <translation>Начупена линия</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>L</source>
        <translation>L</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreateRectangleObjectTool</name>
    <message>
        <location filename="../src/tiled/createrectangleobjecttool.cpp" line="+39"/>
        <source>Insert Rectangle</source>
        <translation>Правоъгълник</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>R</source>
        <translation>R</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::CreateTileObjectTool</name>
    <message>
        <location filename="../src/tiled/createtileobjecttool.cpp" line="+79"/>
        <source>Insert Tile</source>
        <translation>Плочка</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>T</source>
        <translation>T</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::DocumentManager</name>
    <message>
        <location filename="../src/tiled/documentmanager.cpp" line="+328"/>
        <source>%1:

%2</source>
        <translation>%1:

%2</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::EditPolygonTool</name>
    <message>
        <location filename="../src/tiled/editpolygontool.cpp" line="+129"/>
        <location line="+209"/>
        <source>Edit Polygons</source>
        <translation>Редактиране на многоъгълници</translation>
    </message>
    <message>
        <location line="-207"/>
        <location line="+208"/>
        <source>E</source>
        <translation>E</translation>
    </message>
    <message numerus="yes">
        <location line="+227"/>
        <source>Move %n Point(s)</source>
        <translation>
            <numerusform>Преместване на точката</numerusform>
            <numerusform>Преместване на %n точки</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+26"/>
        <location line="+45"/>
        <source>Delete %n Node(s)</source>
        <translation>
            <numerusform>Изтриване на възела</numerusform>
            <numerusform>Изтриване на %n възела</numerusform>
        </translation>
    </message>
    <message>
        <location line="-40"/>
        <location line="+215"/>
        <source>Join Nodes</source>
        <translation>Сливане на възлите</translation>
    </message>
    <message>
        <location line="-214"/>
        <location line="+250"/>
        <source>Split Segments</source>
        <translation>Разделяне на страните</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::EditTerrainDialog</name>
    <message>
        <location filename="../src/tiled/editterraindialog.cpp" line="+149"/>
        <source>E</source>
        <translation>E</translation>
    </message>
    <message>
        <location line="+35"/>
        <source>New Terrain</source>
        <translation>Нов терен</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::Eraser</name>
    <message>
        <location filename="../src/tiled/eraser.cpp" line="+35"/>
        <location line="+36"/>
        <source>Eraser</source>
        <translation>Гумичка</translation>
    </message>
    <message>
        <location line="-33"/>
        <location line="+34"/>
        <source>E</source>
        <translation>E</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ExportAsImageDialog</name>
    <message>
        <location filename="../src/tiled/exportasimagedialog.cpp" line="+63"/>
        <source>Export</source>
        <translation>Изнасяне</translation>
    </message>
    <message>
        <location line="+73"/>
        <source>Export as Image</source>
        <translation>Изнасяне като изображение</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>%1 already exists.
Do you want to replace it?</source>
        <translation>Вече съществува файл с името %1.
Искате ли да го презапишете?</translation>
    </message>
    <message>
        <location line="+46"/>
        <source>Out of Memory</source>
        <translation>Недостатъчно памет</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Could not allocate sufficient memory for the image. Try reducing the zoom level or using a 64-bit version of Tiled.</source>
        <translation>Не може да бъде заделена достатъчно памет за изображението. Опитайте да намалите степента на приближение или използвайте 64-битова версия на Tiled.</translation>
    </message>
    <message>
        <location line="+11"/>
        <source>Image too Big</source>
        <translation>Изображението е твърде голямо</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>The resulting image would be %1 x %2 pixels and take %3 GB of memory. Tiled is unable to create such an image. Try reducing the zoom level.</source>
        <translation>Изображението ще бъде %1 x %2 пиксела и ще има нужда %3 ГБ памет. Tiled не може да създаде толкова голямо изображение. Опитайте да намалите степента на приближение.</translation>
    </message>
    <message>
        <location line="+93"/>
        <source>Image</source>
        <translation>Изображение</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::FileChangedWarning</name>
    <message>
        <location filename="../src/tiled/documentmanager.cpp" line="-266"/>
        <source>File change detected. Discard changes and reload the map?</source>
        <translation>Засечена е промяна по файла. Искате ли да отхвърлите промените и да презаредите картата?</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::FileEdit</name>
    <message>
        <location filename="../src/tiled/fileedit.cpp" line="+113"/>
        <source>Choose a File</source>
        <translation>Изберете файл</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ImageMovementTool</name>
    <message>
        <location filename="../src/tiled/imagemovementtool.cpp" line="+35"/>
        <location line="+65"/>
        <source>Move Images</source>
        <translation>Преместване на изображения</translation>
    </message>
    <message>
        <location line="-63"/>
        <location line="+64"/>
        <source>M</source>
        <translation>M</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::LayerDock</name>
    <message>
        <location filename="../src/tiled/layerdock.cpp" line="+218"/>
        <source>Layers</source>
        <translation>Слоеве</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Opacity:</source>
        <translation>Плътност:</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::LayerModel</name>
    <message>
        <location filename="../src/tiled/layermodel.cpp" line="+151"/>
        <source>Layer</source>
        <translation>Слой</translation>
    </message>
    <message>
        <location line="+152"/>
        <source>Show Other Layers</source>
        <translation>Показване на другите слоеве</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Hide Other Layers</source>
        <translation>Скриване на другите слоеве</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MagicWandTool</name>
    <message>
        <location filename="../src/tiled/magicwandtool.cpp" line="+40"/>
        <location line="+52"/>
        <source>Magic Wand</source>
        <translation>Магическа пръчка</translation>
    </message>
    <message>
        <location line="-49"/>
        <location line="+50"/>
        <source>W</source>
        <translation>W</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MainWindow</name>
    <message>
        <location filename="../src/tiled/mainwindow.cpp" line="+179"/>
        <location line="+11"/>
        <source>Undo</source>
        <translation>Отмяна</translation>
    </message>
    <message>
        <location line="-10"/>
        <location line="+9"/>
        <source>Redo</source>
        <translation>Повторение</translation>
    </message>
    <message>
        <location line="+82"/>
        <source>Ctrl+T</source>
        <translation>Ctrl+T</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Ctrl+=</source>
        <translation>Ctrl+=</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>+</source>
        <translation>+</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>-</source>
        <translation>-</translation>
    </message>
    <message>
        <location line="+23"/>
        <location line="+1365"/>
        <source>Random Mode</source>
        <translation>Случаен режим</translation>
    </message>
    <message>
        <location line="-1362"/>
        <source>D</source>
        <translation>D</translation>
    </message>
    <message>
        <location line="+3"/>
        <location line="+1360"/>
        <source>&amp;Layer</source>
        <translation>&amp;Слой</translation>
    </message>
    <message>
        <location line="-1182"/>
        <source>Ctrl+Shift+O</source>
        <translation>Ctrl+Shift+O</translation>
    </message>
    <message>
        <location line="+30"/>
        <source>Ctrl+Shift+Tab</source>
        <translation>Ctrl+Shift+Tab</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Ctrl+Tab</source>
        <translation>Ctrl+Tab</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Z</source>
        <translation>Z</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Shift+Z</source>
        <translation>Shift+Z</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Alt+C</source>
        <translation>Alt+C</translation>
    </message>
    <message>
        <location line="+130"/>
        <source>Error Opening Map</source>
        <translation>Грешка при отварянето на картата</translation>
    </message>
    <message>
        <location line="+81"/>
        <location line="+181"/>
        <source>All Files (*)</source>
        <translation>Всички файлове (*)</translation>
    </message>
    <message>
        <location line="-178"/>
        <location line="+56"/>
        <source>Tiled map files (*.tmx)</source>
        <translation>Файлове с карти на Tiled (*.tmx)</translation>
    </message>
    <message>
        <location line="-48"/>
        <source>Open Map</source>
        <translation>Отваряне на карта</translation>
    </message>
    <message>
        <location line="+25"/>
        <location line="+73"/>
        <source>Error Saving Map</source>
        <translation>Грешка при запазването на картата</translation>
    </message>
    <message>
        <location line="-31"/>
        <source>untitled.tmx</source>
        <translation>неименувана.tmx</translation>
    </message>
    <message>
        <location line="+47"/>
        <source>Unsaved Changes</source>
        <translation>Незапазени промени</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>There are unsaved changes. Do you want to save now?</source>
        <translation>Има незапазени промени. Искате ли да ги запазите сега?</translation>
    </message>
    <message>
        <location line="+37"/>
        <source>Exported to %1</source>
        <translation>Изнесено като %1</translation>
    </message>
    <message>
        <location line="+5"/>
        <location line="+117"/>
        <source>Error Exporting Map</source>
        <translation>Грешка при изнасянето на картата</translation>
    </message>
    <message>
        <location line="-80"/>
        <source>Export As...</source>
        <translation>Изнасяне като...</translation>
    </message>
    <message>
        <location line="+19"/>
        <source>Non-unique file extension</source>
        <translation>Файловото разширение не е уникално</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Non-unique file extension.
Please select specific format.</source>
        <translation>Файловото разширение не е уникално.
Моля, изберете конкретен формат.</translation>
    </message>
    <message>
        <location line="+16"/>
        <source>Unknown File Format</source>
        <translation>Непознат формат на файла</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>The given filename does not have any known file extension.</source>
        <translation>Посоченият файл има непознато разширение.</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Some export files already exist:</source>
        <translation>Някои файлове за изнасяне вече съществуват:</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Do you want to replace them?</source>
        <translation>Искате ли да ги презапишете?</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Overwrite Files</source>
        <translation>Презаписване на файловете</translation>
    </message>
    <message>
        <location line="+71"/>
        <source>Cut</source>
        <translation>Изрязване</translation>
    </message>
    <message>
        <location line="+555"/>
        <source>[*]%1</source>
        <translation>[*]%1</translation>
    </message>
    <message>
        <location line="+130"/>
        <source>Error Reloading Map</source>
        <translation>Грешка при презареждането на картата</translation>
    </message>
    <message>
        <location line="-609"/>
        <source>Delete</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location line="+103"/>
        <source>Tiled tileset files (*.tsx)</source>
        <translation>Файлове с плочни набори на Tiled (*.tsx)</translation>
    </message>
    <message>
        <location line="+16"/>
        <location line="+5"/>
        <source>Error Reading Tileset</source>
        <translation>Грешка при прочитането на плочния набор</translation>
    </message>
    <message>
        <location line="+77"/>
        <source>Automatic Mapping Warning</source>
        <translation>Предупреждение за автоматичното картиране</translation>
    </message>
    <message>
        <location line="-12"/>
        <source>Automatic Mapping Error</source>
        <translation>Грешка при автоматичното картиране</translation>
    </message>
    <message>
        <location line="-870"/>
        <location line="+1188"/>
        <source>Views and Toolbars</source>
        <translation>Изгледи и ленти с инструменти</translation>
    </message>
    <message>
        <location line="-1187"/>
        <location line="+1188"/>
        <source>Tile Animation Editor</source>
        <translation>Редактор на плочни анимации</translation>
    </message>
    <message>
        <location line="-1186"/>
        <location line="+1187"/>
        <source>Tile Collision Editor</source>
        <translation>Редактор на плочни колизии</translation>
    </message>
    <message>
        <location line="-1158"/>
        <source>Alt+Left</source>
        <translation>Alt+Наляво</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Alt+Right</source>
        <translation>Alt+Надясно</translation>
    </message>
    <message>
        <location line="+743"/>
        <source>Add External Tileset(s)</source>
        <translation>Добавяне на външен плочен набор (или набори)</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>%1: %2</source>
        <translation>%1: %2</translation>
    </message>
    <message numerus="yes">
        <location line="+10"/>
        <source>Add %n Tileset(s)</source>
        <translation>
            <numerusform>Добавяне на плочния набор</numerusform>
            <numerusform>Добавяне на %n почни набора</numerusform>
        </translation>
    </message>
    <message>
        <location line="+201"/>
        <source>Current layer: %1</source>
        <translation>Текущ слой: %1</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&lt;none&gt;</source>
        <translation>&lt;никой&gt;</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MapDocument</name>
    <message>
        <location filename="../src/tiled/mapdocument.cpp" line="+242"/>
        <source>untitled.tmx</source>
        <translation>неименувана.tmx</translation>
    </message>
    <message>
        <location line="+90"/>
        <source>Resize Map</source>
        <translation>Преоразмеряване на картата</translation>
    </message>
    <message>
        <location line="+50"/>
        <source>Offset Map</source>
        <translation>Отместване на картата</translation>
    </message>
    <message numerus="yes">
        <location line="+28"/>
        <source>Rotate %n Object(s)</source>
        <translation>
            <numerusform>Завъртане на обекта</numerusform>
            <numerusform>Завъртане на %n обекта</numerusform>
        </translation>
    </message>
    <message>
        <location line="+35"/>
        <source>Tile Layer %1</source>
        <translation>Слой с плочки %1</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Object Layer %1</source>
        <translation>Слой с обекти %1</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Image Layer %1</source>
        <translation>Слой с изображения %1</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Copy of %1</source>
        <translation>Копие на %1</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Duplicate Layer</source>
        <translation>Копиране на слоя</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>Merge Layer Down</source>
        <translation>Сливане на слоя с долния</translation>
    </message>
    <message>
        <location line="+203"/>
        <source>Tile</source>
        <translation>Плочка</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Tileset Changes</source>
        <translation>Промени в плочния набор</translation>
    </message>
    <message numerus="yes">
        <location line="+189"/>
        <source>Duplicate %n Object(s)</source>
        <translation>
            <numerusform>Копиране на обекта</numerusform>
            <numerusform>Копиране на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+20"/>
        <source>Remove %n Object(s)</source>
        <translation>
            <numerusform>Премахване на обекта</numerusform>
            <numerusform>Премахване на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+12"/>
        <source>Move %n Object(s) to Layer</source>
        <translation>
            <numerusform>Преместване на обекта в слой</numerusform>
            <numerusform>Преместване на %n обекта в слой</numerusform>
        </translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MapDocumentActionHandler</name>
    <message>
        <location filename="../src/tiled/mapdocumentactionhandler.cpp" line="+55"/>
        <source>Ctrl+Shift+A</source>
        <translation>Ctrl+Shift+A</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Ctrl+Shift+D</source>
        <translation>Ctrl+Shift+D</translation>
    </message>
    <message>
        <location line="+17"/>
        <source>Ctrl+Shift+Up</source>
        <translation>Ctrl+Shift+Нагоре</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Ctrl+Shift+Down</source>
        <translation>Ctrl+Shift+Надолу</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Ctrl+Shift+H</source>
        <translation>Ctrl+Shift+H</translation>
    </message>
    <message>
        <location line="+58"/>
        <source>Select &amp;All</source>
        <translation>Избиране на &amp;всичко</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Select &amp;None</source>
        <translation>Избиране на ни&amp;що</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Crop to Selection</source>
        <translation>О&amp;трязване на избраното</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Add &amp;Tile Layer</source>
        <translation>Добавяне на слой с &amp;плочки</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Add &amp;Object Layer</source>
        <translation>Добавяне на слой с &amp;обекти</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Select Pre&amp;vious Layer</source>
        <translation>Избиране на п&amp;редходния слой</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Select &amp;Next Layer</source>
        <translation>Избиране на &amp;следващия слой</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>R&amp;aise Layer</source>
        <translation>Преместване на слоя на&amp;горе</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Lower Layer</source>
        <translation>Преместване на слоя на&amp;долу</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Show/&amp;Hide all Other Layers</source>
        <translation>Показване/скриване на &amp;всички останали слоеве</translation>
    </message>
    <message numerus="yes">
        <location line="+248"/>
        <source>Duplicate %n Object(s)</source>
        <translation>
            <numerusform>Копиране на обекта</numerusform>
            <numerusform>Копиране на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+1"/>
        <source>Remove %n Object(s)</source>
        <translation>
            <numerusform>Премахване на обекта</numerusform>
            <numerusform>Премахване на %n обекта</numerusform>
        </translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Duplicate Objects</source>
        <translation>Копиране на обектите</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Remove Objects</source>
        <translation>Премахване на обектите</translation>
    </message>
    <message>
        <location line="-259"/>
        <source>&amp;Duplicate Layer</source>
        <translation>&amp;Копиране на слоя</translation>
    </message>
    <message>
        <location line="-80"/>
        <source>Ctrl+PgUp</source>
        <translation>Ctrl+PgUp</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Ctrl+PgDown</source>
        <translation>Ctrl+PgDown</translation>
    </message>
    <message>
        <location line="+76"/>
        <source>Add &amp;Image Layer</source>
        <translation>Добавяне на слой с &amp;изображения</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>&amp;Merge Layer Down</source>
        <translation>С&amp;ливане на слоя с долния</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Remove Layer</source>
        <translation>Према&amp;хване на слоя</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Layer &amp;Properties...</source>
        <translation>Свойс&amp;тва на слоя</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MapObjectModel</name>
    <message>
        <location filename="../src/tiled/mapobjectmodel.cpp" line="+152"/>
        <source>Change Object Name</source>
        <translation>Преименуване на обекта</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Change Object Type</source>
        <translation>Промяна на типа на обекта</translation>
    </message>
    <message>
        <location line="+50"/>
        <source>Name</source>
        <translation>Име</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Type</source>
        <translation>Тип</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MapsDock</name>
    <message>
        <location filename="../src/tiled/mapsdock.cpp" line="+83"/>
        <source>Browse...</source>
        <translation>Разглеждане...</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Choose the Maps Folder</source>
        <translation>Изберете папката с картите</translation>
    </message>
    <message>
        <location line="+34"/>
        <source>Maps</source>
        <translation>Карти</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::MiniMapDock</name>
    <message>
        <location filename="../src/tiled/minimapdock.cpp" line="+60"/>
        <source>Mini-map</source>
        <translation>Мини-карта</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::NewMapDialog</name>
    <message>
        <location filename="../src/tiled/newmapdialog.cpp" line="+2"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="-14"/>
        <source>Orthogonal</source>
        <translation>Ортогонална</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Isometric</source>
        <translation>Изометрична</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Isometric (Staggered)</source>
        <translation>Изометрична (размината)</translation>
    </message>
    <message>
        <location line="+1"/>
        <location filename="../src/tiled/propertybrowser.cpp" line="+1"/>
        <source>Hexagonal (Staggered)</source>
        <translation>Шестоъгълна (размината)</translation>
    </message>
    <message>
        <location line="+60"/>
        <source>Tile Layer 1</source>
        <translation>Слой с плочки 1</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Memory Usage Warning</source>
        <translation>Предупреждение за използваната памет</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Tile layers for this map will consume %L1 GB of memory each. Not creating one by default.</source>
        <translation>Всеки от слоевете с плочки в тази карта ще използва %L1 ГБ памет. Обикновено би трябвало да бъде създаден един слой с плочки, но в този случай това няма да стане.</translation>
    </message>
    <message>
        <location line="+49"/>
        <source>%1 x %2 pixels</source>
        <translation>%1 х %2 пиксела</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::NewTilesetDialog</name>
    <message>
        <location filename="../src/tiled/newtilesetdialog.cpp" line="+151"/>
        <location line="+7"/>
        <source>Error</source>
        <translation>Грешка</translation>
    </message>
    <message>
        <location line="-6"/>
        <source>Failed to load tileset image &apos;%1&apos;.</source>
        <translation>Неуспешно зареждане на изображение с плочен набор „%1“.</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>No tiles found in the tileset image when using the given tile size, margin and spacing!</source>
        <translation>В изображението с плочния набор не са открити никакви плочки при зададените размер на плочка, кант и отстояние!</translation>
    </message>
    <message>
        <location line="+24"/>
        <source>Tileset Image</source>
        <translation>Изображение с плочен набор</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ObjectSelectionTool</name>
    <message>
        <location filename="../src/tiled/objectselectiontool.cpp" line="+316"/>
        <location line="+302"/>
        <source>Select Objects</source>
        <translation>Избиране на обекти</translation>
    </message>
    <message>
        <location line="-300"/>
        <location line="+301"/>
        <source>S</source>
        <translation>S</translation>
    </message>
    <message numerus="yes">
        <location line="-190"/>
        <location line="+548"/>
        <source>Move %n Object(s)</source>
        <translation>
            <numerusform>Преместване на обекта</numerusform>
            <numerusform>Преместване на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+67"/>
        <source>Rotate %n Object(s)</source>
        <translation>
            <numerusform>Завъртане на обекта</numerusform>
            <numerusform>Завъртане на %n обекта</numerusform>
        </translation>
    </message>
    <message numerus="yes">
        <location line="+266"/>
        <source>Resize %n Object(s)</source>
        <translation>
            <numerusform>Преоразмеряване на обекта</numerusform>
            <numerusform>Преоразмеряване на %n обекта</numerusform>
        </translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ObjectTypesModel</name>
    <message>
        <location filename="../src/tiled/objecttypesmodel.cpp" line="+51"/>
        <source>Type</source>
        <translation>Тип</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Color</source>
        <translation>Цвят</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::ObjectsDock</name>
    <message>
        <location filename="../src/tiled/objectsdock.cpp" line="+145"/>
        <source>Object Properties</source>
        <translation>Свойства на обекта</translation>
    </message>
    <message>
        <location line="-1"/>
        <source>Add Object Layer</source>
        <translation>Добавяне на слой с обекти</translation>
    </message>
    <message>
        <location line="-2"/>
        <source>Objects</source>
        <translation>Обекти</translation>
    </message>
    <message numerus="yes">
        <location line="+17"/>
        <source>Move %n Object(s) to Layer</source>
        <translation>
            <numerusform>Преместване на обекта в слой</numerusform>
            <numerusform>Преместване на %n обекта в слой</numerusform>
        </translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::PatreonDialog</name>
    <message>
        <location filename="../src/tiled/patreondialog.cpp" line="+66"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;
&lt;h3&gt;Thank you for support!&lt;/h3&gt;
&lt;p&gt;Your support as a patron makes a big difference to me as the main developer and maintainer of Tiled. It allows me to spend less time working for money elsewhere and spend more time working on Tiled instead.&lt;/p&gt;
&lt;p&gt;Keep an eye out for exclusive updates in the Activity feed on my Patreon page to find out what I&apos;ve been up to in the time I could spend on Tiled thanks to your support!&lt;/p&gt;
&lt;p&gt;&lt;i&gt;Thorbj&amp;oslash;rn Lindeijer&lt;/i&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;
&lt;h3&gt;Благодаря Ви за подкрепата!&lt;/h3&gt;
&lt;p&gt;Подкрепата Ви като патрон означава много за мен, като основен разработчик на Tiled. Тя ми позволява да прекарвам по-малко време, работейки някъде за заплата, и да влагам повече време в разработката на Tiled.&lt;/p&gt;
&lt;p&gt;Следете обновленията на страницата ми в Patreon, за да знаете върху какво работя през времето, което мога да отделям на Tiled, благодарение на Вашата подкрепа!&lt;/p&gt;
&lt;p&gt;&lt;i&gt;Thorbj&amp;oslash;rn Lindeijer&lt;/i&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>I&apos;m no longer a patron</source>
        <translation>Вече не съм патрон</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>&lt;html&gt;&lt;head/&gt;&lt;body&gt;
&lt;h3&gt;With your help I can continue to improve Tiled!&lt;/h3&gt;
&lt;p&gt;Please consider supporting me as a patron. Your support would make a big difference to me, the main developer and maintainer of Tiled. I could spend less time working for money elsewhere and spend more time working on Tiled instead.&lt;/p&gt;
&lt;p&gt;Every little bit helps. Tiled has a lot of users and if each would contribute a small donation each month I will have time to make sure Tiled keeps getting better.&lt;/p&gt;
&lt;p&gt;&lt;i&gt;Thorbj&amp;oslash;rn Lindeijer&lt;/i&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</source>
        <translation>&lt;html&gt;&lt;head/&gt;&lt;body&gt;
&lt;h3&gt;С Ваша помощ мога да продължа да подобрявам Tiled!&lt;/h3&gt;
&lt;p&gt;Моля, обмислете възможността да ме подкрепите като патрон. Подкрепата Ви ще означава много за мен – основният разработчик на Tiled. Така бих могъл да прекарвам по-малко време, работейки някъде за заплата, и да влагам повече време в разработката на Tiled.&lt;/p&gt;
&lt;p&gt;Всеки може да помогне, дори и с малко. Tiled има много потребители, и ако всеки от тях дарява по мъничко всеки месец, аз ще имам достатъчно време, за да продължавам да го подобрявам.&lt;/p&gt;
&lt;p&gt;&lt;i&gt;Thorbj&amp;oslash;rn Lindeijer&lt;/i&gt;&lt;/p&gt;&lt;/body&gt;&lt;/html&gt;</translation>
    </message>
    <message>
        <location line="+12"/>
        <source>I&apos;m already a patron!</source>
        <translation>Аз вече съм патрон!</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::PreferencesDialog</name>
    <message>
        <location filename="../src/tiled/preferencesdialog.cpp" line="+121"/>
        <location line="+60"/>
        <source>System default</source>
        <translation>От системата</translation>
    </message>
    <message>
        <location line="+74"/>
        <source>Import Object Types</source>
        <translation>Внасяне на обектни типове</translation>
    </message>
    <message>
        <location line="+2"/>
        <location line="+29"/>
        <source>Object Types files (*.xml)</source>
        <translation>Файлове с обектни типове (*.xml)</translation>
    </message>
    <message>
        <location line="-16"/>
        <source>Error Reading Object Types</source>
        <translation>Грешка при четенето на обектните типове</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Export Object Types</source>
        <translation>Изнасяне на обектни типове</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Error Writing Object Types</source>
        <translation>Грешка при записа на обектните типове</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::PropertiesDock</name>
    <message>
        <location filename="../src/tiled/propertiesdock.cpp" line="+196"/>
        <location line="+52"/>
        <source>Name:</source>
        <translation>Име:</translation>
    </message>
    <message>
        <location line="-51"/>
        <location line="+103"/>
        <source>Add Property</source>
        <translation>Добавяне на свойство</translation>
    </message>
    <message>
        <location line="-50"/>
        <location line="+52"/>
        <source>Rename Property</source>
        <translation>Преименуване на свойството</translation>
    </message>
    <message>
        <location line="-4"/>
        <source>Properties</source>
        <translation>Свойства</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Remove Property</source>
        <translation>Премахване на свойството</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::PropertyBrowser</name>
    <message>
        <location filename="../src/tiled/propertybrowser.cpp" line="+13"/>
        <source>Horizontal</source>
        <translation>Хоризонтално</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Vertical</source>
        <translation>Вертикално</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Top Down</source>
        <translation>Отгоре-надолу</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Manual</source>
        <translation>Ръчно</translation>
    </message>
    <message>
        <location line="+436"/>
        <source>Relative chance this tile will be picked</source>
        <translation>Относителен шанс тази плочка да бъде избрана</translation>
    </message>
    <message>
        <location line="+375"/>
        <source>Custom Properties</source>
        <translation>Допълнителни свойства</translation>
    </message>
    <message>
        <location line="-558"/>
        <source>Map</source>
        <translation>Карта</translation>
    </message>
    <message>
        <location line="+36"/>
        <source>Tile Layer Format</source>
        <translation>Формат на слоевете</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Tile Render Order</source>
        <translation>Ред на изчерт. на плочките</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Background Color</source>
        <translation>Цвят на фона</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Object</source>
        <translation>Обект</translation>
    </message>
    <message>
        <location line="+3"/>
        <location line="+26"/>
        <location line="+59"/>
        <location line="+40"/>
        <source>Name</source>
        <translation>Име</translation>
    </message>
    <message>
        <location line="-122"/>
        <source>Type</source>
        <translation>Тип</translation>
    </message>
    <message>
        <location line="+3"/>
        <location line="+21"/>
        <source>Visible</source>
        <translation>Видим</translation>
    </message>
    <message>
        <location line="-372"/>
        <location line="+352"/>
        <location line="+70"/>
        <source>X</source>
        <translation>X</translation>
    </message>
    <message>
        <location line="-421"/>
        <location line="+352"/>
        <location line="+70"/>
        <source>Y</source>
        <translation>Y</translation>
    </message>
    <message>
        <location line="-420"/>
        <source>Odd</source>
        <translation>Нечетна</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Even</source>
        <translation>Четна</translation>
    </message>
    <message>
        <location line="+280"/>
        <source>Orientation</source>
        <translation>Ориентация</translation>
    </message>
    <message>
        <location line="+5"/>
        <location line="+65"/>
        <source>Width</source>
        <translation>Ширина</translation>
    </message>
    <message>
        <location line="-64"/>
        <location line="+65"/>
        <source>Height</source>
        <translation>Височина</translation>
    </message>
    <message>
        <location line="-64"/>
        <location line="+147"/>
        <source>Tile Width</source>
        <translation>Ширина на плочката</translation>
    </message>
    <message>
        <location line="-146"/>
        <location line="+147"/>
        <source>Tile Height</source>
        <translation>Височина на плочката</translation>
    </message>
    <message>
        <location line="-145"/>
        <source>Tile Side Length (Hex)</source>
        <translation>Страна на плочката (шест.)</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Stagger Axis</source>
        <translation>Ос на разминаване</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Stagger Index</source>
        <translation>Номерация на разминаване</translation>
    </message>
    <message>
        <location line="+49"/>
        <source>Rotation</source>
        <translation>Завъртане</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Flipping</source>
        <translation>Обръщане</translation>
    </message>
    <message>
        <location line="+14"/>
        <source>Opacity</source>
        <translation>Плътност</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Horizontal Offset</source>
        <translation>Хоризонтално отместване</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Vertical Offset</source>
        <translation>Вертикално отместване</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Tile Layer</source>
        <translation>Слой с плочки</translation>
    </message>
    <message>
        <location line="+7"/>
        <source>Object Layer</source>
        <translation>Слой с обекти</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Color</source>
        <translation>Цвят</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Drawing Order</source>
        <translation>Ред на изчертаване</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Image Layer</source>
        <translation>Слой с изображения</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Image</source>
        <translation>Изображение</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Transparent Color</source>
        <translation>Цвят за прозрачност</translation>
    </message>
    <message>
        <location line="+8"/>
        <source>Tileset</source>
        <translation>Плочен набор</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Drawing Offset</source>
        <translation>Отместване при изчертаване</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Source Image</source>
        <translation>Изображение източник</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Margin</source>
        <translation>Кант</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Spacing</source>
        <translation>Отстояние</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Tile</source>
        <translation>Плочка</translation>
    </message>
    <message>
        <location line="-110"/>
        <location line="+111"/>
        <source>ID</source>
        <translation>Ид.</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Probability</source>
        <translation>Вероятност</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Terrain</source>
        <translation>Терен</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::SelectSameTileTool</name>
    <message>
        <location filename="../src/tiled/selectsametiletool.cpp" line="+50"/>
        <location line="+57"/>
        <source>Select Same Tile</source>
        <translation>Избиране на същите плочки</translation>
    </message>
    <message>
        <location line="-54"/>
        <location line="+55"/>
        <source>S</source>
        <translation>S</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::StampBrush</name>
    <message>
        <location filename="../src/tiled/stampbrush.cpp" line="+41"/>
        <location line="+128"/>
        <source>Stamp Brush</source>
        <translation>Печат</translation>
    </message>
    <message>
        <location line="-125"/>
        <location line="+126"/>
        <source>B</source>
        <translation>B</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TerrainBrush</name>
    <message>
        <location filename="../src/tiled/terrainbrush.cpp" line="+45"/>
        <location line="+115"/>
        <source>Terrain Brush</source>
        <translation>Терен</translation>
    </message>
    <message>
        <location line="-112"/>
        <location line="+113"/>
        <source>T</source>
        <translation>T</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TerrainDock</name>
    <message>
        <location filename="../src/tiled/terraindock.cpp" line="+174"/>
        <source>Terrains</source>
        <translation>Терени</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TerrainView</name>
    <message>
        <location filename="../src/tiled/terrainview.cpp" line="+97"/>
        <source>Terrain &amp;Properties...</source>
        <translation>&amp;Свойства на терена</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TileAnimationEditor</name>
    <message>
        <location filename="../src/tiled/tileanimationeditor.cpp" line="-56"/>
        <source>Delete Frames</source>
        <translation>Изтриване на кадрите</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TileCollisionEditor</name>
    <message>
        <location filename="../src/tiled/tilecollisioneditor.cpp" line="+337"/>
        <source>Delete</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location line="+0"/>
        <source>Cut</source>
        <translation>Изрязване</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Tile Collision Editor</source>
        <translation>Редактор на плочни колизии</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TileSelectionTool</name>
    <message>
        <location filename="../src/tiled/tileselectiontool.cpp" line="+34"/>
        <location line="+81"/>
        <source>Rectangular Select</source>
        <translation>Правоъгълно избиране</translation>
    </message>
    <message>
        <location line="-78"/>
        <location line="+79"/>
        <source>R</source>
        <translation>R</translation>
    </message>
    <message>
        <location line="-56"/>
        <source>%1, %2 - Rectangle: (%3 x %4)</source>
        <translation>%1, %2 – правоъгълник: (%3 х %4)</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TileStampModel</name>
    <message>
        <location filename="../src/tiled/tilestampmodel.cpp" line="+78"/>
        <source>Stamp</source>
        <translation>Печат</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Probability</source>
        <translation>Вероятност</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TileStampsDock</name>
    <message>
        <location filename="../src/tiled/tilestampsdock.cpp" line="+196"/>
        <source>Delete Stamp</source>
        <translation>Изтриване на печата</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Remove Variation</source>
        <translation>Изтриване на отклонението</translation>
    </message>
    <message>
        <location line="+71"/>
        <source>Choose the Stamps Folder</source>
        <translation>Изберете папка с печати</translation>
    </message>
    <message>
        <location line="+15"/>
        <source>Tile Stamps</source>
        <translation>Плочни печати</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Add New Stamp</source>
        <translation>Добавяне на нов печат</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Add Variation</source>
        <translation>Добавяне на отклонение</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Duplicate Stamp</source>
        <translation>Копиране на печата</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Delete Selected</source>
        <translation>Изтриване на избрания</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Set Stamps Folder</source>
        <translation>Задаване на папка с печати</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Filter</source>
        <translation>Филтриране</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TilesetDock</name>
    <message>
        <location filename="../src/tiled/tilesetdock.cpp" line="+658"/>
        <source>Remove Tileset</source>
        <translation>Премахване на плочния набор</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>The tileset &quot;%1&quot; is still in use by the map!</source>
        <translation>Плочният набор „%1“ все още се използва от картата!</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Remove this tileset and all references to the tiles in this tileset?</source>
        <translation>Искате ли да премахнете този плочен набор и всички връзки към плочките от него?</translation>
    </message>
    <message>
        <location line="+74"/>
        <source>Tilesets</source>
        <translation>Плочни набори</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>New Tileset</source>
        <translation>Нов плочен набор</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Import Tileset</source>
        <translation>&amp;Внасяне на плочен набор</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Export Tileset As...</source>
        <translation>&amp;Изнасяне на плочния набор като...</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Tile&amp;set Properties</source>
        <translation>&amp;Свойства на плочния набор...</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&amp;Remove Tileset</source>
        <translation>&amp;Премахване на плочния набор</translation>
    </message>
    <message>
        <location line="+2"/>
        <location line="+115"/>
        <location line="+13"/>
        <source>Add Tiles</source>
        <translation>Добавяне на плочки</translation>
    </message>
    <message>
        <location line="-127"/>
        <location line="+176"/>
        <location line="+13"/>
        <source>Remove Tiles</source>
        <translation>Премахване на плочките</translation>
    </message>
    <message>
        <location line="-111"/>
        <source>Error saving tileset: %1</source>
        <translation>Грешка при запазването на плочния набор: %1</translation>
    </message>
    <message>
        <location line="+50"/>
        <source>Could not load &quot;%1&quot;!</source>
        <translation>Неуспешно зареждане на „%1“!</translation>
    </message>
    <message>
        <location line="+49"/>
        <source>One or more of the tiles to be removed are still in use by the map!</source>
        <translation>Една или повече от плочките, които искате да бъдат премахнати, все още се използват от картата!</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Remove all references to these tiles?</source>
        <translation>Искате ли да премахнете всички връзки към тези плочки?</translation>
    </message>
    <message>
        <location line="-184"/>
        <source>Edit &amp;Terrain Information</source>
        <translation>Редактиране на &amp;теренната информация</translation>
    </message>
    <message>
        <location line="+56"/>
        <location line="+23"/>
        <source>Export Tileset</source>
        <translation>Изнасяне на плочен набор</translation>
    </message>
    <message>
        <location line="-39"/>
        <source>Tiled tileset files (*.tsx)</source>
        <translation>Файлове с плочни набори на Tiled (*.tsx)</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TilesetView</name>
    <message>
        <location filename="../src/tiled/tilesetview.cpp" line="+569"/>
        <source>Add Terrain Type</source>
        <translation>Добавяне на теренен тип</translation>
    </message>
    <message>
        <location line="+5"/>
        <source>Set Terrain Image</source>
        <translation>Задаване на изображение за терена</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Tile &amp;Properties...</source>
        <translation>&amp;Свойства на плочката</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Show &amp;Grid</source>
        <translation>Показване на &amp;решетката</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TmxMapFormat</name>
    <message>
        <location filename="../src/tiled/tmxmapformat.h" line="+62"/>
        <source>Tiled map files (*.tmx)</source>
        <translation>Файлове с карти на Tiled (*.tmx)</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::TsxTilesetFormat</name>
    <message>
        <location line="+24"/>
        <source>Tiled tileset files (*.tsx)</source>
        <translation>Файлове с плочни набори на Tiled (*.tsx)</translation>
    </message>
</context>
<context>
    <name>Tiled::Internal::UndoDock</name>
    <message>
        <location filename="../src/tiled/undodock.cpp" line="+64"/>
        <source>History</source>
        <translation>История</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>&lt;empty&gt;</source>
        <translation>&lt;празно&gt;</translation>
    </message>
</context>
<context>
    <name>Tmw::TmwPlugin</name>
    <message>
        <location filename="../src/plugins/tmw/tmwplugin.cpp" line="+47"/>
        <source>Multiple collision layers found!</source>
        <translation>Открити са повече от един колизионни слоеве!</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>No collision layer found!</source>
        <translation>Не е открит колизионен слой!</translation>
    </message>
    <message>
        <location line="+6"/>
        <source>Could not open file for writing.</source>
        <translation>Неуспешно отваряне на файла за запис.</translation>
    </message>
    <message>
        <location line="+30"/>
        <source>TMW-eAthena collision files (*.wlk)</source>
        <translation>Файлове с колизии на TMW-eAthena (*.wlk)</translation>
    </message>
</context>
<context>
    <name>TmxViewer</name>
    <message>
        <location filename="../src/tmxviewer/tmxviewer.cpp" line="+182"/>
        <source>TMX Viewer</source>
        <translation>Преглед на TMX</translation>
    </message>
</context>
<context>
    <name>Undo Commands</name>
    <message>
        <location filename="../src/tiled/addremovelayer.h" line="+67"/>
        <source>Add Layer</source>
        <translation>Добавяне на слой</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Remove Layer</source>
        <translation>Премахване на сло</translation>
    </message>
    <message>
        <location filename="../src/tiled/addremovemapobject.cpp" line="+76"/>
        <source>Add Object</source>
        <translation>Добавяне на обект</translation>
    </message>
    <message>
        <location line="+13"/>
        <source>Remove Object</source>
        <translation>Премахване на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/addremovetileset.cpp" line="+66"/>
        <source>Add Tileset</source>
        <translation>Добавяне на плочен набор</translation>
    </message>
    <message>
        <location line="+9"/>
        <source>Remove Tileset</source>
        <translation>Премахване на плочен набор</translation>
    </message>
    <message>
        <location filename="../src/tiled/changemapobject.cpp" line="+36"/>
        <source>Change Object</source>
        <translation>Промяна на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/changeobjectgroupproperties.cpp" line="+39"/>
        <source>Change Object Layer Properties</source>
        <translation>Промяна на свойствата на слой с обекти</translation>
    </message>
    <message>
        <location filename="../src/tiled/changeproperties.cpp" line="+38"/>
        <source>Change %1 Properties</source>
        <translation>Промяна на свойствата на %1</translation>
    </message>
    <message>
        <location line="+41"/>
        <source>Set Property</source>
        <translation>Задаване на стойност на свойство</translation>
    </message>
    <message>
        <location line="+2"/>
        <source>Add Property</source>
        <translation>Добавяне на свойство</translation>
    </message>
    <message>
        <location line="+32"/>
        <source>Remove Property</source>
        <translation>Премахване на свойство</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Rename Property</source>
        <translation>Преименуване на свойство</translation>
    </message>
    <message>
        <location filename="../src/tiled/changeselectedarea.cpp" line="+31"/>
        <source>Change Selection</source>
        <translation>Промяна на избраната област</translation>
    </message>
    <message>
        <location filename="../src/tiled/erasetiles.cpp" line="+39"/>
        <source>Erase</source>
        <translation>Изтриване</translation>
    </message>
    <message>
        <location filename="../src/tiled/filltiles.cpp" line="+37"/>
        <source>Fill Area</source>
        <translation>Запълване на област</translation>
    </message>
    <message>
        <location filename="../src/tiled/movemapobject.cpp" line="+40"/>
        <location line="+12"/>
        <source>Move Object</source>
        <translation>Преместване на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/movemapobjecttogroup.cpp" line="+41"/>
        <source>Move Object to Layer</source>
        <translation>Преместване на обект в слой</translation>
    </message>
    <message>
        <location filename="../src/tiled/movetileset.cpp" line="+31"/>
        <source>Move Tileset</source>
        <translation>Преместване на плочен набор</translation>
    </message>
    <message>
        <location filename="../src/tiled/offsetlayer.cpp" line="+42"/>
        <source>Offset Layer</source>
        <translation>Отместване на слой</translation>
    </message>
    <message>
        <location filename="../src/tiled/painttilelayer.cpp" line="+49"/>
        <source>Paint</source>
        <translation>Рисуване</translation>
    </message>
    <message>
        <location filename="../src/tiled/renamelayer.cpp" line="+40"/>
        <source>Rename Layer</source>
        <translation>Преименуване на слой</translation>
    </message>
    <message>
        <location filename="../src/tiled/resizetilelayer.cpp" line="+37"/>
        <source>Resize Layer</source>
        <translation>Преоразмеряване на слой</translation>
    </message>
    <message>
        <location filename="../src/tiled/resizemap.cpp" line="+32"/>
        <source>Resize Map</source>
        <translation>Преоразмеряване на карта</translation>
    </message>
    <message>
        <location filename="../src/tiled/resizemapobject.cpp" line="+40"/>
        <location line="+12"/>
        <source>Resize Object</source>
        <translation>Преоразмеряване на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/tilesetdock.cpp" line="-695"/>
        <source>Import Tileset</source>
        <translation>Внасяне на плочен набор</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Export Tileset</source>
        <translation>Изнасяне на плочен набор</translation>
    </message>
    <message>
        <location filename="../src/tiled/tilesetchanges.cpp" line="+35"/>
        <source>Change Tileset Name</source>
        <translation>Преименуване на плочен набор</translation>
    </message>
    <message>
        <location line="+22"/>
        <source>Change Drawing Offset</source>
        <translation>Промяна на отместването при изчертаване</translation>
    </message>
    <message>
        <location filename="../src/tiled/movelayer.cpp" line="+37"/>
        <source>Lower Layer</source>
        <translation>Преместване на слой надолу</translation>
    </message>
    <message>
        <location line="+1"/>
        <source>Raise Layer</source>
        <translation>Преместване на слой нагоре</translation>
    </message>
    <message>
        <location filename="../src/tiled/changepolygon.cpp" line="+40"/>
        <location line="+12"/>
        <source>Change Polygon</source>
        <translation>Промяна на многоъгълник</translation>
    </message>
    <message>
        <location filename="../src/tiled/addremoveterrain.cpp" line="+69"/>
        <source>Add Terrain</source>
        <translation>Добавяне на терен</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Remove Terrain</source>
        <translation>Премахване на терен</translation>
    </message>
    <message>
        <location filename="../src/tiled/changeimagelayerproperties.cpp" line="+39"/>
        <source>Change Image Layer Properties</source>
        <translation>Промяна на свойствата на слой с изображения</translation>
    </message>
    <message>
        <location filename="../src/tiled/changetileterrain.cpp" line="+131"/>
        <source>Change Tile Terrain</source>
        <translation>Промяна на терен с плочки</translation>
    </message>
    <message>
        <location filename="../src/tiled/editterraindialog.cpp" line="-135"/>
        <source>Change Terrain Image</source>
        <translation>Промяна на изображението на терен</translation>
    </message>
    <message>
        <location filename="../src/tiled/changelayer.cpp" line="+41"/>
        <source>Show Layer</source>
        <translation>Показване на слой</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Hide Layer</source>
        <translation>Скриване на слой</translation>
    </message>
    <message>
        <location line="+21"/>
        <source>Change Layer Opacity</source>
        <translation>Промяна на плътността на слой</translation>
    </message>
    <message>
        <location line="+29"/>
        <source>Change Layer Offset</source>
        <translation>Промяна на отместването на слой</translation>
    </message>
    <message>
        <location filename="../src/tiled/changemapobject.cpp" line="+31"/>
        <source>Show Object</source>
        <translation>Показване на обект</translation>
    </message>
    <message>
        <location line="+3"/>
        <source>Hide Object</source>
        <translation>Скриване на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/renameterrain.cpp" line="+37"/>
        <source>Change Terrain Name</source>
        <translation>Преименуване на терен</translation>
    </message>
    <message>
        <location filename="../src/tiled/addremovetiles.cpp" line="+74"/>
        <source>Add Tiles</source>
        <translation>Добавяне на плочки</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Remove Tiles</source>
        <translation>Премахване на плочки</translation>
    </message>
    <message>
        <location filename="../src/tiled/changeimagelayerposition.cpp" line="+36"/>
        <source>Change Image Layer Position</source>
        <translation>Преместване на слой с изображения</translation>
    </message>
    <message>
        <location filename="../src/tiled/changemapobjectsorder.cpp" line="+44"/>
        <location filename="../src/tiled/raiselowerhelper.cpp" line="+67"/>
        <source>Raise Object</source>
        <translation>Преместване на обект нагоре</translation>
    </message>
    <message>
        <location line="+2"/>
        <location filename="../src/tiled/raiselowerhelper.cpp" line="+29"/>
        <source>Lower Object</source>
        <translation>Преместване на обект надолу</translation>
    </message>
    <message>
        <location filename="../src/tiled/changetileanimation.cpp" line="+33"/>
        <source>Change Tile Animation</source>
        <translation>Промяна на плочна анимация</translation>
    </message>
    <message>
        <location filename="../src/tiled/changetileobjectgroup.cpp" line="+15"/>
        <source>Change Tile Collision</source>
        <translation>Промяна на плочна колизия</translation>
    </message>
    <message numerus="yes">
        <location filename="../src/tiled/flipmapobjects.cpp" line="+39"/>
        <source>Flip %n Object(s)</source>
        <translation>
            <numerusform>Обръщане на обект</numerusform>
            <numerusform>Обръщане на %n обекта</numerusform>
        </translation>
    </message>
    <message>
        <location filename="../src/tiled/raiselowerhelper.cpp" line="+43"/>
        <source>Raise Object To Top</source>
        <translation>Преместване на обект най-отгоре</translation>
    </message>
    <message>
        <location line="+37"/>
        <source>Lower Object To Bottom</source>
        <translation>Преместване на обект най-отдолу</translation>
    </message>
    <message>
        <location filename="../src/tiled/rotatemapobject.cpp" line="+40"/>
        <location line="+12"/>
        <source>Rotate Object</source>
        <translation>Завъртане на обект</translation>
    </message>
    <message>
        <location filename="../src/tiled/changemapproperty.cpp" line="+41"/>
        <source>Change Tile Width</source>
        <translation>Промяна на ширината на плочките</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Change Tile Height</source>
        <translation>Промяна на височината на плочките</translation>
    </message>
    <message>
        <location line="+4"/>
        <source>Change Hex Side Length</source>
        <translation>Промяна на страната на шестоъгълните плочки</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Background Color</source>
        <translation>Промяна на цвета на фона</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Stagger Axis</source>
        <translation>Промяна на оста на разминаване</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Stagger Index</source>
        <translation>Промяна на номерацията на разминаване</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Orientation</source>
        <translation>Промяна на ориентацията</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Render Order</source>
        <translation>Промяна на реда на изчертаване</translation>
    </message>
    <message>
        <location line="+10"/>
        <source>Change Layer Data Format</source>
        <translation>Промяна на формата на данните на слоевете</translation>
    </message>
    <message>
        <location filename="../src/tiled/changetileprobability.cpp" line="+38"/>
        <source>Change Tile Probability</source>
        <translation>Промяна на вероятността на плочка</translation>
    </message>
</context>
<context>
    <name>Utils</name>
    <message>
        <location filename="../src/tiled/utils.cpp" line="+34"/>
        <source>Image files</source>
        <translation>Файлове с изображения</translation>
    </message>
</context>
</TS>
