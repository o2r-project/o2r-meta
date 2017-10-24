This is a documentation on the metadata elements provided by the o2r meta extract.


_Last updated: 2017-10-20, work in progress!_ 

# Elements of the raw metadata file

- `access_right`_String_. Zenodo preset. Defaults "open".
- `author` _Array of objects_. 
- `author[0].affiliation` _String_.
- `author[0].name` _String_.
- `author[0].orcid`_String_.
- `author. (...)` Additional subelements from extracted rmd yaml header
- `bagit` _Object_.
- `bagit.bagittxt_files`_Array of strings_. List of extracted _bagit.txt_ files.
- `codefiles` _Array of strings_ List of all files of the recursively parsed workspace that have an extension belonging to a ("R") codefile.
- `communities` _Array of objects_ prepared zenodo MD element
- `communities[0].identifier` _String_. Indicating the collection as required in zenodo MD, default "o2r".
- `depends` _Array of objects_. Lists all extracted library requirements, e.g. R packages.
- `depends[0].identifier` _String_. The name of the extracted dependency.
- `description` _String_.
- `displayfile` _String_. 
- `displayfile_candidates` _Array of strings_.
- `ercIdentifier` _String_. A universally unique character string associated with the asset as executable research compendium, provided by the o2r service.
- `file`_Object_. _Deprecated_.
- `file.filename` _String_. _Deprecated_.
- `file.filepath` _String_. _Deprecated_.
- `file.mimetype` _String_. _Deprecated_.
- `generatedBy` _String_. 
- `identifier` _Object_.
- `identifier.doi` _String_. DOI
- `identifier.doiurl` _String_. DOI as URL
- `identifier.reserveddoi` _String_. _Deprecated_.
- `inputfiles` _Array of strings_. A compiled list of files from the extracted workspace that is called or used in the extracted code of the workspace.
- `interaction` TBD
- `keywords` _Array of strings_.
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
- `r_comment.feature` _String_.
- `r_comment.line` _Integer_.
- `r_comment.text` _String_.
- `r_input`  _Array of objects_. Input contexts in extracted R code.
- `r_input[0].feature` _String_
- `r_input[0].line` _Integer_.
- `r_input[0].text` _String_.
- `r_output` _Array of objects_. Output contexts in extracted R code.
- `r_output[0].feature` _String_.
- `r_output[0].line`_Integer_.
- `r_output[0].text` _String_.
- `r_rdata` _Array of objects_.
- `recordDateCreated` _String_. The publication date of the paper publication as ISO8601 string.
- `researchHypotheses` _Array of strings_. _Deprecated_.
- `researchQuestions` _Array of strings_. _Deprecated_.
- `softwarePaperCitation` _String_.
- `spatial` _Object_. Spatial information of the workspace.
- `spatial.files` _Array of objects_.
- `spatial.files.bbox`_Array of strings_. Contains the coordinates of the corresponding bounding box of the file.
- `spatial.files.name` _String_. File names extracted from.
- `spatial.union` _Object_.
- `spatial.union.bbox`_Array of array of strings_. The union bounding box of the spatial extractions (files). _Will be made geojson compatible_.
- `temporal` _Object_. Aggregated information about the relevant time period of the underlying data sets.
- `temporal.begin`The starting point of the relevant time period.
- `temporal.end` The end point of the relevant time period.
- `title` The distinguishing name of the paper publication.
- `upload_type` _String._ Zenodo preset "publication".
- `version` _String_. _Deprecated._



---

Example dummy file:

