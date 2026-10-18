#!/usr/bin/env bash
# Ultimate Pack — dedicated server launcher.
# First run installs NeoForge; every run syncs mods/configs/scripts from GitHub, then starts the server.
#   MEMORY=8G ./start.sh        (default 6G)
#   PACK_URL=... ./start.sh     (use a fork or a pinned commit)
set -euo pipefail
cd "$(dirname "$0")"

PACK_URL="${PACK_URL:-https://raw.githubusercontent.com/Dim4312/ultimate-pack/main/pack.toml}"
NEOFORGE="21.1.262"
MEMORY="${MEMORY:-6G}"

if [ ! -f run.sh ]; then
  echo "Installing NeoForge $NEOFORGE server..."
  curl -fsSL -o neoforge-installer.jar "https://maven.neoforged.net/releases/net/neoforged/neoforge/$NEOFORGE/neoforge-$NEOFORGE-installer.jar"
  java -jar neoforge-installer.jar --installServer
  rm -f neoforge-installer.jar neoforge-installer.jar.log
fi

if ! grep -q -- '-Xmx' user_jvm_args.txt 2>/dev/null; then
  echo "-Xmx$MEMORY" >> user_jvm_args.txt
fi

if [ ! -f server.properties ]; then
  # Create contraptions and airships trip the vanilla fly-kick; Phase 1 starts at spawn, so no spawn protection.
  cat > server.properties <<PROPS
allow-flight=true
spawn-protection=0
difficulty=normal
view-distance=10
simulation-distance=8
motd=Ultimate Pack
PROPS
fi

if [ ! -f packwiz-installer-bootstrap.jar ]; then
  curl -fsSL -o packwiz-installer-bootstrap.jar https://github.com/packwiz/packwiz-installer-bootstrap/releases/latest/download/packwiz-installer-bootstrap.jar
fi
echo "Syncing pack from $PACK_URL"
java -jar packwiz-installer-bootstrap.jar -g -s server "$PACK_URL"

if ! grep -q '^eula=true' eula.txt 2>/dev/null; then
  echo "You must accept the Minecraft EULA (https://aka.ms/MinecraftEULA):  echo eula=true > eula.txt"
  exit 1
fi

exec ./run.sh nogui
