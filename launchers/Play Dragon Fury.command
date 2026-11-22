#!/bin/zsh

launcher_dir=${0:A:h}
gameboy_dir=${launcher_dir:h:h}
tic80_app=${TIC80_APP:-$gameboy_dir/tools/TIC-80.app}
cartridge="$gameboy_dir/ROMS/TIC-80/dragon_fury.tic"

[[ -f "$cartridge" ]] || { print -u2 "Cartridge missing: $cartridge"; exit 1; }
[[ -d "$tic80_app" ]] || { print -u2 "TIC-80 app missing: $tic80_app"; exit 1; }
if [[ $1 == --check ]]; then
 print -r -- "$cartridge"
 exit 0
fi
open -n -a "$tic80_app" --args --fs "$gameboy_dir/ROMS/TIC-80" --cmd 'load dragon_fury.tic & run'