```
{
    "access_right": "open",
    "author": [
        {
            "Telephone": "+00/00/1000-2000",
            "address": "This might be a correct address Yet it might also be lorem ipsum\\newline Another line 252b\\newline 00000 Anywhere, Nomansland\n",
            "affiliation": "University of Munster",
            "affiliation2": "University of Nowhere",
            "email": "ted.tester@awebsite8372930.org",
            "name": "Ted Tester",
            "orcid": null,
            "url": "\\url{http://404.awebsite8372930.org}"
        },
        {
            "affiliation": "N.O.N.E",
            "name": "Carl Connauthora",
            "orcid": null
        }
    ],
    "bagit": {
        "bagittxt_files": []
    },
    "codefiles": [
        "extract/tests/test1.R",
        "extract/tests/test2.Rmd"
    ],
    "communities": [
        {
            "identifier": "o2r"
        }
    ],
    "depends": [
        {
            "category": "geo sciences,CRAN Top100",
            "identifier": "RColorBrewer",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        },
        {
            "category": "geo sciences,CRAN Top100",
            "identifier": "dplyr",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        },
        {
            "category": "geo sciences,CRAN Top100",
            "identifier": "ggplot2",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        },
        {
            "category": null,
            "identifier": "definitivelyUnknownPackage",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        },
        {
            "category": "CRAN Top100",
            "identifier": "minqa",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        },
        {
            "category": "geo sciences",
            "identifier": "PBSmapping",
            "packageSystem": "https://cloud.r-project.org/",
            "version": null
        }
    ],
    "description": "Tempus eget nunc eu, lobortis condimentum nulla. Nam sagittis massa nec libero luctus facilisis. Suspendisse ac ornare ligula. Morbi non dignissim sem. Pellentesque eleifend neque nec dui interdum varius.\n",
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
        "doi": "10.9999/test",
        "doiurl": "https://doi.org/10.9999/test",
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
    "keywords": [
        "lorem",
        "ipsum",
        "dolor",
        "sit",
        "amet"
    ],
    "license": {
        "code": null,
        "data": null,
        "md": null,
        "text": null,
        "uibindings": null
    },
    "mainfile": "extract/tests/test2.Rmd",
    "mainfile_candidates": [
        "extract/tests/test1.R",
        "extract/tests/test2.Rmd"
    ],
    "paperLanguage": [
        "en"
    ],
    "paperSource": null,
    "provenance": {
        "extract/tests/test2.Rmd": "parsers.parse_rmd parse"
    },
    "publicationDate": "2017-10-19",
    "publication_type": "other",
    "r_comment": [
        {
            "feature": "comment",
            "line": 10,
            "text": "Trying some seperation lines:"
        },
        {
            "feature": "comment",
            "line": 14,
            "text": "chunk: random string"
        },
        {
            "feature": "comment",
            "line": 20,
            "text": "umlaut \u00f6 \u00e4 \u00fc \u00df"
        },
        {
            "feature": "comment",
            "line": 24,
            "text": "some plot"
        }
    ],
    "r_input": [
        {
            "feature": "data input",
            "line": 19,
            "text": "anyfile.csv"
        }
    ],
    "r_output": [
        {
            "feature": "setseed",
            "line": 15,
            "text": "42"
        },
        {
            "feature": "result",
            "line": 25,
            "text": "plot"
        },
        {
            "feature": "result",
            "line": 27,
            "text": "print"
        }
    ],
    "r_rdata": [],
    "recordDateCreated": null,
    "researchHypotheses": [],
    "researchQuestions": [],
    "softwarePaperCitation": null,
    "spatial": {
        "files": [
            {
                "bbox": [
                    12.04195976257324,
                    12.042903900146483,
                    50.07708274998269,
                    50.077633570782616
                ],
                "name": "extract/tests/geojson/test2_map.geojson"
            },
            {
                "bbox": [
                    7.606143951416016,
                    7.612967491149902,
                    51.961509706685675,
                    51.965872760333085
                ],
                "name": "extract/tests/geojson/test_map.geojson"
            }
        ],
        "union": {
            "bbox": [
                [
                    7.606143951416016,
                    7.612967491149902
                ],
                [
                    12.04195976257324,
                    7.612967491149902
                ],
                [
                    12.04195976257324,
                    12.042903900146483
                ],
                [
                    7.606143951416016,
                    12.042903900146483
                ]
            ]
        }
    },
    "temporal": {
        "begin": null,
        "end": null
    },
    "title": "This is the title: it contains a colon",
    "upload_type": "publication",
    "version": null
}

```
