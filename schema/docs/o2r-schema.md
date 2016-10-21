---
title: 'o2r metadata schema documentation'
author: o2r-project
version: 0.022
license: CC-BY 4.0 International
---

# o2r metadata schema documentation

## 0. Schema location
Current schema draft for descriptive metadata of the asset, e.g. software:

- <https://raw.githubusercontent.com/o2r-project/o2r-meta/master/schema/json/o2r-meta-schema.json>

Current schema draft for interaction metadata, i.e. UI widgets:

- <https://raw.githubusercontent.com/o2r-project/o2r-meta/master/schema/json/o2r-meta-ui-schema.json>

## 1. Purpose

This is a work-in-progress documentation of the metadata schema used for _executable research compendia_, focusing to depict package dependencies and other requirements for reproducible computational environments as well as compliance with existing modern metadata standards, e.g. DataCite 4.0 schema.
In its current state these metadate elements, properties and definitions strongly rely on the [CodeMeta](https://github.com/codemeta/codemeta) software metadata concepts, extending them for the interaction with software in the context of Reproducible Research. Rationales of CodeMeta equivalents are taken from or based on the corresponding descriptions.
The required information for a complete set of o2r metadata according to this schema are gathered by automated extraction and collection from the creator of the asset.

## 2. Metadata elements

### Main Schema

- ```Author``` (mandatory, 1-n)
 - ```AuthorAffiliation``` (mandatory, 1-n)
 - ```AuthorId``` (optional, 0-n)
 - ```AuthorName``` (mandatory, 1)
- ```DateCreated``` (optional, 0-1)
- ```Dependency``` (mandatory, 1-n)
 - ```operatingSystem``` (optional, 0-n)
 - ```packageId``` (mandatory, 1)
 - ```packageSystem``` (mandatory, 1)
 - ```version``` (mandatory, 1)
- ```Description``` (mandatory, 1)
- ```ErcIdentifier``` (mandatory, 1)
- ```GeneratedBy``` (mandatory, 1)
- ```InteractionMethod``` (optional, 0-n)
- ```Keywords``` (mandatory, 1-n)
- ```ObjectType``` (optional, 0-1)
- ```PaperLanguage``` (optional, 0-n)
- ```RecordDateCreated``` (optional, 0-1)
- ```SoftwarePaperCitation``` (optional, 0-1)
- ```Title``` (mandatory, 1)
- ```Version``` (mandatory, 1)

### UI Schema
The following meta information are used to control widgets for interaction with ERCs on our platform.

- ```ErcIdentifier``` (mandatory, 1)
- ```checkboxes``` (optional, 0-n)
 - ```label``` (mandatory, 1)
 - ```value``` (mandatory, 1)
 - ```is_checked``` (mandatory, 1)
 - ```parameter_type``` (mandatory, 1)
 - ```reference_point``` (mandatory, 1)
- ```radiobuttons``` (optional, 0-n)
 - ```label``` (mandatory, 1)
 - ```value``` (mandatory, 1)
 - ```is_checked``` (mandatory, 1)
 - ```parameter_type``` (mandatory, 1)
 - ```reference_point``` (mandatory, 1)
- ```sliders``` (optional, 0-n)
 - ```label``` (mandatory, 1)
 - ```value``` (mandatory, 1)
 - ```value_max``` (mandatory, 1)
 - ```value_min``` (mandatory, 1)
 - ```is_checked``` (mandatory, 1)
 - ```parameter_type``` (mandatory, 1)
 - ```reference_point``` (mandatory, 1)


## 3. Rationales

- Author
> A block for each creator of the asset.

- ⌞ Author/AuthorAffiliation
> The institution, organization or other group that the creator of the asset is associated with.

- ⌞ Author/AuthorId
> A universally unique character string that is associated with the author, e.g."http://orcid.org/0000-0002-1825-0097".

- ⌞ Author/AuthorName
> The name of the human individual, institution, organization, machine or other entity that acts as creator of the asset.

- DateCreated
> The date that a published version of the asset was created by the author.

- Dependency
> A block for each entity that the software is dependent on for execution.

- ⌞ Dependency/operatingSystem
> The operating system for the software to run under.

- ⌞ Dependency/packageId
> An identification string for the dependency entity that is unique in the corresponding package system.
 
- ⌞ Dependency/packageSystem
> The package manager system that makes the dependency entity available.
 
- ⌞ Dependency/version
> The computer software and hardware required to run the software.

- Description
> A text representation conveying the purpose and scope of the asset.

- ErcIdentifier
> A universally unique character string associated with the asset as _executable research compendium_.

- GeneratedBy
> The entity, person or tool, that created the software.

- InteractionMethod
> The specified method(s) that can be used to interact with the software (e.g. command-line vs. GUI vs. Excel..., entry points).

- Keywords
> Keywords (tags) associated with the asset.

- ObjectType
> The category of the resource that is associated with the software. TO DO: controlled list, such as software, paper, data, image...

- PaperLanguage
> A list of the specific counties or regions that the software has been adapted to, e.g. “en-GB,en-US,zh-CN,zh-TW” (if using the ISO 639-1 standard codes).

- RecordDateCreated
> The date that this metadata record describing the asset was created.

- SoftwarePaperCitation
> A text string that can be used to authoritatively cite a research paper, conference proceedings or other scholarly work that describes the design, development, usage, significance or other aspect of the software.

- Title
> The distinguishing name associated with the asset.

- Version
> A unique string indicating a specific state of the software, i.e. an initial public release, an update or bug fix release, etc. No version format or schema is enforced for this value.

