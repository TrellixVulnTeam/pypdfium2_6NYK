<!-- SPDX-FileCopyrightText: 2022 geisserml <geisserml@gmail.com> -->
<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Changelog


## 3.8.0 (2022-11-14)

- Updated PDFium from `5406` to `5418` (autorelease).
- Major improvements to GitHub Workflows.
- Fixed setup on macOS with Python 3.11. (Wheel users were not impacted.)
- Fixed build script on macOS (GN configuration).
- Fixed build script on Windows (patches and RC).
- Fixed test suite on Windows (cleanup failure).
- Fixed test suite on Python < 3.7.


## 3.7.0 (2022-11-07)

- Updated PDFium from `5392` to `5406` (autorelease).


## 3.6.0 (2022-10-31)

- Updated PDFium from `5378` to `5392` (autorelease).


## 3.5.0 (2022-10-24)

- Updated PDFium from `5364` to `5378` (autorelease).
- Fixed an issue with the `__new__` method of `PdfPageObject` that caused `__init__` to run twice.
- Fixed faulty examples in the Readme.


## 3.4.0 (2022-10-17)

- Updated PDFium from `5351` to `5364` (autorelease).
- Added a new support model `PdfImageObject` (which inherits from `PdfPageObject`). This can be used to insert a JPEG image into a page, get metadata, etc.
- Docs: The changelog page now selectively includes an entry for the next release that may be shown on `latest` builds.


## 3.3.0 (2022-10-10)

- Updated PDFium from `5337` to `5351` (autorelease).
- Disruption: `PdfPage.insert_text()` does not generate page content automatically anymore. The new `PdfPage.generate_content()` method now needs to be called to apply changes, to avoid generating content repeatedly.
- Disruption: In `PdfTextPage.get_text()`, the boundary values are now only set to defaults if they're `None`, not 0. This change was necessary because the underlying PDFium function requires PDF box values rather than normalised values.
- pypdfium2 finally implements automatic object finalisation. Calling the `close()` methods is not mandatory anymore. The context manager API of `PdfDocument` is retained for backwards compatibility, but exiting the context manager does not close the document anymore, since this would increase the risk of closing objects in wrong order.
- A new text extraction method `get_text_range()` was added. `get_text()` was renamed to `get_text_bounded()` but is still available as deprecated alias.
- Text pages now have an `n_chars` attribute. `count_chars()` is still available as deprecated alias.
- Added a helper class for transform matrices.
- Added support models to capture pages as XObjects, to get page objects for XObjects, to transform them with matrices, and to insert page objects into a page. This may be used to implement a custom N-up compositor, for instance.
- The document level renderer now uses a shortcut if processing just a single page.
- When rendering, pypdfium2 now checks if the document has forms before initialising/exiting a form environment.
- The Sphinx documentation now includes the Readme file.


## 3.2.0 (2022-10-03)

- Updated PDFium from `5323` to `5337` (autorelease).


## 3.1.0 (2022-09-26)

- Updated PDFium from `5316` to `5323` (autorelease).
- `render_to()` was fixed to actually allow callables. The code passage in question was unreachable due to an unguarded `issubclass()` check before.


## 3.0.0 (2022-09-24)

- Updated PDFium from `5254` to `5316` (autorelease).

