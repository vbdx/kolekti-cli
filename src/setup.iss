; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define BuildDir "F:\Bureau\kolekti\sources\0.7\kolekti\src"

#define MyAppName "Kolekti"
#define MyAppVersion "0.7.5-pre2"
#define MyAppPublisher "Exselt Services"
#define MyAppURL "http://www.kolekti.org/"
#define MyAppExeName "kolekti_server.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8B4AEA7A-A156-49ED-8498-5DDAEF4A888F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile={#BuildDir}\LICENCE
OutputBaseFilename=setup-{#MyAppName}_{#MyAppVersion}
;OutputDir=F:\kolekti\
Compression=lzma
SolidCompression=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildDir}\dist\kolekti_server\*"; DestDir: "{app}";  Excludes: "db.sqlite3*"; Flags: ignoreversion recursesubdirs createallsubdirs

Source: "{#BuildDir}\dist\Exemple_PDF\*"; DestDir: "{%HOMEPATH}\kolekti-projects\Exemple_PDF"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall; Permissions: users-modify
Source: "{#BuildDir}\dist\Exemple_Webhelp\*"; DestDir: "{%HOMEPATH}\kolekti-projects\Exemple_Webhelp"; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall; Permissions: users-modify
Source: "{#BuildDir}\dist\Project_template\*"; DestDir: "{app}\kolekti\project_template"; Flags: ignoreversion recursesubdirs createallsubdirs;

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[INI]
Filename: "{userappdata}\kolekti\kolekti.ini"; Section: "InstallSettings"; Key: "projectsPath"; String: "{%HOMEDRIVE}{%HOMEPATH}\kolekti-projects"
Filename: "{userappdata}\kolekti\kolekti.ini"; Section: "InstallSettings"; Key: "installdir"; String: "{app}"
Filename: "{userappdata}\kolekti\kolekti.ini"; Section: "InstallSettings"; Key: "kolektiversion"; String: "{#MyAppVersion}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "syncdb"
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[UninstallDelete]
Type: filesandordirs; Name: "{userappdata}\kolekti"
Type: filesandordirs; Name: "{app}\kolekti.ini"
Type: filesandordirs; Name: "{app}\kolekti.log"
Type: filesandordirs; Name: "{app}\kolekti.err"

[Code]
function gsInstalled(): Boolean;
begin
  if RegKeyExists(HKEY_CURRENT_USER, 'SOFTWARE\GPL Ghostscript') then
  begin
	Result := true;
  end
  else
  begin
	Result := false;
  end
end;
 
procedure installGs();
var
ErrCode: integer;
begin
  if (msgbox('In order to enable Converseen to manage PDF files you have to download and install Ghostscript. Do you want to download it now?', mbConfirmation, MB_YESNO) = IDYES) then
  begin
	ShellExec('open', 'http://www.ghostscript.com/download/gsdnld.html', '', '', SW_SHOW, ewNoWait, ErrCode);
  end
end;
 
procedure CurPageChanged(CurPageID: Integer);
var
gsIsInstalled : boolean;
begin
  if CurPageID = wpFinished then
  begin
	gsIsInstalled := gsInstalled();
 
	if gsIsInstalled = false then
	   installGs();
  end
end;
