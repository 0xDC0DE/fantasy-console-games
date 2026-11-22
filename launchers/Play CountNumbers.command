#!/bin/zsh

launcher_dir=${0:A:h}
gameboy_dir="$launcher_dir/../.."
pico8_app="$HOME/Downloads/pico-8/PICO-8.app"
cartridge="$launcher_dir/../CountNumbers/CountNumbers.p8"

open -n -a "$pico8_app" --args -run "$cartridge"