- Support model
    
    *API-breaking changes*
    - If the target page of a bookmark cannot be identified, `OutlineItem.page_index` is now `None` rather than `-1`, to avoid accidental reverse list indexing and to enforce that callers properly handle this case. Moreover, `OutlineItem.is_closed` is now `None` rather than `False` if the bookmark has no kids.
    - `PdfPageObject.get_type()` was replaced with a `type` attribute.
    - `PdfPage.count_objects()` was removed. Use `PdfPage.get_objects()` or the raw PDFium API instead.
    - If a negative index is passed to `PdfDocument.new_page()`, it is now interpreted in reversed direction, rather than inserting at the beginning.
    - PDFium is now provided with an external, python-allocated buffer for rendering. This has numerous advantages, most notably that callers don't need to free resources anymore. `PdfPage.render_base()` now directly returns a ctypes ubyte array; `BitmapDataHolder` has been removed.
    - Changed rendering parameters
        - `annotations` was renamed to `draw_annots`
        - `colour` was renamed to `fill_colour` and now only takes a list of 4 values for simplicity - it may not be 3 values or `None` anymore
        - `no_antialias` has been replaced with separate boolean options `no_smoothtext`, `no_smoothimage`, and `no_smoothpath`
    
    *Other changes*
    - `OutlineItem` now contains information on the number of sub-items (`n_kids` attribute).
    - All document-level methods that take a page index now accept negative values for reverse indexing (except the rendering methods).
    - New method `PdfDocument.get_page_size()` to retrieve page size by index without needing to load a `PdfPage` (uses `FPDF_GetPageSizeByIndexF()` under the hood).
    - New rendering parameters added: `colour_scheme`, `fill_to_stroke`, `force_halftone`, `draw_forms`, `rev_byteorder`, `prefer_bgrx`, `force_bitmap_format`, `extra_flags`, `allocator`, and `memory_limit`.
    - Added new `render_to()` functions to `PdfPage` and `PdfDocument` that take a custom bitmap converter, to transform the ctypes array to a different object. A set of built-in converters is provided with the `BitmapConv` class. Confer the updated API documentation for details. The previous rendering functions (`render_topil()` `render_tobytes()`, ...) are still around as aliases but might be deprecated eventually.
    - New rendering target `numpy_ndarray` added.
    - The `pil_image` rendering target now accepts a `prefer_la` parameter to request automatic conversion of `BGRA`/`RGBA` to `LA` if rendering in greyscale mode with alpha channel.
    - `PdfPage.get_objects()` can now recursively descend into Form XObjects.
    - Form environments are now initialised/exited on document level rather than on page rendering. *In the course of this work, a segmentation fault source was eliminated, related to a formerly undocumented requirement of PDFium regarding object lifetime. Whether the segmentation fault would actually take place was dependent on Python garbage collection behaviour. This did not appear to happen under normal circumstances, so the issue remained unnoticed for a long time.*

- Setup code
    - `$PYP_TARGET_PLATFORM` was renamed to `$PDFIUM_BINARY`, the value `sdist` was renamed to `none`.
    - When doing an automatic release, repository changes are now only pushed after successful wheel building, to avoid leaving the repository in an invalid state in case some earlier step fails.
    - pypdfium2 now declares a no-op setuptools extension to prevent wheel content from landing in a `purelib` folder. Some systems use this information to separate platform-dependent packages from pure-python packages (i. e. `/usr/lib64` instead of `/usr/lib`). Confer PEP 427.
    - Autorelease now properly takes existing beta tags into account for its version changes.
    - PDFium's commit log is now shown with GitHub releases.
    - The wheel packaging script now restores in-tree artefacts from a possible editable install.
    - Platform files are now detected in a more robust way. If missing, a proper exception will be raised.
    - Platform data directories are now annotated with a text file storing the pdfium version, to prevent a possible mismatch between the state of `version.py` and the actual version of the used binary. The update and build scripts do not directly change the main version file anymore, but defer the changes to `setup.py`.
    - Missing platform files are now always procured implicitly on installation. If platform files exist already but are outdated, they will be updated by default. You may opt out by creating an empty file called `.lock_autoupdate.txt` in `data/`.
    - A `MANIFEST.in` file was added to avoid being dependent on `setuptools_scm`.
    - On setup, dependency checks are now only done for system commands. The wonky implicit installation of missing Python packages was removed. If opting out of build isolation, callers should properly install setup dependencies beforehand.

- Documentation
    - Rewrote the project's `README.md`. Added more support model examples and an extensive guide regarding the raw PDFium/ctypes API.
    - Improved docstrings and included type hints.


## 2.11.0 (2022-08-22)

