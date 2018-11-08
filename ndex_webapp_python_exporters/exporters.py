# -*- coding:utf-8 -*-

"""Main module."""

import logging
import json
import xml.etree.cElementTree as ET


logger = logging.getLogger(__name__)

UNICODE = 'unicode'
AT_ID_KEY='@id'
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
        raise NotImplementedError('Should be implemented by subclasses')


class GraphMLExporter(NDexExporter):
    """Exports CX networks in GraphML XML format
       http://graphml.graphdrawing.org/
    """
    NODE = 'node'
    EDGE = 'edge'
    SOURCE = 'source'
    TARGET = 'target'
    DATA = 'data'
    KEY = 'key'
    ID = 'id'

    def __init__(self):
        """Constructor"""
        super(NDexExporter, self).__init__()
        self._key_id = 0
        self._nodes = None
        self._edges = None
        self._node_attr = None
        self._edge_attr = None
        self._net_attr = None
        self._xml = None
        self._network_name = None
        self._keys_net = None
        self._keys_node = None
        self._keys_edge = None

    def _reset_key_id(self):
        self._key_id = 0

    def _get_next_key_id(self):
        self._key_id += 1
        return 'k' + str(self._key_id - 1)

    def _split_json(self, json_data):
        for data in json_data:
            for key, value in data.items():
                if key == "nodes":
                    self._nodes = value
                if key == "edges":
                    self._edges = value
                if key == "nodeAttributes":
                    self._node_attr = value
                if key == "edgeAttributes":
                    self._edge_attr = value
                if key == "networkAttributes":
                    self._net_attr = value

    def _add_node_attributes_to_nodes(self):
        if self._node_attr is None:
            return
        for attr in self._node_attr:
            for node in self._nodes:
                if node.get(AT_ID_KEY) == attr.get(PO_KEY):
                    node[attr.get(N_KEY)] = attr.get(V_KEY)
        del self._node_attr
        self._node_attr = None

    def _add_edge_attributes_to_edges(self):
        if self._edge_attr is None:
            return
        for attr in self._edge_attr:
            for edge in self._edges:
                if edge.get(AT_ID_KEY) == attr.get(PO_KEY):
                    edge[attr.get(N_KEY)] = attr.get(V_KEY)
        del self._edge_attr
        self._edge_attr = None

    def _extract_network_name(self):
        """Iterates through networkAttributes list for name of network
           setting the value to internal variable
        """
        if self._net_attr is None:
            return
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
        if self._net_attr is None:
            return
        self._keys_net = {}
        for netattr in self._net_attr:
            if netattr.get(N_KEY) != "name":
                d = ET.Element(GraphMLExporter.DATA,
                               attrib={GraphMLExporter.KEY: str(netattr.get(N_KEY))})
                d.text = str(netattr[V_KEY])
                ET.ElementTree(d).write(out, encoding=UNICODE)

            if self._keys_net.get(netattr[N_KEY]) is None:
                temp = {}
                temp["attr.name"] = netattr[N_KEY]
                temp["attr.type"] = self._convert_data_type(type(netattr[V_KEY]).__name__)
                temp["for"] = "graph"
                temp["id"] = netattr[N_KEY]
                self._keys_net[netattr[N_KEY]] = temp

    def _get_xml_for_under_node(self, node):
        el = []
        for node_key, node_value in node.items():
            if node_key == "n":
                kval = 'name'
            elif node_key == "r":
                kval = 'represents'
            elif node_key != "@id":
                n = ET.Element('data', attrib={'key': kval})
                n.text = node_value
                el.append(n)

            if self._keys_node.get(node_key) is None:
                if node_key != "@id":
                    temp = {}
                    if node_key == "n":
                        temp["attr.name"] = "name"
                        temp["id"] = self._get_next_key_id()
                    elif node_key == "r":
                        temp["attr.name"] = "represents"
                        temp["id"] = self._get_next_key_id()
                    else:
                        temp["attr.name"] = node_key
                        temp["id"] = self._get_next_key_id()
                        temp["attr.type"] = type(node_value).__name__
                        temp["for"] = "node"
                        self._keys_node[node_key] = temp
        import sys
        sys.stderr.write(str(len(el)))
        return el

    def _generate_xml_for_nodes(self, out):
        self._keys_node = {}
        for node in self._nodes:
            n = ET.Element(GraphMLExporter.NODE,
                           attrib={GraphMLExporter.ID: str(node[AT_ID_KEY])})
            subel = self._get_xml_for_under_node(node)
            if subel is not None:
                n.extend(subel)
            ET.ElementTree(n).write(out, encoding=UNICODE)

    def _generate_xml_for_edges(self, out):
        for edge in self._edges:
            e = ET.Element(GraphMLExporter.EDGE,
                           attrib={GraphMLExporter.SOURCE: str(edge[S_KEY]),
                                   GraphMLExporter.TARGET: str(edge[T_KEY])})
            ET.ElementTree(e).write(out, encoding=UNICODE)

    def _generate_xml_for_keys(self, out, the_keys):
        for attr, attr_val in the_keys.items():
            kattrib = {}
            for key, value in attr_val.items():
                kattrib[key] = value
            k = ET.Element('key', attrib=kattrib)
            ET.ElementTree(k).write(out, encoding=UNICODE)

    def _generate_xml(self, out):
        self._extract_network_name()
        out.write('  <graph edgedefault="directed" id="' +
                  str(self._network_name) + '">\n')
        self._generate_xml_for_network_keys(out)
        self._generate_xml_for_keys(out, self._keys_net)
        self._generate_xml_for_nodes(out)
        self._generate_xml_for_edges(out)
        out.write('\n</graph>\n</graphml>\n')

    def _create_xml(self, new_json):

        keys_nodes = {}
        keys_edges = {}
        keys_net = {}
        graphml = ""
        for node in new_json["nodes"]:
            node_data = ""
            for node_key, node_value in node.items():
                if node_key == "n":
                    node_data = (node_data + '  <data key = "name">' +
                                 str(node_value) + "</data>" + '\n')
                elif node_key == "r":
                    node_data = (node_data + '  <data key = "represents">' +
                                 str(node_value) + "</data>" + '\n')
                elif node_key != "@id":
                    node_data = (node_data + '  <data key = "' +
                                 str(node_key) + '">' +
                                 str(node_value) +
                                 "</data>" + '\n')

                if keys_nodes.get(node_key) == None:
                    if node_key != "@id":
                        temp = {}
                        if node_key == "n":
                            temp["attr.name"] = "name"
                            temp["id"] = self._get_next_key_id()
                        elif node_key == "r":
                            temp["attr.name"] = "represents"
                            temp["id"] = self._get_next_key_id()
                        else:
                            temp["attr.name"] = node_key
                            temp["id"] = self._get_next_key_id()
                        temp["attr.type"] = type(node_value).__name__
                        temp["for"] = "node"
                        keys_nodes[node_key] = temp

            #node_data was in there
            node_data = ('<node id = "' + str(node["@id"]) + '">' +
                         '\n' + str('') + "</node>" + '\n')
            graphml = graphml + node_data
        for edge in new_json["edges"]:
            edge_data = ""
            for edge_key, edge_value in edge.items():
                logger.debug(str(type(edge_key)) + ' and ' +
                             str(type(edge_value)))
                if edge_key == "i":
                    edge_data = (edge_data + '  <data key = "interaction">' +
                                 str(edge_value) + "</data>" + '\n')
                elif edge_key == "@id":
                    edge_data = (edge_data + '  <data key = "key">' +
                                 str(edge_value) + "</data>" + '\n')
                elif edge_key != "s" and edge_key != "t":
                        edge_data = (edge_data + '  <data key = "' +
                                     str(edge_key) + '">' +
                                     str(edge_value) +
                                     "</data>" + '\n')

                if keys_edges.get(edge_key) == None:
                    if edge_key != "s" and edge_key != "t":
                        temp = {}
                        if edge_key == "@id":
                            temp["attr.name"] = "key"
                            temp["id"] = self._get_next_key_id()
                        elif edge_key == "i":
                            temp["attr.name"] = "interaction"
                            temp["id"] = self._get_next_key_id()
                        else:
                            temp["attr.name"] = edge_key
                            temp["id"] = self._get_next_key_id()
                        temp["attr.type"] = type(edge_value).__name__
                        temp["for"] = "edge"
                        keys_edges[edge_key] = temp
            # edge_data was in ''
            edge_data = '<edge source = "' + str(edge["s"]) + '" target = "' + str(edge["t"]) + '" >' + "\n" + str(
                '') + "</edge>" + '\n'
            graphml = graphml + edge_data

        # print(keys_edges)

        net_name = "Untitled"
        """
        if new_json.get("networkAttributes") is not None:
            for netattr in new_json["networkAttributes"]:
                if netattr.get("n") != "name":
                    graphml = ('<data key = "' + str(netattr["n"]) + '">' +
                               str(netattr["v"]) + "</data>" +
                               '\n' + graphml)
                elif netattr.get("n") == "name":
                    net_name = str(netattr.get("v"))

                if keys_net.get(netattr["n"]) == None:
                    temp = {}
                    temp["attr.name"] = netattr["n"]
                    temp["attr.type"] = type(netattr["v"]).__name__
                    temp["for"] = "graph"
                    temp["id"] = self._get_next_key_id()
                    keys_net[netattr["n"]] = temp
        """
        graphml = '<graph edgedefault="directed" id="' + net_name + '">' + '\n' + graphml + '</graph>'
        # print(graphml)
        # keys_nodes = self._change_to_proper_data_type(keys_nodes)
        # keys_edges = self._change_to_proper_data_type(keys_edges)
        # keys_net = self._change_to_proper_data_type(keys_net)
        # graphml = self._create_list_xml_keys(keys_net) + graphml
        # graphml = self._create_list_xml_keys(keys_edges) + graphml
        # graphml = self._create_list_xml_keys(keys_nodes) + graphml
        return graphml

    def _change_to_proper_data_type(self, keys_list):
        for key, value in keys_list.items():
            if value["attr.type"] == "int":
                value["attr.type"] = "integer"
            elif value["attr.type"] == "str":
                value["attr.type"] = "string"
            elif value["attr.type"] == "bool":
                value["attr.type"] = "boolean"
        return keys_list

    def _create_list_xml_keys(self, keys_list):
        final_key_xml = ""
        for attr, attr_val in keys_list.items():
            key_xml = "  <key"
            for key, value in attr_val.items():
                key_xml = key_xml + ' ' + key + ' = "' + value + '"'
            key_xml = key_xml + "/>\n"
            final_key_xml = final_key_xml + key_xml
        print(final_key_xml)
        return final_key_xml

    def export(self, inputstream, outputstream):
        """Converts CX network to GraphML xml format in
           a non efficient approach where entire inputstream
           is loaded as a json document and then parsed
        """
        self._reset_key_id()
        outputstream.write('<?xml version="1.0" encoding="UTF-8" ' +
                           'standalone="no"?>' + '\n' +
                           '<graphml xmlns="http://graphml.' +
                           'graphdrawing.org/xmlns">\n')
        logger.debug('Reading inputstream')
        json_data = json.load(inputstream)
        logger.debug('Completed reading inputstream')
        logger.debug('Processing CX data')
        self._split_json(json_data)
        logger.debug('Completed processing CX data')
        self._generate_xml(outputstream)
        outputstream.flush()
        return 0





