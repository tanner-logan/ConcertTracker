; Inno Setup script for Concert Tracker.
; Build the exe first (pyinstaller, see README step 4), then compile this with:
;   iscc installer\ConcertTracker.iss /DMyAppVersion=1.0.0
; MyAppVersion defaults to 0.0.0-dev if not passed in (e.g. local test compiles).

#ifndef MyAppVersion
#define MyAppVersion "0.0.0-dev"
#endif

#define MyAppName "Concert Tracker"
#define MyAppPublisher "Concert Tracker"
#define MyAppExeName "ConcertTracker.exe"

[Setup]
; Fixed GUID identifying this app across versions - do not change.
AppId={{9F7B0F5B-9E4A-4A1B-8C2D-6C6A4C2C2F41}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Per-user install with no admin prompt - matches how the app stores all of its
; own data (config, tokens, autostart registry key) under the current user.
PrivilegesRequired=lowest
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=ConcertTrackerSetup
SetupIconFile=..\concert_tracker\resources\app_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent
