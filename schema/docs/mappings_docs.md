This is a documentation on the minimal language used in the o2r-meta mappings that provide instructions for metadata translation as used by the broker tool.


# Format
The mapping files are json.


# Validity
The mapping files must be valid according to the map-schema.json file, located at _schema/json/map-schema.json_.


# Structure
Every mapping file has two sections, represented by json keys. The first section is "Settings". It stores properties of the map, used for configuration.
The second section is "Map" with includes instructions for each metadata element that will be translated by the broker.
The mapping file may contain additional keys on the top level, e.g. "Map_disabled" that indicate future additions of temporally excluded metadata elements. These additional top level keys will be ignored by the broker.


# Settings Elements
- *name* This key indicates the name of the mapping file.
- *outputfile* This key determines name of the output file, created by the broker tool.
- *map_description* This key contains a description of the purpose of the mapping file.
- *const* This key contains a list of json objects that will be added to the translated file at top level regardless of the input file
- *mode* This key determines the translation mode for the map, e.g. json or xml.
- *root* This key indicates the root element that will be created for the metadata translation.
- *root@xmlns* This key indicates the xml namespace for the source metadata file, if mode is xml.


# Map Elements
A metadata element of the "Map" section of the mapping file may look as follows:

```
		"name": {
			"translatesTo": "name",
			"type": "string",
			"hasParent": "author",
			"needsParent": "creators"
		},
```
The name of each key represents the name of the metadata element that needs to be translated by the broker.

Meaningful subkeys are:

- *translatesTo* This key indicates the string that is the target translation for the element.
- *type* This key indicates the data type of the element. Additionally the *type* can have the value `new` to indicate that a new key has to be created by the broker. This is needed for sub element metadata to become top level elements.
- *hasParent* This key indicates the name of the parent key that the metadata element belongs to.
- *needsParent* This key indicates the target translation for the parent keys of the metadata element.




