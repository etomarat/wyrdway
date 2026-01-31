# Web Assembly (WASM) Support

TIC-80 supports compiled languages via our WASM binary support. Compile a `.wasm` file using an external compiler toolchain and then import
that binary (up to to 256kb) into your TIC-80 cartridge.  Many modern
languages support compiling to WASM.

### Unique WASM workflow/behavior

- The built-in editor content is not used to edit your code.
  - editor comments must use the Lua style, e.g. `-- this is a comment`...
  - a `-- script: wasm` magic comment is required to use the `wasm` runtime
  - ...no code you type in the editor will ever be executed

#### WASM "hardware" limits

- a 256KB [`BINARY` chunk](.tic-File-Format#binary) stores compiled code
  - binary `.wasm` files up to 256KB may be imported
- 256KB addressable memory
  - 112KB base [RAM](ram) for memory mapped I/O, SFX, VRAM, etc.
  - 160KB of [RAM](ram) free for cartridge use

### Starting a new compiled from source project

Copying one of the built-in project templates we provide is the best way to get started. These templates include both a tiny sample project and library bindings for the TIC-80 API.


- [C](https://github.com/nesbox/TIC-80/tree/main/templates/c)
- C++ ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- [D](https://github.com/nesbox/TIC-80/tree/main/templates/d)
- Go ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- NeLua ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- Nim ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- Odin ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- [Rust](https://github.com/nesbox/TIC-80/tree/main/templates/rust)
- other? ([help wanted](https://github.com/nesbox/TIC-80/issues/1784))
- [Zig](https://github.com/nesbox/TIC-80/tree/main/templates/zig)


If you're familiar with one of the languages above and would like to contribute an official library binding for TIC-80, we'd love your help!  Just comment on [#1784](https://github.com/nesbox/TIC-80/issues/1784) or open a new GitHub issue.