- Updated PDFium from `5241` to `5254` (autorelease).
- Added a new function `PdfDocument.get_version()` to obtain the PDF version of a document.


## 2.10.0 (2022-08-15)

- Updated PDFium from `5226` to `5241` (autorelease).


## 2.9.0 (2022-08-08)

- Updated PDFium from `5215` to `5226` (autorelease).


## 2.8.0 (2022-08-02)

- Updated PDFium from `5200` to `5215` (autorelease).


## 2.7.2 (2022-08-01)

*PDFium was not updated with this release due to an upstream build failure (HTTP 503 error when trying to get the tag).*

- No PDFium update (autorelease).
- Added support for password-protected PDFs in the CLI subcommands `merge`, `render`, `tile` and `toc`.
- Corrected the release workflow to avoid incrementing minor version twice.
- Added a proper way for updating the major version or setting a beta tag with automatic releases.
  Moved most versioning logic from the update script to autorelease on the way.
- Rewrote package building script with python.
- The stable branch is now always updated, even if it contains commits that are not in main.
- Various code style improvements.


## 2.7.1 (2022-07-25)

*Due to a mishap in the workflow, this release got wrongly numbered as 2.7.1 while there was no 2.7.0 release. This also caused problems with the release description on GitHub. We apologise for the inconveniences.*

- Updated PDFium from `5187` to `5200` (autorelease).
- Improved release workflow.
- Documentation corrections.
- Enabled pinning of `wheel` and removed related warning filter in `pyproject.toml`.


## 2.6.0 (2022-07-18)

- Updated PDFium from `5173` to `5187` (autorelease).
- Switched from `FPDF_LoadMemDocument()` to `FPDF_LoadMemDocument64()`. The latter uses `size_t` rather than `int` to avoid integer overflows on huge files.
- Pinned `ctypesgen` to a more recent stable commit in `pyproject.toml`, as the release is fairly outdated. Suggested pinning of `wheel` by code comment.
- Updated planned changes.


## 2.5.0 (2022-07-11)

- Updated PDFium from `5159` to `5173` (autorelease).
- Wheels are now correctly flagged as impure, for they contain a binary extension.
- Merged `trigger.yaml` into `release.yaml` workflow, and `mk_releasenotes.py` into `autorelease.py`, which significantly simplifies the code base.
- Changed autorelease schedule from 12 to 10 o'clock UTC.


## 2.4.1 (2022-07-04)

- No PDFium update (autorelease).
- The manual summary of changes is now shown on the GitHub release page as well.


## 2.4.0 (2022-07-04)

- Updated PDFium from `5145` to `5159` (autorelease).
- Subtle improvements were applied to the handling of input buffers (providing `read()` beside `readinto()` is now explicitly required).
- Concerning file access, the autoclose logic has been moved from the loder data holder to `PdfDocument.close()`, which is somewhat more obvious.
- The internal `colour_tohex()` utility function has been optimised by using bit-shifts and the binary `or` operator.
- Disabled implicit source build in `setup.py`, which used to be the fallback if no pre-built binaries are available for the host platform. Now, an exception is raised instead.
- The changelog is now better integrated with automatic releases.
- In the release workflow, reverted an inelegant change regarding dependency installation order.
- Updated hosts for release workflow and documentation build to Python 3.10.


## 2.3.1 (2022-06-27)

*This version was pushed to test the new autorelease feature. Its non-setup code is virtually identical with release 2.3.0, though.*

- No PDFium update (autorelease).
- Tweaked setup code and GitHub workflows to perform a fully automatic release every monday at 12 o'clock.


## 2.3.0 (2022-06-27)

- Updated PDFium from `5131` to `5145`.
- Improved error handling.
- Updated a comment regarding the `wheel` package.


## 2.2.0 (2022-06-20)

- Updated PDFium from `5117` to `5131`.
- Slightly improved gitignore rules.
- Hid distutils deprecation warnings in test suite, caused by the import of `wheel` in setup scripts.

