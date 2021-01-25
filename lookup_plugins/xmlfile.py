# SPDX-FileCopyrightText: 2021 Robin Schneider <ypid@riseup.net>
#
# SPDX-License-Identifier: Apache-2.0
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = """
    lookup: file
    author: Robin Schneider <ypid@riseup.net>
    short_description: read XML file contents
    description:
        - This lookup returns the contents from a XML file on the Ansible controller's file system.
    options:
      _terms:
        description: path(s) of XML files to read
        required: True
      xpath:
        description: The XPath to filter the XML file with.
        type: str
        required: False
"""

EXAMPLES = """
- name: Extract hostname from XML file
  debug:
    msg: 'OPNsense hostname: {{ lookup("xmlfile", "path/to/file.xml", xpath="//system/hostname/text()") }}'
"""

RETURN = """
  _raw:
    description:
      - content of XPath matches. Either as XML or as text depending on what the XPath matched.
"""

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_text
from ansible.utils.display import Display

#  from lxml import etree
import defusedxml.lxml as etree

display = Display()


class LookupModule(LookupBase):
    def _get_xml_matches(self, xml_file, xpath):
        with open(xml_file, 'r') as fh:
            tree = etree.parse(fh)

        xml_string_list = []
        for match in tree.xpath(xpath):
            if isinstance(match, str):
                # XPath example: //text()
                xml_string = match
            else:
                # XPath example: //
                xml_string = etree.tostring(match).decode('utf-8')
            xml_string_list.append(xml_string.strip())

        return xml_string_list

    def run(self, terms, variables=None, **kwargs):

        ret = []

        for term in terms:
            display.debug("File lookup term: %s" % term)

            # Find the file in the expected search path.
            lookupfile = self.find_file_in_search_path(variables, 'files', term)
            display.vvvv(u"File lookup using %s as file" % lookupfile)
            try:
                if lookupfile:
                    xml_string = '\n'.join(self._get_xml_matches(lookupfile, kwargs.get('xpath')))
                    display.vvvv(u"Content %s" % xml_string)
                    ret.append(xml_string)
                else:
                    raise AnsibleParserError()
            except AnsibleParserError:
                raise AnsibleError("could not locate file in lookup: %s" % term)

        return ret


if __name__ == '__main__':
    import sys
    xmlfile_lookup = LookupModule()
    print('\n'.join(xmlfile_lookup._get_xml_matches(sys.argv[1], xpath=sys.argv[2])))
