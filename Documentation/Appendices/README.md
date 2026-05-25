# Project Appendices Folder

Place all your PDF appendices, Astah files, or other documentation files here. They will be automatically packaged into the final submission zip folder when you run the build script.

Recommended files to place here:

1. **Project Description** (e.g. `Project_Description.pdf`)
2. **Group Contract** (e.g. `Group_Contract.pdf`)
3. **User Guide / Installation Guide** (e.g. `User_Installation_Guide.pdf` or separate files)
4. **Astah Files** (e.g. `StudyHelper.astah`) - or in our case puml and such
5. **Additional Calculations or Drawings** (in PDF/SVG format)

## Automatic Packaging

When the `./build_submission.sh` script is executed, it will:

1. Compile and merge the reports into `Documentation/StudyHelper_Final_Handin.pdf`.
2. Convert all PNG diagrams under `Documentation/` to PDF format.
3. Automatically zip this `Appendices` folder along with the project source code directories (`API`, `Frontend`, `IOT`, `MAL`) into a single `StudyHelper_Appendices.zip` file, ready for WISEflow upload.
