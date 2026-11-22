#!/bin/zsh

launcher_dir=${0:A:h}
gameboy_dir="$launcher_dir/../.."
cartridge_dir="$launcher_dir/../FireDragon"
tic80_app="$gameboy_dir/tools/TIC-80.app"

open -n -a "$tic80_app" --args --fs "$cartridge_dir" --cmd 'load dragon_fury.tic & run'
