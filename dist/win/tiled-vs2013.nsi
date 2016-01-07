; NSIS installer script for Tiled
; --------------- Headers --------------
!include "MUI2.nsh"
!include "FileAssociation.nsh"

; --------------- General --------------
CRCCheck force
XPStyle on
SetCompressor /FINAL /SOLID lzma

!ifndef QT_DIR
!define QT_DIR $%QTDIR%                       ; Qt Installation directory
!endif

!ifndef V
!define V $%VERSION%                          ; Program version
!endif

!ifndef ARCH
!define ARCH $%ARCH%                          ; Architecture 32 or 64
!endif

!define P "Tiled"                             ; Program name
!define P_NORM "tiled"                        ; Program name (normalized)

!ifndef ROOT_DIR
!define ROOT_DIR "..\.."                      ; Program root directory
!endif

!ifndef BUILD_DIR
!define BUILD_DIR $%TILED_BUILD_DIR%          ; Build dir
!endif

!define ADD_REMOVE "Software\Microsoft\Windows\CurrentVersion\Uninstall\Tiled"
!define PRODUCT_REG_KEY "Tiled Map Editor"

!if ARCH == 32
!define SYSTEM_DIR "C:\windows\system32"
InstallDir "$PROGRAMFILES\${P}"               ; Default 32-bit installation directory
!else
!define SYSTEM_DIR "C:\windows\SysWOW64"
InstallDir "$PROGRAMFILES64\${P}"             ; Default 64-bit installation directory
!endif

Name "${P}"                                   ; Name displayed on installer
OutFile "${P_NORM}-${V}-win${ARCH}-setup.exe" ; Resulting installer filename
BrandingText /TRIMLEFT "${P_NORM}-${V}"
RequestExecutionLevel admin

; ----------- Icon and Bitmap ---------
;!define MUI_ICON install.ico                 ; TODO: find suitable icon
;!define MUI_UNICON uninstall.ico             ; TODO: find suitable icon
!define MUI_HEADERIMAGE
	!define MUI_HEADERIMAGE_BITMAP headerimage.bmp
	!define MUI_HEADERIMAGE_UNBITMAP headerimage.bmp
!define MUI_HEADER_TRANSPARENT_TEXT

; -------------------------------------
!define MUI_ABORTWARNING

;------------- Language Selection Dialog Settings --------------
!define MUI_LANGDLL_REGISTRY_ROOT "HKCU"
!define MUI_LANGDLL_REGISTRY_KEY "Software\${P}\${V}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "Installer Language"

;-------------- Install Pages -------------
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE ${ROOT_DIR}\dist\win\gpl-2.0.rtf
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
    ; These indented statements modify settings for MUI_PAGE_FINISH
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_FINISHPAGE_RUN "$INSTDIR\${P_NORM}.exe"
    !define MUI_FINISHPAGE_RUN_CHECKED
    !define MUI_FINISHPAGE_RUN_TEXT "Launch ${P}"
    !define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
    !define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!insertmacro MUI_PAGE_FINISH

;-------------- Uninstall Pages -------------
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
	; These indented statements modify settings for MUI_UNPAGE_FINISH
	!define MUI_UNFINISHPAGE_NOAUTOCLOSE
!insertmacro MUI_UNPAGE_FINISH

;--------------- Languages ---------------
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "SpanishInternational"
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "TradChinese"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "Korean"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "Danish"
!insertmacro MUI_LANGUAGE "Swedish"
!insertmacro MUI_LANGUAGE "Norwegian"
!insertmacro MUI_LANGUAGE "NorwegianNynorsk"
!insertmacro MUI_LANGUAGE "Finnish"
!insertmacro MUI_LANGUAGE "Greek"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Portuguese"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "Ukrainian"
!insertmacro MUI_LANGUAGE "Czech"
!insertmacro MUI_LANGUAGE "Slovak"
!insertmacro MUI_LANGUAGE "Croatian"
!insertmacro MUI_LANGUAGE "Bulgarian"
!insertmacro MUI_LANGUAGE "Hungarian"
!insertmacro MUI_LANGUAGE "Thai"
!insertmacro MUI_LANGUAGE "Romanian"
!insertmacro MUI_LANGUAGE "Latvian"
!insertmacro MUI_LANGUAGE "Macedonian"
!insertmacro MUI_LANGUAGE "Estonian"
!insertmacro MUI_LANGUAGE "Turkish"
!insertmacro MUI_LANGUAGE "Lithuanian"
!insertmacro MUI_LANGUAGE "Slovenian"
!insertmacro MUI_LANGUAGE "Serbian"
!insertmacro MUI_LANGUAGE "SerbianLatin"
!insertmacro MUI_LANGUAGE "Arabic"
!insertmacro MUI_LANGUAGE "Farsi"
!insertmacro MUI_LANGUAGE "Hebrew"
!insertmacro MUI_LANGUAGE "Indonesian"
!insertmacro MUI_LANGUAGE "Mongolian"
!insertmacro MUI_LANGUAGE "Luxembourgish"
!insertmacro MUI_LANGUAGE "Albanian"
!insertmacro MUI_LANGUAGE "Breton"
!insertmacro MUI_LANGUAGE "Belarusian"
!insertmacro MUI_LANGUAGE "Icelandic"
!insertmacro MUI_LANGUAGE "Malay"
!insertmacro MUI_LANGUAGE "Bosnian"
!insertmacro MUI_LANGUAGE "Kurdish"
!insertmacro MUI_LANGUAGE "Irish"
!insertmacro MUI_LANGUAGE "Uzbek"
!insertmacro MUI_LANGUAGE "Galician"
!insertmacro MUI_LANGUAGE "Afrikaans"
!insertmacro MUI_LANGUAGE "Catalan"
!insertmacro MUI_LANGUAGE "Esperanto"