## 2.1.0 (2022-06-13)

- Updated PDFium from `5104` to `5117`.
- Tweaked the setup code to enable the possibility of performing an editable install using `pip3 install -e .`,
  which is very convenient for development to avoid the necessity of repeated re-installing.
- Improved `PdfDocument.new_page()` to append to the end by default, rather than insert to the beginning.
- Implemented several special methods for `PdfDocument`, including context manager API, looping, and index access.
- Enhanced the documentation.


## 2.0.0 (2022-06-09)

*This release has deeply changed the support model API in a way that is incompatible with previous releases.*

- Updated PDFium from `5092` to `5104`.
- Entirely re-implemented the support model to improve the API and fix some structural issues.
  * All helpers are now object-oriented. This has numerous advantages, including simpler method calls, a cleaner namespace and the possibility to nicely cache internal data.
  * Opening was improved so that any available PDFium loader can now be selected by callers.
  * A page helper class was added to avoid repeated loading and closing of pages in separate functions.
    It also provides new getters and setters for rotation and PDF boxes.
  * Text pages can not be loaded from document objects anymore, as they require a regular page as initialisation parameter.
    The previous API would load and close the regular page implicitly, which is inefficient if callers need to work with it as well.
  * Link extraction features were added to the text page helper class.
  * The table of contents reader now passes through PDFium's viewmode constants instead of converting to attributes of a custom enum, to reduce duplication.
  * The document helper class can now be initialised from a raw `FPDF_DOCUMENT` handle, which allows for seamless interoperability with lower-level PDFium functions.
  * The multipage renderer now does not return a string suffix anymore, only the result object.
  * Internal utilities have been rearranged, and error handling has been improved.
  * Command-line interfaces were adapted to the new API.
  * The Sphinx documentation has been thoroughly overhauled.
- The version file now gets updated accordingly when building from source.
- The test suite has been rearranged, improved and extended.
- Added an option to set a custom PDFium build target, which can be useful to also compile PDFium tests.
- Added the missing libtiff license to PDFium third-party licenses.
- Made the release notes script more elegant.


## 1.11.0 (2022-06-01)

- Updated PDFium from `5079` to `5092`.
- In the text extractor, avoid decoding errors on malformed documents by using `errors="ignore"`.


## 1.10.0 (2022-05-25)

- Updated PDFium from `5065` to `5079`.
- Added cropping capabilities to the rendering engine.
- Added support models to extract text and work with page objects.


## 1.9.1 (2022-05-16)

- Bugfix release to address incompatibility of the CLI with Python 3.6, caused by recent changes.


## 1.9.0 (2022-05-16)

- Updated PDFium from `5052` to `5065`.
- Significantly improved maintainability of the command-line interface by using argparse subparsers instead of a custom implementation.
- Integrated optional support for shell auto-completion using `argcomplete`.
- Added capabilities to determine bookmark state (open/closed) to the TOC parser. Thanks to PDFium Team for reviewing/merging the CL.
- Improved tests for PDF boxes, setup, and table of contents code.
- Integrated the release notes script into setup code.
- Added means to build PDFium with system-provided ICU.
- Fixed `make build`.
- Blocked `pip==22.1` in CI due to a regression related to `--no-build-isolation`.


## 1.8.0 (2022-05-09)

- Updated PDFium from `5038` to `5052`.
- Added support model for text insertion. Special thanks to Anurag Bansal.
- Created a new function `open_page()`, mainly to avoid internal duplication. This basically is a wrapper around `FPDF_LoadPage()` with page index validation.
- Improved cedits section in the Readme.
- Made automatic buffer closure optional for `open_pdf_buffer()`.
- Tweaked the build script.
- Enhanced integration of markdown files into the Sphinx documentation.


## 1.7.0 (2022-05-02)

- Updated PDFium from `5024` to `5038`.
- Improved integration of custom setup tooling.
- Added musllinux wheels for x64 and x86.


## 1.6.0 (2022-04-25)

