!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "EliClaw"
OutFile "EliClaw-Setup.exe"
InstallDir "$PROGRAMFILES64\EliClaw"
InstallDirRegKey HKCU "Software\EliClaw" "InstallDir"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "..\assets\icons\icon.ico"
!define MUI_UNICON "..\assets\icons\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\..\LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "EliClaw" SecMain
  SetOutPath "$INSTDIR"
  File /r "..\..\dist\win-unpacked\*"

  CreateDirectory "$SMPROGRAMS\EliClaw"
  CreateShortcut "$SMPROGRAMS\EliClaw\EliClaw.lnk" "$INSTDIR\EliClaw.exe"
  CreateShortcut "$DESKTOP\EliClaw.lnk" "$INSTDIR\EliClaw.exe"

  WriteRegStr HKCU "Software\EliClaw" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw" "DisplayName" "EliClaw"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw" "DisplayIcon" "$INSTDIR\EliClaw.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw" "Publisher" "Virtualab Digital"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw" "URLInfoAbout" "https://virtualabdigital.com"

  WriteUninstaller "$INSTDIR\uninstall.exe"
SectionEnd

Section "Uninstall"
  Delete "$INSTDIR\*"
  RMDir /r "$INSTDIR"

  Delete "$SMPROGRAMS\EliClaw\*"
  RMDir "$SMPROGRAMS\EliClaw"
  Delete "$DESKTOP\EliClaw.lnk"

  DeleteRegKey HKCU "Software\EliClaw"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\EliClaw"
SectionEnd