; ------------- Reserve Files ---------------------
!insertmacro MUI_RESERVEFILE_LANGDLL

; ------------- Installer Functions ---------------
Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Function checkAlreadyInstalled
	; check for already installed instance
	ClearErrors
	ReadRegStr $R0 HKLM "SOFTWARE\${PRODUCT_REG_KEY}" "Version"
	StrCmp $R0 "" 0 +2
	Return
	MessageBox MB_YESNO|MB_ICONQUESTION "${P} version $R0 seems \
	to be installed on your system.$\nWould you like to \
	uninstall that version first?" IDYES UnInstall
	Return
	UnInstall:
        ClearErrors
        ReadRegStr $R0 HKLM "${ADD_REMOVE}" "UninstallString"
		DetailPrint "Uninstalling previously installed version"
        ExecWait '$R0 _?=$INSTDIR'
		IfErrors OnError 0
		Return
	OnError:
		MessageBox MB_OK|MB_ICONSTOP "Error while uninstalling \
		previously installed version. Please uninstall it manually \
		and start the installer again."
		Quit
FunctionEnd

;-------------- Uninstaller Functions -------------
Function un.onInit
  !insertmacro MUI_UNGETLANGUAGE
FunctionEnd

;-------------- Installer -------------------------
Section "" ; No components page, name is not important
Call checkAlreadyInstalled

SetOutPath $INSTDIR ; Set output path to the installation directory.
WriteUninstaller $INSTDIR\uninstall.exe ; Location of the uninstaller

File /oname=COPYING.txt ${ROOT_DIR}\COPYING
File /oname=AUTHORS.txt ${ROOT_DIR}\AUTHORS
File /oname=README.txt ${ROOT_DIR}\README.md
File /oname=NEWS.txt ${ROOT_DIR}\NEWS
File /oname=LICENSE.APACHE.txt ${ROOT_DIR}\LICENSE.APACHE
File /oname=LICENSE.BSD.txt ${ROOT_DIR}\LICENSE.BSD
File /oname=LICENSE.GPL.txt ${ROOT_DIR}\LICENSE.GPL
File ${BUILD_DIR}\${P_NORM}.dll
File ${BUILD_DIR}\${P_NORM}.exe
File ${BUILD_DIR}\tmxviewer.exe
File ${BUILD_DIR}\tmxrasterizer.exe
File ${BUILD_DIR}\automappingconverter.exe
File ${QT_DIR}\bin\Qt5Core.dll
File ${QT_DIR}\bin\Qt5Gui.dll
File ${QT_DIR}\bin\Qt5Widgets.dll
File ${QT_DIR}\bin\Qt5OpenGL.dll
File ${QT_DIR}\bin\icuin54.dll
File ${QT_DIR}\bin\icuuc54.dll
File ${QT_DIR}\bin\icudt54.dll
File ${SYSTEM_DIR}\MSVCP120.DLL
File ${SYSTEM_DIR}\MSVCR120.DLL
File ${ROOT_DIR}\src\tiled\images\tiled-icon.ico
File ${ROOT_DIR}\dist\win\qt.conf

SetOutPath $INSTDIR\plugins\platforms
File ${QT_DIR}\plugins\platforms\qwindows.dll

SetOutPath $INSTDIR\plugins\imageformats
File ${QT_DIR}\plugins\imageformats\qgif.dll
File ${QT_DIR}\plugins\imageformats\qjpeg.dll
File ${QT_DIR}\plugins\imageformats\qtiff.dll

