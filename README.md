GalaxyScript VM & bytecode
==========================

This repository holds information about the GalaxyScript bytecode reverse 
engineered from the virtual machine used in the "StarCraft2" and 
"Heroes of the Storms" games. A disassembler and a PoC-grade IDA processor 
module are provided in the `gsdisas` directory.

The info essentially consists of the leftovers of what I wrote down when I 
reversed it about two years ago. As I lost interest in the VM pretty quickly, 
the research and especially the `GSVM.md` writedown aren't complete and 
probably also have a few things incorrect, should however provide a solid 
starting point for anyone interested in diving into the low-levels of the GS 
language. The disassembler features near-complete decoding for all instructions
that were implemented by the VM at the time of reversing.

Mnemonic names and disassembly format were invented to fit what they do
and most probably won't correspond to the format used by Blizzard 
internally as no documentation nor hints about them exist in publicly
available sources.

Credits go out to my friend [TheWisp](https://github.com/TheWisp) who gave me a
kickstart into the GalaxyScript basics when I began my research in this area!

All information is provided under MIT license.
