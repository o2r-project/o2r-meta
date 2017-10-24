This is a documentation on the metadata elements provided by the o2r meta extract.


_Last updated: 2017-10-24, work in progress!_ 

# Elements of the raw metadata file

- `access_right`_String_. Zenodo preset. Defaults "open".
- `author` _Array of objects_. 
- `author[0].affiliation` _String_.
- `author[0].name` _String_.
- `author[0].orcid`_String_.
- `author[0]. (...)` Additional subelements from extracted rmd yaml header
- `bagit` _Object_. Information on the bagit bag if present.
- `bagit.bagittxt_files`_Array of strings_. List of extracted _bagit.txt_ files.
- `codefiles` _Array of strings_ List of all files of the recursively parsed workspace that have an extension belonging to a ("R") codefile.
- `communities` _Array of objects_ prepared zenodo MD element
- `communities[0].identifier` _String_. Indicating the collection as required in zenodo MD, default "o2r".
- `depends` _Array of objects_. Lists all extracted library requirements, e.g. R packages.
- `depends[0].identifier` _String_. The name of the extracted dependency.
- `description` _String_. A text representation conveying the purpose and scope of the asset (the abstract).
- `displayfile` _String_. The suggested file for viewing the text of the workspace, i.e. a rendering of the suggested mainfile.
- `displayfile_candidates` _Array of strings_. An unsorted list of candidates for displayfiles.
- `ercIdentifier` _String_. A universally unique character string associated with the asset as executable research compendium, provided by the o2r service.
- `file`_Object_. _Deprecated_.
- `file.filename` _String_. _Deprecated_.
- `file.filepath` _String_. _Deprecated_.
- `file.mimetype` _String_. _Deprecated_.
- `generatedBy` _String_. The entity, person or tool, that created the software. Defaults to o2r meta.
- `identifier` _Object_.
- `identifier.doi` _String_. DOI
- `identifier.doiurl` _String_. DOI as URL
- `identifier.reserveddoi` _String_. _Deprecated_.
- `inputfiles` _Array of strings_. A compiled list of files from the extracted workspace that is called or used in the extracted code of the workspace.
- `interaction` TBD
- `keywords` _Array of strings_. Tags associated with the asset.
- `license`_Object_.  License information for the entire ERC.
- `license.code` _String_. License information for the code included.
- `license.data `_String_. License information for the data included.
- `license.md` _String_. License information for the metadata included. Should be cc0 to include in catalogues.
- `license.text`_String_. License information for the text included.
- `license.uibindings` _String_. License information for the UI-bindings included.
- `mainfile` _String_. The suggested main file of workspace
- `mainfile_candidates` _Array_. Unsorted list of mainfile candidates of the workspace.
- `paperLanguage` _Array of strings_. List of guessed languages for the workspace.
- ~~`paperSource` _String_.~~ _Deprecated_.
- `provenance`  _Array of objects_. More information of where the MD came from.
- `publicationDate` _String_. The publication date of the paper publication as ISO8601 string.
- `publication_type` _String_. Zenodo preset. Defaults to "other".
- `r_comment` _Array of objects_. Comments in extracted R code.
- `r_comment.feature` _String_. The kind of comment feature encountered.
- `r_comment.line` _Integer_. Line number.
- `r_comment.text` _String_. Text of the comment.
- `r_input`  _Array of objects_. Input contexts in extracted R code.
- `r_input[0].feature` _String_ The kind of input feature encountered.
- `r_input[0].line` _Integer_. Line number.
- `r_input[0].text` _String_. Value of the input context.
- `r_output` _Array of objects_. Output contexts in extracted R code.
- `r_output[0].feature` _String_. The kind of output feature encountered.
- `r_output[0].line`_Integer_. Line number.
- `r_output[0].text` _String_. Value of the output context.
- `r_rdata` _Array of objects_.
- `recordDateCreated` _String_. The publication date of the paper publication as ISO8601 string.
- `researchHypotheses` _Array of strings_. _Deprecated_.
- `researchQuestions` _Array of strings_. _Deprecated_.
- `softwarePaperCitation` _String_.
- `spatial` _Object_. Spatial information of the workspace.
- `spatial.files` _Array of objects_.
- `spatial.files.bbox`_Array of strings_. Contains the coordinates of the corresponding bounding box of the file.
- `spatial.files.name` _String_. File names extracted from.
- `spatial.union` _Object_. A combination of the extracted spatial information.
- `spatial.union.bbox`_Array of array of strings_. The union bounding box of the spatial extractions (files). _Will be made geojson compatible_.
- `temporal` _Object_. Aggregated information about the relevant time period of the underlying data sets.
- `temporal.begin`The starting point of the relevant time period.
- `temporal.end` The end point of the relevant time period.
- `title` The distinguishing name of the paper publication.
- `upload_type` _String._ Zenodo preset. Defaults to "publication".
- `version` _String_. _Deprecated._



---

Example dummy file:

```
{
    "access_right": "open",
    "author": [],
    "bagit": {
        "bagittxt_files": []
    },
    "codefiles": [],
    "communities": [
        {
            "identifier": "o2r"
        }
    ],
    "depends": [],
    "description": null,
    "displayfile": null,
    "displayfile_candidates": [],
    "ercIdentifier": null,
    "file": {
        "filename": null,
        "filepath": null,
        "mimetype": null
    },
    "generatedBy": "o2r-meta metaextract.py",
    "identifier": {
        "doi": null,
        "doiurl": null,
        "reserveddoi": null
    },
    "inputfiles": [],
    "interaction": {
        "interactive": false,
        "ui_binding": {
            "code": {
                "filename": null,
                "function": null,
                "functionParameter": null,
                "shinyInputFunction": null,
                "shinyRenderFunction": null
            },
            "purpose": null,
            "variable": null,
            "widget": null
        }
    },
    "keywords": [],
    "license": {
        "code": null,
        "data": null,
        "md": null,
        "text": null,
        "uibindings": null
    },
    "mainfile": null,
    "mainfile_candidates": [],
    "paperLanguage": [],
    "provenance": [],
    "publicationDate": null,
    "publication_type": "other",
    "r_comment": [],
    "r_input": [],
    "r_output": [],
    "r_rdata": [],
    "recordDateCreated": null,
    "researchHypotheses": [],
    "researchQuestions": [],
    "softwarePaperCitation": null,
    "spatial": {
        "files": [],
        "union": null
    },
    "temporal": {
        "begin": null,
        "end": null
    },
    "title": null,
    "upload_type": "publication",
    "version": null
}

```
