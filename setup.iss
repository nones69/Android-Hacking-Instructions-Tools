; Inno Setup Script for MobileDeviceToolkit
; Generated and refined by Gemini Code Assist

; --- Project Defines ---
#define MyAppName "MobileDeviceToolkit"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Company Name"
#define MyAppURL "https://www.example.com/"
#define MyAppExeName "MobileDeviceToolkit.exe"

; --- Path Defines ---
; These paths are relative to the script file's location.
#define SourceDir "dist"
#define AssetsDir "assets"
#define MyAppIcon AssetsDir + "\icon.ico"

[Setup]
; IMPORTANT: The value of AppId uniquely identifies this application.
; You MUST generate a new GUID and replace the placeholder below.
; In Inno Setup, use "Tools -> Generate GUID".
AppId={{A3E8B0E1-2D4B-4F8A-8A9E-3B7C6D9F1A2B}}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
; Place the final installer in an 'installers' sub-directory
OutputBaseFilename=MobileDeviceToolkit-{#MyAppVersion}-setup
OutputDir=installers
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Request administrator privileges for installation in Program Files
PrivilegesRequired=admin
; Icon for the installer itself
SetupIconFile={#MyAppIcon}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; This copies the main executable built by PyInstaller into the application directory.
; The executable is expected to be in the 'dist' folder relative to this script.
Source: "{#SourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; NOTE: All other assets (tools, payloads, etc.) are bundled inside the
; single-file executable by PyInstaller, so they don't need to be listed here.

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; This ensures that the entire application directory is removed on uninstall,
; including any log files or other data the application might have created.
Type: filesandordirs; Name: "{app}"