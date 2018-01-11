This is a documentation on the metadata elements provided by the o2r meta extract.


_Last updated: 2017-12-01, work in progress!_ 

# Elements of the o2r metadata file

- `access_right` _String_.
- `creators` _Array of objects_.
- `creators.name` _String_.
- `creators.orcid` _String_.
- `creators.affiliation` _String_.
- `codefiles` _Array of strings_ List of all files of the recursively parsed workspace that have an extension belonging to a ("R") codefile.
- `communities` _Array of objects_ prepared zenodo MD element
- `communities[0].identifier` _String_. Indicating the collection as required in zenodo MD, default "o2r".
- `depends` _Array of objects_.
- `depends.operatingSystem` _String_.
- `depends.identifier` _String_.
- `depends.packageSystem` _String_. URL
- `depends.version` _String_.
- `description` _String_. A text representation conveying the purpose and scope of the asset (the abstract).
- `displayfile` _String_. The suggested file for viewing the text of the workspace, i.e. a rendering of the suggested mainfile.
- `displayfile_candidates` _Array of strings_. An unsorted list of candidates for displayfiles.
- `ercIdentifier` _String_. A universally unique character string associated with the asset as executable research compendium, provided by the o2r service.
- `identifier` _Object_.
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
- `publication_date` _String_. The publication date of the paper publication as ISO8601 string.
- `publication_type` _String_.
- `related_identifier` _String_.
- `spatial` _Object_. Spatial information of the workspace.
- `spatial.files` _Array of objects_.
- `spatial.union` _Array of objects_.
- `temporal` _Object_. Aggregated information about the relevant time period of the underlying data sets.
- `temporal.begin`
- `temporal.end`
- `title` The distinguishing name of the paper publication.
- `upload_type` _String._ Zenodo preset. Defaults to "publication".

