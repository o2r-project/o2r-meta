#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mimetypes
import os
import re
import xml.etree.cElementTree as elt
from datetime import date
from xml.dom import minidom


def checkrpacks(myPackage):
    if myPackage in open(packlist_crantop100).read():
        return 'CRAN-top100'
    if myPackage in open(packlist_geopack).read():
        return 'geo'
    else:
        return 'none'

def checkcomments(myComment):
    #monochar string concatenation, likely a seperator line
    if len(myComment) > 1 and myComment == len(myComment) * myComment[0]:
        return 'seperator'
    #email address, likely a contact
    m = re.match(r'(.*[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.].*)', myComment)
    if m is not None:
        return 'contact'
    #URL
    m = re.match(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', myComment)
    if m is not None:
        #DOI
        m = re.match(r'(.*http.*doi\.org.*)', myComment)
        if m is not None:
            return 'DOI'
        else:
            return 'URL'
    #code fragments
    m = re.match(r'(.*\=.*\(.*\))', myComment)
    if m is not None:
        return 'code_fragment'
    #anything else
    else:
        return 'none'

#extract for R
def processfile_R(myPathFile):
    c=0
    root = elt.Element('extracted')
    elt.SubElement(root, 'file').text = str(myPathFile)
    elt.SubElement(root, 'mime-type').text = str(mimetypes.guess_type(myPathFile, strict=False)[1]) #include non IANA mimes
    elt.SubElement(root, 'generator', modus='R').text = 'metaextract.py'
    with open(os.path.relpath(myPathFile), encoding='utf-8') as ifile:
        for line in ifile:
            c+=1
            ##### Comments
            m = re.match('#{1,3}\s*(.{1,})', line)
            if m is not None:
                if len(m.group(1).strip()) > 0:
                    elt.SubElement(root, 'comment', line=str(c), guess=checkcomments(str(m.group(1)))).text = '{}'.format(m.group(1))
            ##### dependency library require packages
            #r package naming conventions
            # "The mandatory ‘Package’ field gives the name of the package. This should contain only (ASCII) letters, numbers and dot,
            # have at least two characters and start with a letter and not end in a dot."
            # http://stackoverflow.com/questions/24201568/whats-a-good-r-package-name
            #r \library
            m = re.match('library\(\"?([a-zA-Z\d\.]*)[\"\)]', line)
            if m is not None:
                elt.SubElement(root, 'dependent_library', line=str(c), guess=checkrpacks(str(m.group(1)))).text = '{}'.format(m.group(1))
            #r \require
            m = re.match('require\(\"?([a-zA-Z\d\.]*)[\"\)]', line)
            if m is not None:
                elt.SubElement(root, 'dependent_require', line=str(c), guess=checkrpacks(str(m.group(1)))).text = '{}'.format(m.group(1))
            #r install.packages
            m = re.match('install.packages\((.*)\)', line)
            if m is not None:
                elt.SubElement(root, 'dependent_installs', line=str(c), guess='list').text = '{}'.format(m.group(1))
            ##### other (pseudo)literate methods of R
            #r input data
            m = re.match('data\..*\((.*)\)', line)
            if m is not None:
                elt.SubElement(root, 'input', line=str(c), guess='dataset').text = '{}'.format(m.group())
            #r output plot or print
            m = re.match('(ggplot|plot|print)\((.*)\)', line)
            if m is not None:
                elt.SubElement(root, 'output', line=str(c), guess='result').text = '{}'.format(m.group())
            #r output saved file
            m = re.match('write\..*\((.*)\)', line)
            if m is not None:
                elt.SubElement(root, 'output', line=str(c), guess='file').text = '{}'.format(m.group())
            #r match fixed random seed sets
            m = re.match('set\.seed\((.*)\)', line)
            if m is not None:
                elt.SubElement(root, 'output', line=str(c), guess='random_seed').text = '{}'.format(m.group())
    #save:
        myExtracted = minidom.parseString(elt.tostring(root)).toprettyxml(indent='\t')
        now = date.today()
        outputfilename = 'metaex_' + os.path.basename(myPathFile)[:8].replace('.', '_') + '_' + str(now) + '.xml'
        with open(outputfilename, 'w', encoding='utf-8') as ofile:
            ofile.write(myExtracted)
        print(str(os.stat(outputfilename).st_size) + ' bytes written to ' + str(outputfilename))

#extract for R markdown
def processfile_Rmd(myPathFile):
    c=0
    root = elt.Element('extracted')
    elt.SubElement(root, 'file').text = str(myPathFile)
    elt.SubElement(root, 'mime-type').text = str(mimetypes.guess_type(myPathFile, strict=False)[1]) #include non IANA mimes
    elt.SubElement(root, 'generator', modus='Rmd').text = 'metaextract.py'
    with open(os.path.relpath(myPathFile), encoding='utf-8') as ifile:
        for line in ifile:
            c += 1
            ##### header
            # title
            m = re.match('\@?title\:\s[\"\'](.*)[\"\']', line)
            if m is not None:
                if len(m.group(1).strip()) > 0:
                    elt.SubElement(root, 'title', line=str(c)).text = '{}'.format(m.group(1))
            # title
            m = re.match('\@?author\:\s\"(.*)\"', line)
            if m is not None:
                if len(m.group(1).strip()) > 0:
                    elt.SubElement(root, 'author', line=str(c)).text = '{}'.format(m.group(1))
            ##### connected files
            # knitr
            m = re.match('knitr\:\:read\_chunk\([\"\'](.*)[\"\']\)', line)
            if m is not None:
                if len(m.group(1).strip()) > 0:
                    elt.SubElement(root, 'related_file', guess='knitr', line=str(c)).text = '{}'.format(m.group(1))
            ##### dependency library require packages
            # to do; usepackage, library, require
            ##### headlines
            # '#' if not included in '```' code blocks
        # save:
        myExtracted = minidom.parseString(elt.tostring(root)).toprettyxml(indent='\t')
        now = date.today()
        outputfilename = 'metaex_' + os.path.basename(myPathFile)[:8].replace('.', '_') + '_' + str(now) + '.xml'
        with open(outputfilename, 'w', encoding='utf-8') as ofile:
            ofile.write(myExtracted)
        print(str(os.stat(outputfilename).st_size) + ' bytes written to ' + str(outputfilename))

# Main:
if __name__==  "__main__":
    print('initializing...')
    mimetypes.init(files=None)
    #to do argument parser for input dir, option xml or json; raise err msgs
    inputDir='tests'
    packlist_crantop100='list_crantop100.txt'
    packlist_geopack='list_geopack.txt'
    for file in os.listdir(inputDir):
        if file.lower().endswith('.r'):
            processfile_R(str(os.path.join(inputDir, file)))
        if file.lower().endswith('.rmd'):
            processfile_Rmd(str(os.path.join(inputDir, file)))
    print('done')