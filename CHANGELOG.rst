Changelog
#########

Unreleased
==========

- encoding: Add regex_pattern_to_bytes() for converting UTF8 format string into a byte regular expression.
- utils.grep_iter: Create a base method for regular expression based searching.
- cli: Update command line tools to support recursive directory traversal.
- Add changelog.

0.7.0 - 2019-09-26
==================

- fields: Update the string Field classes (e.g. Bytes, CString) to be based on StringField. This allows multiple elements.
- fields.ChunkField: Allow using an enum class for chunk IDs.
- lib.containers.vgm: Add preliminary support for VGM files.
- tests: Improve test coverage.
- fields.StreamField: get_from_buffer() changed to fail if there's no data left.
- lib.platforms.director: More improvements to Macromedia Director support.
- fields: Change Field classes to disallow unnamed arguments except klass and offset. This improves readability and makes argument ordering less brittle.
- lib.images.base: Fix IndexedImage to not crash out of bounds and fall back to TEST_PALETTE by default.
- ansi: Add escape sequences for clearing the screen and moving the cursor.
- lib.games.lomax: Add preliminary support for Adventures of Lomax graphics data.

0.6.1 - 2019-07-06
==================

- lib.games.jill: Add audio support, fix load ordering and class invocations.
- lib.audio.voc: Add preliminary support for Creative VOC files.
- encoding: Add support for 24-bit integers.
- fields: Add Fields for decoding variants of Int24.
- views.Store: Add support for inline Transforms.
- lib.os.dos.B800Char: Add ANSI support for blinking text.
- lib.platforms.director: More improvements to Macromedia Director support, add a Lingo disassembler.
- lib.games.boppin: Add inline decompression to loader.
- fields.Bytes: Add support for alignment.
- utils.pixdump: Add a shortcut for displaying data as a 256 colour image.
- fields.BlockField: Fix updating the dependencies on child objects on save.
- utils: Split out the console-output parts into the new ansi module.
- utils: Split out the colour-handling parts into the new colour module.
- lib.audio.base: Split out the PCM playback code into the new sound module.
- utils: Move some low-level methods into the new common module, to avoid importing utils everywhere.
- fields.ChunkField: Allow None as a chunk payload.
- refs.Ref: Start enforcing immutability.
- common: Add a serialise() method for Fields.
- utils: Add a diff() tool for comparing Blocks.
- sound: Fix multichannel support and resampling.
- .travis.yml: Add CI for running tests.

0.6.0 - 2019-01-13
==================

0.5.1 - 2018-07-20
==================

0.5.0 - 2018-06-22
==================

0.4.2 - 2018-02-05
==================

0.4.1 - 2017-11-26
==================

0.4.0 - 2017-10-12
==================

