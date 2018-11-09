# -*- coding:utf-8 -*-

"""Main module."""

import logging
import json
from json.decoder import JSONDecodeError
import xml.etree.cElementTree as ET


logger = logging.getLogger(__name__)

# xml encoding for ElementTree
UNICODE = 'unicode'

# CX format keys
AT_ID_KEY = '@id'
PO_KEY = 'po'
V_KEY = 'v'
N_KEY = 'n'
S_KEY = 's'
T_KEY = 't'


class NDexExporter(object):
    """Base class from which other exporters should be
       derived
    """
    def __init__(self):
        """Constructor"""
        pass

    def export(self, inputstream, outputstream):
        """Implementing subclasses should consume the
           CX data coming from inputstream and export
           processed data to outputstream.
        Sub classes should implement this
        :param inputstream: Input stream containing CX data
        :param outputstream: Output stream to write results to
        :returns int: 0 upon success otherwise 1 or higher for failure
        """
        raise NotImplementedError('Should be implemented by subclass')


class GraphMLExporter(NDexExporter):
    """Exports CX networks in GraphML XML format
       http://graphml.graphdrawing.org/
       WARNING: This implementation follows design of
                Cytoscape which allows duplicate key ids
    """
    NODE = 'node'
    EDGE = 'edge'
    SOURCE = 'source'
    TARGET = 'target'
    DATA = 'data'
    KEY = 'key'
    ID = 'id'
    ATTR_NAME = 'attr.name'
    ATTR_TYPE = 'attr.type'

    def __init__(self):
        """Constructor"""
        super(NDexExporter, self).__init__()
        self._nodes = None
        self._edges = None
        self._node_attr = None
        self._edge_attr = None
        self._net_attr = None
        self._network_name = None
        self._keys_net = None
        self._keys_node = None
        self._keys_edge = None

    def _clear_internal_variables(self):
        """Deletes all data in internal variables
        and sets them to None
        """
        del self._nodes
        del self._edges
        del self._node_attr
        del self._edge_attr
        del self._net_attr
        del self._network_name
        del self._keys_net
        del self._keys_node
        del self._keys_edge

        self._nodes = None
        self._edges = None
        self._node_attr = None
        self._edge_attr = None
        self._net_attr = None
        self._network_name = None
        self._keys_net = None
        self._keys_node = None
        self._keys_edge = None

    def _split_json(self, json_data):
        """
        Splits json_data into separate Aspects.
        This is a nieve implementation assuming each
        Aspect only appears once.
        :param json_data: CX data loaded by json
        :return:
        """
        if json_data is None:
            logger.error('No json data to split by Aspect')
            return

        for data in json_data:
            for key, value in data.items():
                if key == "nodes":
                    if self._nodes is None:
                        self._nodes = value
                    else:
                        self._nodes.extend(value)

                if key == "edges":
                    if self._edges is None:
                        self._edges = value
                    else:
                        self._edges.extend(value)

                if key == "nodeAttributes":
                    if self._node_attr is None:
                        self._node_attr = value
                    else:
                        self._node_attr.extend(value)

                if key == "edgeAttributes":
                    if self._edge_attr is None:
                        self._edge_attr = value
                    else:
                        self._edge_attr.extend(value)

                if key == "networkAttributes":
                    if self._net_attr is None:
                        self._net_attr = value
                    else:
                        self._net_attr.extend(value)

    def _build_node_attribute_dict(self):
        """
        Puts internal node attributes list into a dictionary
        :return: dict():
        """
        logger.info('Putting ' + str(len(self._node_attr)) +
                    ' node attributes into dictionary')
        attrdict = dict()
        for attr in self._node_attr:
            attrdict[attr.get(PO_KEY)] = attr
        del self._node_attr
        self._node_attr = None
        return attrdict

    def _add_node_attributes_to_nodes(self):
        """Adds node attributes to nodes
        """
        if self._node_attr is None:
            logger.debug('No node attributes found')
            return
        logger.info('Adding node attributes to ' + str(len(self._node_attr)) +
                    ' nodes.')
        attrdict = self._build_node_attribute_dict()
        for node in self._nodes:
            node_id = node.get(AT_ID_KEY)
            attr = attrdict.get(node_id)
            if attr is None:
                continue
            node[attr.get(N_KEY)] = attr.get(V_KEY)

    def _build_edge_attribute_dict(self):
        """Puts internal edge attributes list into a dictionary
           setting key to value of PO_KEY. After completion
           edge attributes list is deleted.
           :returns dict():
        """
        logger.info('Putting ' + str(len(self._edge_attr)) +
                    ' edge attributes into dictionary ')
        attrdict = dict()
        for attr in self._edge_attr:
            attrdict[attr.get(PO_KEY)] = attr
        del self._edge_attr
        self._edge_attr = None
        return attrdict

    def _add_edge_attributes_to_edges(self):
        """Adds edge attributes to edges by first building a
           dictionary of edge attributes then iterating across
           the edges
        """
        if self._edge_attr is None:
            logger.debug('No edge attributes found')
            return

        attrdict = self._build_edge_attribute_dict()
        del self._edge_attr
        logger.info('Adding edge attributes to ' + str(len(self._edges)) +
                    ' edges.')
        for edge in self._edges:
            edge_id = edge.get(AT_ID_KEY)
            attr = attrdict.get(edge_id)
            if attr is None:
                continue
            edge[attr.get(N_KEY)] = attr.get(V_KEY)

    def _extract_network_name(self):
        """Iterates through networkAttributes list for name of network
           setting the value to internal variable
        """
        if self._net_attr is None:
            logger.debug('No network attributes found. ' +
                         'Using unknown for network name')
            self._network_name = 'unknown'
            return
        logger.info('Searching ' + str(len(self._net_attr)) +
                    ' network attributes for network name')
        for netattr in self._net_attr:
            if netattr.get(N_KEY) == "name":
                self._network_name = str(netattr.get(V_KEY))
                break

    def _convert_data_type(self, data_type):
        """Converts Python data types (int, str, bool) to types
        acceptable by graphml
        """
        if data_type == "int":
            return "integer"
        if data_type == "str":
            return "string"
        if data_type == "bool":
            return "boolean"
        return data_type

    def _generate_xml_for_network_keys(self, out):
        """Creates and writes to out stream an xml fragment
           for keys
        """
        if self._net_attr is None:
            logger.debug('No network attributes found. ' +
                         'Skipping generation of data tags for graph')
            return
        for netattr in self._net_attr:
            if netattr.get(N_KEY) != "name":
                d = ET.Element(GraphMLExporter.DATA,
                               attrib={GraphMLExporter.KEY: str(netattr.get(N_KEY))})
                d.text = str(netattr[V_KEY])
                ET.ElementTree(d).write(out, encoding=UNICODE)
                out.write('\n')

    def _extract_network_keys(self):
        """
        Extracts network keys data from network attributes
        :return:
        """
        if self._net_attr is None:
            logger.debug('No network attributes found. Skipping ' +
                         'extraction of network keys')
            return
        self._keys_net = {}
        for netattr in self._net_attr:
            if self._keys_net.get(netattr[N_KEY]) is None:
                temp = {}
                temp[GraphMLExporter.ATTR_NAME] = netattr[N_KEY]
                temp[GraphMLExporter.ATTR_TYPE] = self._convert_data_type(type(netattr[V_KEY]).__name__)
                temp["for"] = "graph"
                temp["id"] = netattr[N_KEY]
                self._keys_net[netattr[N_KEY]] = temp

    def _extract_node_keys(self):
        """Extract node keys from nodes
        """
        self._keys_node = {}
        for node in self._nodes:
            for node_key, node_value in node.items():
                if node_key == '@id':
                    continue
                if self._keys_node.get(node_key) is not None:
                    continue
                temp = {}
                if node_key == "n":
                    temp[GraphMLExporter.ATTR_NAME] = 'name'
                    temp["id"] = 'name'
                elif node_key == "r":
                    temp[GraphMLExporter.ATTR_NAME] = 'represents'
                    temp["id"] = 'represents'
                else:
                    temp[GraphMLExporter.ATTR_NAME] = node_key
                    temp["id"] = node_key
                temp["attr.type"] = self._convert_data_type(type(node_value).__name__)
                temp["for"] = "node"
                self._keys_node[node_key] = temp

    def _extract_edge_keys(self):
        """Extract edge keys from edges
        """
        self._keys_edge = {}
        for edge in self._edges:
            for edge_key, edge_value in edge.items():
                if edge_key == 's' or edge_key == 't':
                    continue
                if self._keys_edge.get(edge_key) is not None:
                    continue
                temp = {}
                if edge_key == "@id":
                    temp[GraphMLExporter.ATTR_NAME] = 'key'
                    temp["id"] = 'key'
                elif edge_key == "i":
                    temp[GraphMLExporter.ATTR_NAME] = "interaction"
                    temp["id"] = 'interaction'
                else:
                    temp[GraphMLExporter.ATTR_NAME] = edge_key
                    temp["id"] = edge_key
                temp[GraphMLExporter.ATTR_TYPE] = self._convert_data_type(type(edge_value).__name__)
                temp["for"] = "edge"
                self._keys_edge[edge_key] = temp

    def _get_xml_for_under_node(self, node):
        """
        Creates data xml fragments for node passed in
        :param node: Node to extract data from
        :return: list of ET.Element objects
        """

        el = []
        for node_key, node_value in node.items():
            if node_key == '@id':
                continue
            if node_key == "n":
                kval = 'name'
            elif node_key == "r":
                kval = 'represents'
            else:
                kval = node_key

            n = ET.Element('data', attrib={'key': kval})
            n.text = node_value
            el.append(n)
        return el

    def _generate_xml_for_nodes(self, out):
        """
        Creates and writes to out xml fragments for the nodes
        :param out: Output stream
        :return:
        """

        for node in self._nodes:
            n = ET.Element(GraphMLExporter.NODE,
                           attrib={GraphMLExporter.ID: str(node[AT_ID_KEY])})
            subel = self._get_xml_for_under_node(node)
            if subel is not None:
                n.extend(subel)
            ET.ElementTree(n).write(out, encoding=UNICODE)
            out.write('\n')

    def _get_xml_for_under_edge(self, edge):
        """
        Generates xml of data values for edge passed in.
        :param edge: Edge to extract data values for
        :return: list of ET.Element objects
        """
        el = []
        for edge_key, edge_value in edge.items():
            eattrib = {}
            if edge_key == "i":
                eattrib[GraphMLExporter.KEY] = 'interaction'
            elif edge_key == "@id":
                eattrib[GraphMLExporter.KEY] = 'key'
            elif edge_key != "s" and edge_key != "t":
                eattrib[GraphMLExporter.KEY] = edge_key
            else:
                continue
            e = ET.Element(GraphMLExporter.DATA, attrib=eattrib)
            e.text = str(edge_value)
            el.append(e)
        return el

    def _generate_xml_for_edges(self, out):
        """
        Creates and writes xml to out stream for edges
        :param out: Output stream
        :return:
        """
        for edge in self._edges:
            e = ET.Element(GraphMLExporter.EDGE,
                           attrib={GraphMLExporter.SOURCE: str(edge[S_KEY]),
                                   GraphMLExporter.TARGET: str(edge[T_KEY])})
            subel = self._get_xml_for_under_edge(edge)
            if subel is not None:
                e.extend(subel)
            ET.ElementTree(e).write(out, encoding=UNICODE)
            out.write('\n')

    def _generate_xml_for_keys(self, out, the_keys):
        """
        Creates and writes xml for data in the_keys variable to
        out stream
        :param out: Output stream
        :param the_keys: dict of key data to convert to xml
        :return:
        """
        for attr, attr_val in the_keys.items():
            kattrib = {}
            for key, value in attr_val.items():
                kattrib[key] = value
            k = ET.Element('key', attrib=kattrib)
            ET.ElementTree(k).write(out, encoding=UNICODE)
            out.write('\n')

    def _generate_xml(self, out):
        """
        Main workflow method that creates the xml document
        by preprocessing input data and writing data as
        xml to out stream
        :param out: Output stream
        :return:
        """
        self._add_node_attributes_to_nodes()
        self._add_edge_attributes_to_edges()
        self._extract_network_name()
        self._extract_network_keys()
        self._extract_node_keys()
        self._extract_edge_keys()

        out.write('<?xml version="1.0" encoding="UTF-8" ' +
                  'standalone="no"?>' + '\n' +
                  '<graphml xmlns="http://graphml.' +
                  'graphdrawing.org/xmlns">\n')
        logger.info('Split json data by aspect')
        self._generate_xml_for_keys(out, self._keys_net)
        self._generate_xml_for_keys(out, self._keys_node)
        self._generate_xml_for_keys(out, self._keys_edge)

        # @TODO figure out way to determine what edgedefault should be set to
        out.write('  <graph edgedefault="directed" id="' +
                  str(self._network_name) + '">\n')

        self._generate_xml_for_network_keys(out)
        self._generate_xml_for_nodes(out)
        self._generate_xml_for_edges(out)
        out.write('\n</graph>\n</graphml>\n')

    def export(self, inputstream, outputstream):
        """
        Converts CX network to GraphML xml format in
           a non efficient approach where entire inputstream
           is loaded as a json document and then parsed
        :param inputstream: InputStream to read CX data from
        :param outputstream: OutputStream to write graphml xml data to
        :raises JSONDecodeError: if there is an error parsing data
        :raises AttributeError: Possibly raise if no data is offered by
                                inputstream
        :return: 0 upon success otherwise failure
        """
        """Converts CX network to GraphML xml format in
           a non efficient approach where entire inputstream
           is loaded as a json document and then parsed
        """
        self._clear_internal_variables()
        logger.info('Reading inputstream')
        json_data = json.load(inputstream)
        self._split_json(json_data)
        logger.info('Writing xml')
        self._generate_xml(outputstream)
        logger.info('Completed writing xml')
        outputstream.flush()
        return 0
