version 0.02 |
created by o2r-project |
part of <https://github.com/o2r-project/o2r-meta> |
this documentation is licensed under CC-BY 4.0 International

# o2r metadata schema documentation

## 0. Schema location
Schema draft for descriptive metadata:
<https://raw.githubusercontent.com/o2r-project/o2r-meta/master/schema/json/o2r-meta-schema.json>
Schema draft for interaction metadata, i.e. UI widgets:
<https://raw.githubusercontent.com/o2r-project/o2r-meta/master/schema/json/o2r-meta-schema-ui.json>

## 1. Purpose

This is a work-in-progress documentation of the metadata schema used for _executable research compendia_.
In its current state these metadate elements, properties and definitions strongly rely on the Codemeta software metadata concepts, available at <https://github.com/codemeta/codemeta>. Rationales of codemeta equivalents are taken from or based on the corresponding descriptions.
The required information for a complete set of o2r metadata according to this schema are gathered by automated extraction and collection from the creator of the software in executable research compendia.

## 2. Metadata elements

- ```AuthorAffiliation``` (required, 1-n)
- ```AuthorId``` (required, 1-n)
- ```AuthorName``` (required, 1-n)
- ```DateCreated``` (required, 1)
- ```Dependency``` (required, 1-n)
- ```Description``` (required, 1)
- ```GeneratedBy``` (required, 1-n)
- ```InteractionMethod``` (0-n)
- ```ObjectType``` (0-1)
- ```RecordDateCreated``` (0-1)
- ```SoftwarePaperCitation``` (required, 1-n)
- ```Version``` (required, 1-n)
- ```ErcIdentifier``` (required, 1)
- ```Title``` (required, 1)
- ```Keywords``` (required, 1-n)
- ```PaperLanguage``` (required, 1)

## 3. Rationales

- AuthorAffiliation
> The institution, organization or other group that the software creator is associated with.

- AuthorId
> A universally unique character string that is associated with the software author, e.g."http://orcid.org/0000-0002-1825-0097".

- AuthorName
> The name of the institution, organization, individuals or other entities that created the software.

- DateCreated
> The date that a published version of the software was created by the author.

- Dependency
> The computer software and hardware required to run the software.

- Description
> A text representation conveying the purpose and scope of the software.

- GeneratedBy
> The entity, person or tool, that created the software.

- InteractionMethod
> The specified method(s) that can be used to interact with the software (e.g. command-line vs. GUI vs. Excel..., entry points).

- ObjectType
> The category of the resource that is associated with the software. TO DO: controlled list, such as software, paper, data, image...

- RecordDateCreated
> The date that this metadata record describing the software was created.

- SoftwarePaperCitation
> A text string that can be used to authoritatively cite a research paper, conference proceedings or other scholarly work that describes the design, development, usage, significance or other aspect of the software.

- Version
> A unique string indicating a specific state of the software, i.e. an initial public release, an update or bug fix release, etc. No version format or schema is enforced for this value.

- ErcIdentifier
> A universally unique character string associated with the software.

- Title
> The distinguishing name associated with the software.

- Keywords
> Keywords (tags) associated with the software.

- PaperLanguage
> A list of the specific counties or regions that the software has been adapted to, e.g. “en-GB,en-US,zh-CN,zh-TW” (if using the ISO 639-1 standard codes).
