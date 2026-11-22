# Layout checks for homemade PICO-8 games

- PICO-8 gameplay uses a 128×128 screen. Center the main visual group and any
  choice row on x=64. Calculate each group's actual left and right edges,
  including shape radius, string, and selection marks; do not center only its
  first and last coordinates by eye.
- Check every menu setting and gameplay difficulty. A layout that is centered
  with two choices can shift when it has three, four, or five.
- Check rendered pixels at 1× or integer scaling after building. Include
  partial final rows, progress indicators, coin stacks, labels, and control
  hints in the visual review. Keep these elements clear of one another.
- When changing a game's layout, update its cartridge artwork if the artwork
  depicts the changed screen.

## Selector style

- Keep a simple V selector small and symmetric. Use this exact 5×3 bitmap,
  centered above the selected choice; `X` is one foreground pixel and `O` is
  transparent:

  ```text
  XOOOX
  OXOXO
  OOXOO
  ```

- Place the V with a visible gap above the choice. Set its pixels explicitly
  so line rasterization cannot change its size or symmetry.