- Updated PDFium from `5010` to `5024`.
- Removed the undocumented version aliases `__version__` and `__pdfium_version__`. Please use `V_PYPDFIUM2` and `V_LIBPDFIUM` instead.
- Added a project description to the [GitHub organisation page](https://github.com/pypdfium2-team).


## 1.5.0 (2022-04-18)

- Updated PDFium from `4997` to `5010`.


## 1.4.1 (2022-04-18)

- Changed string formatting from `"{}".format(...)` to `"%s" % (...)`.
- Added an option to save documents at a specific PDF version.
- In `pdf_renderer.py`, notable style improvements were applied to the implementation of concurrency.
- In `render_pdf_base()`, the amount of zeros prepended to the serial number is now adaptive to the `page_indices` parameter.
- Revised parts of the documentation.
- Added a Python script to create release notes in a more flexible way in the GitHub workflow.

*After an initial build failure at pdfium-binaries, we had decided to publish a release without updating PDFium. Since the build failure was fixed shortly afterwards, there were two releases on 2022-04-18. Their support model code is identical, though.*


## 1.4.0 (2022-04-11)

- Updated PDFium from `4983` to `4997`.
- Added a GitHub workflow to test the PyPI release wheels on different platforms.


## 1.3.0 (2022-04-04)

- Updated PDFium from `4969` to `4983`.
- Fixed downloading or updating PDFium in the source build script, which was broken because of the `skip_deps` patch. The purpose of this patch was to speed up downloading, but we now removed it to avoid breakage when the upstream `DEPS` file changes.
- Fixed `save_pdf()` to include deletions. We wrongly used the `FPDF_INCREMENTAL` flag, which meant that only additions or modifications were saved. The function is now changed to use the correct flag `FPDF_NO_INCREMENTAL`.
- Added a GitHub workflow to largely automate the release process.

*Releases since 1.3.0 are uploaded using GitHub Actions CI.*


## 1.2.0 (2022-03-28)

- Updated PDFium from `4955` to `4969`.
- Fixed running `setup.py` on Windows by not using `os.mknod()`, which is only available on Unix-like systems.
- Addressed some Windows-specific issues with the build script.


## 1.1.0 (2022-03-21)

- Updated PDFium from `4943` to `4955`.
- Improved style of subprocess calls to use lists rather than strings. This is more elegant, and safer in terms of whitespace handling.


## 1.0.0 (2022-03-14)

- Updated PDFium from `4915` to `4943`.
- Added support for Linux x86 platform (i686).
- API-breaking changes:
  * Removed deprecated members `open_pdf()` and `print_toc()`.
  * Restructured rendering functions to provide multiple different output types:
    `render_page_topil()` and `render_page_tobytes()` replace `render_page()`; similarly, `render_pdf_topil()` and `render_pdf_tobytes()` replace `render_pdf()`.
    These functions are derived from `render_page_base()` and `render_pdf_base()`, respectively.
  * In `render_page_...()` and `render_pdf_...()`, we now only accept RGBA tuples for the colour parameter.
- The Pillow dependency is now optional in the core library.
- Removed workarounds for non-ascii filepaths on Windows. The issues with `FPDF_LoadDocument()` should be fixed since PDFium `4915`. Thanks to Lei Zhang and Thomas Sepez of PDFium team.
- Added some boilerplate code to setup scripts to make sure imports always work when the file is invoked directly.
- Enhancements to `build_pdfium.py`:
  * Improved configuration handling to use dictionaries rather than lists. This is a lot more elegant and flexible.
  * Added an option to dynamically link against system libraries instead of statically linking against bundled dependencies.
  * Integrated a patch to speed up downloading by skipping unnecessary dependencies (such as Skia or V8).
  * Improved finding of system llvm/lld binaries for native build.
- Improved setup status tracking.
- Started removing manual line breaks to simplify editing. Any decent text editor or diff tool should provide automatic word wrap.

*Releases since 1.0.0 have git tags so that you can easily determine the corresponding commit.*


## 0.15.0 (2022-02-28)

- Updated PDFium from `4901` to `4915`.
- Improved build and update scripts:
  * Enhanced Python API accessibility so that the main functions can now be invoked directly, without the need for argparse.
  * Simplified code related to platform names and corresponding data directories to achieve more flexibility and reduce complexity.
  * Modified commands to ensure that paths or links are properly wrapped in double quotes.
  * Regrouped patches to be operating system specific.
- Updated setup configuration:
  * We are now using `setup_requires` for setup dependencies, rather than a custom `build` group in `extras_require`.
  * Explicitly blacklisted Python 3.7.6 and 3.8.1 as incompatible due to a regression in CPython that broke ctypesgen-created string handling code.
- Started moving type hints from code into docstrings. This makes the function headers easier to read and would help running the library with older versions of Python.


## 0.14.0 (2022-02-21)

- Updated PDFium from `4888` to `4901`.
- Completed support model for PDF boxes (new functions `get_bleedbox()`, `get_trimbox()`, and `get_artbox()`)
- Fixed automatic dependency installation for platforms where the Python executable is not named `python3`.
- Tweaked wheel tags to improve compatibility. Changed related code that assigns the tags.
- Completely reworked the setup infrastructure to achieve PEP 517 compliance. Thanks to Anderson Bravalheri for the invaluable help.
- Improved documentation:
  * Wrote instructions on how to add support for a new platform.
  * Restructured the table of contents.
  * Created a `.readthedocs.yaml` configuration, mainly to make the documentation builder use PEP 517 compliant setup.
- General clean-up and lots of minor enhancements.


## 0.13.1 (2022-02-15)

- Fixed a logical issue related to the internal class definitions and imports: `PdfContext` should be defined in `opener.py` rather than `classes.py`, since `PdfDocument` already requires importing components that use `PdfContext`, causing a possible circularity. While the Python interpreter seems to have automatically resolved these conflicts and the test suite passed, this has been a logical mistake to be addressed with this patch release.


## 0.13.0 (2022-02-14)

- Updated PDFium from `4874` to `4888`.
- In `render_page()`, the bitmap is now directly initialised with the right colour format, rather than always using RGBA and converting afterwards. This is expected to improve performance when rendering without alpha channel, in particular for greyscale.
- Installed a new support model class `PdfDocument` on top of the separate helper functions, for object oriented document access. This should be easier to use and more like the API of other Python PDF libraries.
- Fixed `setup.py` to always call `getdeps` first, before other imports that already require packages that `getdeps` should install.
- Restructured platform-specific setup to greatly reduce code duplication.
- Moved setup-related code into an own directory, to be able to use cleaner imports, and to avoid messing up the root directory of the repository.
- Adapted the Makefile to setup changes and added documentation commands.
- Improvements related to license files:
  * Made the repository fully compliant with the `reuse` standard.
  * Moved the PDFium wheel license into the `LICENSES/` directory and removed its embedded copies of `Apache-2.0` and `BSD-3-Clause` since they are duplicates.
- Fixed link on the PyPI page to point at the stable documentation, not the development build.


## 0.12.0 (2022-02-07)

- Updated PDFium from `4861` to `4874`.
- Restructured file opening to finally address the Windows issues with non-ascii filenames by implementing a support model for `FPDF_LoadCustomDocument()`, which allows us to do file reading on the Python side if necessary. For this purpose, the following changes to opener functions have been made:
  * Added `open_pdf_buffer()` to incrementally load a document from a byte buffer.
  * Added `open_pdf_native()` to load a PDF file, with reading being done in Python natively using `open_pdf_buffer()`.
  * Added `open_pdf_auto()`, which will use `FPDF_LoadDocument()` for regular file paths, `open_pdf_native()` for non-ascii filepaths on Windows, and `open_pdf_buffer()` for bytes or byte buffers.
  * Adapted `PdfContext` to use `open_pdf_auto()`.
  * Marked `open_pdf()` as deprecated. It should not be used anymore and may be removed at some point.
- Improved the command line interface to list help and version commands in the main help. Also made the internals more flexible to allow multiple names for the same command.
- Moved changelog, dependencies, contributing, and tasks files into `docs/markdown/`. They are now included in the Sphinx documentation using `myst-parser`.
- Splitted up support model tests into separate files for improved readability and extensibility.
- Cleaned up some typos, unused variables and excessive imports.


## 0.11.0 (2022-01-31)

- Updated PDFium from `4849` to `4861`.
- Overhauled the command-line interface to group different tasks in subcommands. It should be a lot cleaner now; easier to use and extend. These modifications make the command-line API incompatible with previous releases, though. In the course of this restructuring, the following functional changes were applied:
  * Made rendering output format customisable by providing control over the file extension to use, from which the `Pillow` library will be able to automatically determine the corresponding encoder.
  * Changed the rendering parser to accept multiple files at once.
  * Positional arguments are now used for file input.
  * Added CLI commands for merging PDFs and performing page tiling (N-up).
  * Temporarily removed support for working with encrypted PDFs while we are looking for a
    suitable way to take passwords of multiple files.
- Adapted documentation to the CLI changes.
- When opening from a byte buffer, any object that implements the `.read()` method is now accepted (previously, only `BytesIO` and `BufferedReader` were supported). Note that we do not automatically seek back to the start of the buffer anymore.
- Restructured installing the exit handler, so that its function is no longer inadvertently part of the public namespace.
- Removed the `None` defaults of the table of contents helper class `OutlineItem`. The parameters are now passed at construction time.
- Greatly improved `setup.py`: Formerly, running `pip3 install .` always triggered a source build, on behalf of platforms for which no wheel is available. With this release, the code was changed to detect the current platform and use pre-compiled binaries if available, with source build only as fallback.
- On setup, the version file is now always read literally (i. e. without importing the module), which makes it a lot less prone to errors.
- Modernised the update script code that reads and writes the version file.
- Added notes concerning the need for a recent version of pip when installing from source. Tried to improve compatibility with older releases in the scope of what is possible.
- Added test cases to ensure existence of version aliases and correctness of CLI entry point configuration.
- Updated the Makefile.
- Removed KDevelop project files from the repository.


## 0.10.0 (2022-01-24)

- Updated PDFium from `4835` to `4849`.
- Completely rearranged the internal structure of the support model. The public API should be mostly unaffected by these changes, however.
- Adapted documentation and tests to the support model changes.
- Modifications to exceptions:
    * `LoadPdfError` and `LoadPageError` were removed. The more general `PdfiumError` is now raised instead. This is because the exception handler may be used universally for more situations than just loading PDF documents or pages.
    * `PageIndexError` was replaced with `IndexError`. A custom exception seemed unnecessary for this case.
- New support models added:
    * Function `save_pdf()` to create a PDF file from an `FPDF_DOCUMENT` handle. This is demonstrated in the example `merge_pdfs.py`.
    * Methods `get_mediabox()` and `get_cropbox()` to retrieve PDF boxes of an `FPDF_PAGE`.
    * Made the utility functions `translate_viewmode()` and `translate_rotation()` public.
- Removed the in-library logging setup as it could cause issues for downstream users who wish to configure the pypdfium2 logger.
- Started backporting pypdfium2 to older Python versions by removing all uses of f-strings, keywords-only enforcement, and `pathlib` across the package. The minimum required Python version is now 3.5. (It might be possible to further reduce the requirement by moving type hints from the actual code into docstrings.)
- Minor optimisations have been made to the table of contents helper functions.
- Improved build scripts.
- Adapted the update script to upstream changes (thanks @bblanchon).
- Moved some scripts from the root directory into `utilities/` and changed the Makefile accordingly.
- Added a list of future tasks to keep in mind.

*Tracking changes started with version 0.10.0, so there are no entries for older releases.*
