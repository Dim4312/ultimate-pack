@echo off
rem Ultimate Pack - dedicated server launcher for Windows.
rem First run installs NeoForge; every run syncs mods/configs/scripts from GitHub, then starts the server.
rem   set MEMORY=8G ^& start.bat     (default 8G)
setlocal
cd /d "%~dp0"

if not defined PACK_URL set PACK_URL=https://raw.githubusercontent.com/Dim4312/ultimate-pack/main/pack.toml
set NEOFORGE=21.1.262
if not defined MEMORY set MEMORY=8G

if not exist run.bat (
  echo Installing NeoForge %NEOFORGE% server...
  curl -fsSL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/%NEOFORGE%/neoforge-%NEOFORGE%-installer.jar" || goto :fail
  java -jar neoforge-installer.jar --installServer || goto :fail
  del /q neoforge-installer.jar neoforge-installer.jar.log 2>nul
)

findstr /c:"-Xmx" user_jvm_args.txt >nul 2>&1 || echo -Xmx%MEMORY%>> user_jvm_args.txt

if not exist server.properties (
  rem Create contraptions and airships trip the vanilla fly-kick; Phase 1 starts at spawn, so no spawn protection.
  > server.properties (
    echo allow-flight=true
    echo spawn-protection=0
    echo difficulty=normal
    echo view-distance=10
    echo simulation-distance=8
    echo motd=Ultimate Pack
  )
)

if not exist packwiz-installer-bootstrap.jar (
  curl -fsSL -o packwiz-installer-bootstrap.jar https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar || goto :fail
)
echo Syncing pack from %PACK_URL%
if "%PACKWIZ_BOOTSTRAP_NO_UPDATE%"=="1" (
  if not exist packwiz-installer.jar (
    echo PACKWIZ_BOOTSTRAP_NO_UPDATE=1 requires a predownloaded packwiz-installer.jar
    goto :fail
  )
  for %%I in (packwiz-installer.jar) do if %%~zI EQU 0 goto :fail
  java -jar packwiz-installer-bootstrap.jar --bootstrap-no-update -g -s server "%PACK_URL%" || goto :fail
) else (
  java -jar packwiz-installer-bootstrap.jar -g -s server "%PACK_URL%" || goto :fail
)

findstr /b "eula=true" eula.txt >nul 2>&1 || (
  echo You must accept the Minecraft EULA ^(https://aka.ms/MinecraftEULA^): open eula.txt and set eula=true
  if not exist eula.txt echo eula=false> eula.txt
  pause
  exit /b 1
)

call run.bat nogui
exit /b

:fail
echo Setup failed, see the messages above.
pause
exit /b 1