SetOutPath $INSTDIR\plugins\tiled
File /r ${BUILD_DIR}\plugins\tiled\*.dll

SetOutPath $INSTDIR\translations
File  ${BUILD_DIR}\translations\*.qm
File  ${QT_DIR}\translations\qt_cs.qm
File  ${QT_DIR}\translations\qt_de.qm
File  ${QT_DIR}\translations\qt_es.qm
File  ${QT_DIR}\translations\qt_fr.qm
File  ${QT_DIR}\translations\qt_he.qm
File  ${QT_DIR}\translations\qt_ja.qm
File  ${QT_DIR}\translations\qt_pt.qm
File  ${QT_DIR}\translations\qt_ru.qm
File  ${QT_DIR}\translations\qt_zh_CN.qm
File  ${QT_DIR}\translations\qt_zh_TW.qm

SetOutPath $INSTDIR\examples
File /r ${ROOT_DIR}\examples\*.*

SetOutPath $INSTDIR\docs
File /r ${ROOT_DIR}\docs\map.*

SetOutPath $INSTDIR\util
File /r /x .gitignore /x README /x README.txt ${ROOT_DIR}\util\*.*

; Shortcuts
CreateDirectory "$SMPROGRAMS\${P}"
CreateShortCut  "$SMPROGRAMS\${P}\${P}.lnk" "$INSTDIR\${P_NORM}.exe"
CreateShortCut  "$SMPROGRAMS\${P}\uninstall.lnk" "$INSTDIR\uninstall.exe"

; File associations
${RegisterExtension} "$INSTDIR\${P_NORM}.exe" ".tmx" "Tiled.tmx"

; Add version number to Registry
WriteRegStr HKLM "Software\${PRODUCT_REG_KEY}" "Version" "${V}"

; Add uninstall information to "Add/Remove Programs"
WriteRegStr HKLM ${ADD_REMOVE} "DisplayName" "Tiled - Tiled Map Editor"
WriteRegStr HKLM ${ADD_REMOVE} "DisplayIcon" "$INSTDIR\${P_NORM}-icon.ico"
WriteRegStr HKLM ${ADD_REMOVE} "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
WriteRegStr HKLM ${ADD_REMOVE} "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
WriteRegStr HKLM ${ADD_REMOVE} "Version" "${V}"
SectionEnd
;------------ Uninstaller -------------
Section "uninstall"
Delete $INSTDIR\COPYING.txt
Delete $INSTDIR\AUTHORS.txt
Delete $INSTDIR\README.txt
Delete $INSTDIR\NEWS.txt
Delete $INSTDIR\LICENSE.APACHE.txt
Delete $INSTDIR\LICENSE.BSD.txt
Delete $INSTDIR\LICENSE.GPL.txt
Delete $INSTDIR\tiled.dll
Delete $INSTDIR\tiled.exe
Delete $INSTDIR\tmxviewer.exe
Delete $INSTDIR\tmxrasterizer.exe
Delete $INSTDIR\automappingconverter.exe
Delete $INSTDIR\Qt5Core.dll
Delete $INSTDIR\Qt5Gui.dll
Delete $INSTDIR\Qt5Widgets.dll
Delete $INSTDIR\Qt5OpenGL.dll
Delete $INSTDIR\libEGL.dll
Delete $INSTDIR\libGLESv2.dll
Delete $INSTDIR\icuin54.dll
Delete $INSTDIR\icuuc54.dll
Delete $INSTDIR\icudt54.dll
Delete $INSTDIR\MSVCP120.DLL
Delete $INSTDIR\MSVCR120.DLL
Delete $INSTDIR\tiled-icon.ico
Delete $INSTDIR\qt.conf
Delete $INSTDIR\uninstall.exe

RMDir /r $INSTDIR\plugins\platforms
RMDir /r $INSTDIR\plugins\imageformats
RMDir /r $INSTDIR\plugins\tiled
RMDir    $INSTDIR\plugins
RMDir /r $INSTDIR\translations
RMDir /r $INSTDIR\examples
RMDir /r $INSTDIR\docs
RMDir /r $INSTDIR\util

RMDir  $INSTDIR

; Removing shortcuts
Delete "$SMPROGRAMS\${P}\${P}.lnk"
Delete "$SMPROGRAMS\${P}\uninstall.lnk"
RMDir  "$SMPROGRAMS\${P}"

; Removing file associations
${UnRegisterExtension} ".tmx" "Tiled.tmx"

; Remove Procut Registry Entries
DeleteRegKey HKLM "Software\${PRODUCT_REG_KEY}"

; Remove entry from "Add/Remove Programs"
DeleteRegKey HKLM ${ADD_REMOVE}
SectionEnd
