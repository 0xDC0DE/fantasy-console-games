#!/bin/zsh

launcher_dir=${0:A:h}
gameboy_dir=${launcher_dir:h:h}
pico8_app=${PICO8_APP:-$HOME/Downloads/pico-8/PICO-8.app}
cartridge="$gameboy_dir/ROMS/PICO-8/CountNumbers.p8.png"

[[ -f "$cartridge" ]] || { print -u2 "Cartridge missing: $cartridge"; exit 1; }
[[ -d "$pico8_app" ]] || { print -u2 "PICO-8 app missing: $pico8_app"; exit 1; }
if [[ $1 == --check ]]; then
 print -r -- "$cartridge"
 exit 0
fi
open -n -a "$pico8_app" --args -run "$cartridge"
