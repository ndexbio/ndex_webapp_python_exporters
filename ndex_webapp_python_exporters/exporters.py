# -*- coding:utf-8 -*-

"""Main module."""

import logging
import xml.etree.cElementTree as ET
import json
import numpy as np
import pandas as pd
import ndex2

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
R_KEY = 'r'
D_KEY = 'd'


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
        self._cxnetwork = None

    def _clear_internal_variables(self):
        """Deletes all data in internal variables
        and sets them to None
        """
        del self._cxnetwork
        self._cxnetwork = None

    def _loadcx(self, inputstream):
        logger.info('Loading CX data')
        self._cxnetwork = ndex2.\
            create_nice_cx_from_raw_cx(json.load(inputstream))

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
        if data_type == "float":
            return "double"
        return data_type

    def _translate_edge_key_names(self, val):
        if val is 'i':
            return 'interaction'
        if val is AT_ID_KEY:
            return 'key'
        return val

    def _translate_node_key_names(self, val):
        if val is N_KEY:
            return 'name'
        if val is R_KEY:
            return 'represents'
        return val

    def _get_xml_for_under_node(self, node):
        """
        Creates data xml fragments for node passed in
        :param node: Node to extract data from
        :return: list of ET.Element objects
        """
        el = []
        logger.info('Node:  ' + str(node))
        for nid, val in node.items():
            if nid == '@id':
                continue
            kval = self._translate_node_key_names(nid)
            n = ET.Element('data', attrib={'key': kval})
            n.text = str(val)
            el.append(n)

        if self._cxnetwork.get_node_attributes(node) is None:
            return el

        for nitem in self._cxnetwork.get_node_attributes(node):
            if nitem is None:
                continue
            logger.info('Node attrib: ' + str(nitem))
            nid = nitem[N_KEY]

            if nid == '@id':
                continue
            val = nitem[V_KEY]
            kval = self._translate_node_key_names(nid)
            n = ET.Element('data', attrib={'key': kval})
            n.text = str(val)
            el.append(n)
        return el

    def _generate_xml_for_nodes(self, out):
        """
        Creates and writes to out xml fragments for the nodes
        :param out: Output stream
        :return:
        """
        if self._cxnetwork.get_nodes() is None:
            return
        for node_key, node_val in self._cxnetwork.get_nodes():
            n = ET.Element(GraphMLExporter.NODE,
                           attrib={GraphMLExporter.ID: str(node_key)})
            subel = self._get_xml_for_under_node(node_val)
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
        logger.info('Edge: ' + str(edge))
        for eid, val in edge.items():
            if eid == '@id' or eid == 's' or eid == 't':
                continue
            kval = self._translate_edge_key_names(eid)
            n = ET.Element('data', attrib={'key': kval})
            n.text = str(val)
            el.append(n)

        if self._cxnetwork.get_edge_attributes(edge) is None:
            return el
        for edgeattr in self._cxnetwork.get_edge_attributes(edge):
            if edgeattr is None:
                continue
            logger.info("Edge attr: " + str(edgeattr))
            eattrib = {}
            edge_key = edgeattr[N_KEY]
            if edge_key == "i":
                eattrib[GraphMLExporter.KEY] = 'interaction'
            elif edge_key == "v":
                eattrib[GraphMLExporter.KEY] = 'directed'
            elif edge_key == "s" or edge_key == "t":
                continue
            eattrib[GraphMLExporter.KEY] = str(edge_key)
            e = ET.Element(GraphMLExporter.DATA, attrib=eattrib)
            e.text = str(edgeattr[V_KEY])
            el.append(e)
        return el

    def _generate_xml_for_edges(self, out):
        """
        Creates and writes xml to out stream for edges
        :param out: Output stream
        :return:
        """
        for id, edge in self._cxnetwork.get_edges():
            e = ET.Element(GraphMLExporter.EDGE,
                           attrib={GraphMLExporter.SOURCE: str(edge[S_KEY]),
                                   GraphMLExporter.TARGET: str(edge[T_KEY])})
            subel = self._get_xml_for_under_edge(edge)
            if subel is not None:
                e.extend(subel)
            ET.ElementTree(e).write(out, encoding=UNICODE)
            out.write('\n')

    def _generate_xml_for_data(self, out):
        """
        Reads network attributes and writes out data elements
        :param out:
        :return:
        """
        for netattr in self._cxnetwork.networkAttributes:
            kattrib = {}
            kattrib[GraphMLExporter.KEY] = str(netattr[N_KEY])
            k = ET.Element('data', attrib=kattrib)
            k.text = str(netattr[V_KEY])
            ET.ElementTree(k).write(out, encoding=UNICODE)

    def _generate_xml_for_net_keys(self, out):
        """
        Creates and writes xml for data in the_keys variable to
        out stream
        :param out: Output stream
        :param the_keys: dict of key data to convert to xml
        :return:
        """
        netkeyset = set()

        for netattr in self._cxnetwork.networkAttributes:
            logger.info('NET attr' + str(netattr))
            kattrib = {}
            n_key = str(netattr[N_KEY])
            if n_key in netkeyset:
                continue

            netkeyset.add(n_key)

            kattrib[GraphMLExporter.ATTR_NAME] = n_key
            value = netattr[V_KEY]
            if value is None:
                logger.info('value is none')
            else:
                if D_KEY in netattr.keys():
                    kattrib[GraphMLExporter.ATTR_TYPE] = \
                        self._convert_data_type(netattr[D_KEY])
                else:
                    kattrib[GraphMLExporter.ATTR_TYPE] = \
                        self._convert_data_type(type(value).__name__)
            kattrib['for'] = 'graph'
            kattrib['id'] = n_key

            k = ET.Element('key', attrib=kattrib)
            ET.ElementTree(k).write(out, encoding=UNICODE)

    def _write_name_represents_keys(self, out):
        nodekeyset = set(['name', 'represents'])
        for entry in nodekeyset:
            kattrib = {}
            kattrib['for'] = 'node'
            kattrib['id'] = entry
            kattrib[GraphMLExporter.ATTR_NAME] = entry
            kattrib[GraphMLExporter.ATTR_TYPE] = 'string'
            k = ET.Element('key', attrib=kattrib)
            ET.ElementTree(k).write(out, encoding=UNICODE)
        return nodekeyset

    def _generate_xml_for_node_keys(self, out):
        """
        Creates and writes xml for data in the_keys variable to
        out stream
        :param out: Output stream
        :param the_keys: dict of key data to convert to xml
        :return:
        """

        nodekeyset = self._write_name_represents_keys(out)
        for id, node in self._cxnetwork.get_nodes():
            logger.info('node in keys ' + str(node))
            for nid, val in node.items():
                if nid == '@id' or nid == 'n' or nid == 'r':
                    continue
                if nid in nodekeyset:
                    continue
                nodekeyset.add(nid)
                kattrib = {}
                kattrib[GraphMLExporter.ATTR_NAME] = nid
                if val is None:
                    logger.info('value is none')
                else:
                    kattrib[GraphMLExporter.ATTR_TYPE] = \
                        self._convert_data_type(type(val).__name__)
                kattrib['for'] = 'node'
                kattrib['id'] = nid

                k = ET.Element('key', attrib=kattrib)
                ET.ElementTree(k).write(out, encoding=UNICODE)

            if self._cxnetwork.get_node_attributes(node) is None:
                return
            for nodeattr in self._cxnetwork.get_node_attributes(node):
                if nodeattr is None:
                    continue

                logger.info(str(nodeattr))
                kattrib = {}
                n_key = self._translate_node_key_names(nodeattr[N_KEY])
                if n_key in nodekeyset:
                    continue

                nodekeyset.add(n_key)

                kattrib[GraphMLExporter.ATTR_NAME] = n_key
                value = nodeattr[V_KEY]
                if value is None:
                    logger.info('value is none')
                else:
                    kattrib[GraphMLExporter.ATTR_TYPE] = \
                        self._convert_data_type(type(value).__name__)
                kattrib['for'] = 'node'
                kattrib['id'] = n_key

                k = ET.Element('key', attrib=kattrib)
                ET.ElementTree(k).write(out, encoding=UNICODE)

    def _write_interaction_keys(self, out):
        edgekeyset = set(['interaction', 'key'])
        for entry in edgekeyset:
            kattrib = {}
            kattrib['for'] = GraphMLExporter.EDGE
            kattrib['id'] = entry
            kattrib[GraphMLExporter.ATTR_NAME] = entry
            kattrib[GraphMLExporter.ATTR_TYPE] = 'string'
            k = ET.Element('key', attrib=kattrib)
            ET.ElementTree(k).write(out, encoding=UNICODE)
        return edgekeyset

    def _generate_xml_for_edge_keys(self, out):
        """
        Creates and writes xml for data in the_keys variable to
        out stream
        :param out: Output stream
        :param the_keys: dict of key data to convert to xml
        :return:
        """
        edgekeyset = self._write_interaction_keys(out)
        for id, edge in self._cxnetwork.get_edges():
            if self._cxnetwork.get_edge_attributes(edge) is None:
                continue
            for edgeattr in self._cxnetwork.get_edge_attributes(edge):
                if edgeattr is None:
                    continue
                logger.info(str(edgeattr))
                kattrib = {}
                n_key = self._translate_edge_key_names(edgeattr[N_KEY])
                if n_key in edgekeyset:
                    continue

                edgekeyset.add(n_key)

                kattrib[GraphMLExporter.ATTR_NAME] = n_key
                value = edgeattr[V_KEY]
                if value is None:
                    logger.info('value is none')
                else:
                    if D_KEY in edgeattr.keys():
                        kattrib[GraphMLExporter.ATTR_TYPE] = \
                            self._convert_data_type(edgeattr[D_KEY])
                    else:
                        kattrib[GraphMLExporter.ATTR_TYPE] = \
                            self._convert_data_type(type(value).__name__)
                kattrib['for'] = GraphMLExporter.EDGE
                kattrib['id'] = n_key

                k = ET.Element('key', attrib=kattrib)
                ET.ElementTree(k).write(out, encoding=UNICODE)

    def _generate_xml(self, out):
        """
        Main workflow method that creates the xml document
        by preprocessing input data and writing data as
        xml to out stream
        :param out: Output stream
        :return:
        """
        out.write('<?xml version="1.0" encoding="UTF-8" ' +
                  'standalone="no"?>' + '\n' +
                  '<graphml xmlns="http://graphml.' +
                  'graphdrawing.org/xmlns">\n')

        self._generate_xml_for_net_keys(out)
        self._generate_xml_for_node_keys(out)
        self._generate_xml_for_edge_keys(out)

        # @TODO figure out way to determine what q should be set to
        out.write('\n  <graph edgedefault="directed" id="' +
                  str(self._cxnetwork.get_name()) + '">\n')

        self._generate_xml_for_data(out)
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
        self._loadcx(inputstream)
        logger.info('Writing xml')
        self._generate_xml(outputstream)
        logger.info('Completed writing xml')
        outputstream.flush()
        return 0


class ExcelViaPandasExporter(NDexExporter):
    """Excel exporter written by Cecilia Zhang that leverages
       Pandas framework
    """
    def __init__(self):
        """Constructor"""
        pass

    def get_adjusted_cx(self, inputstream):
        """Takes NDEx CX data from inputstream and adjusts it
           returning an ndex2 CX object
        :returns: NDEx2 CX object
        """
        raw_cx = json.load(inputstream)
        counter = 0
        position_n = 0
        position_e = 0
        position_net = 0
        new_node_attr_list = []
        new_edge_attr_list = []
        context = []
        for section in raw_cx:
            for name_section, info in section.items():
                if name_section == "nodes":
                    for node in info:
                        if node.get("@id"):
                            new_attr_n = {}
                            id = node["@id"]
                            new_attr_n["po"] = id
                            new_attr_n["n"] = "cx node id"
                            new_attr_n["v"] = id
                            new_node_attr_list.append(new_attr_n)
                        if node.get("r"):
                            new_attr_r = {}
                            represents = node.get("r")
                            new_attr_r["po"] = node["@id"]
                            new_attr_r["n"] = "ID"
                            new_attr_r["v"] = represents
                            new_node_attr_list.append(new_attr_r)

                if name_section == "edges":
                    for edge in info:
                        new_attr = {}
                        id = edge["@id"]
                        new_attr["po"] = id
                        new_attr["n"] = "cx edge id"
                        new_attr["v"] = id
                        new_edge_attr_list.append(new_attr)

                if name_section == "@context":
                    temp = {}
                    temp["n"] = "@context"
                    temp["v"] = info[0]
                    context.append(temp)
                if name_section == "nodeAttributes":
                    position_n = counter
                if name_section == "edgeAttributes":
                    position_e = counter
                if name_section == "networkAttributes":
                    position_net = counter
            counter = counter + 1

        n_attr = raw_cx[position_n].get("nodeAttributes")
        if n_attr is not None:
            raw_cx[position_n].get("nodeAttributes").extend(new_node_attr_list)

        e_attr = raw_cx[position_e].get("edgeAttributes")
        if e_attr is not None:
            raw_cx[position_e].get("edgeAttributes").extend(new_edge_attr_list)

        net_attr = raw_cx[position_net].get("networkAttributes")
        if net_attr is not None:
            raw_cx[position_net].get("networkAttributes").extend(context)

        return ndex2.create_nice_cx_from_raw_cx(raw_cx)

    def check_for_vert_bars(self, df):

        poscol = 0
        for name, values in df.iteritems():
            posrow = 0
            for data_points in values:
                if type(data_points) is str:
                    if data_points.find('|') != -1:
                        data_points = data_points.replace('|', " ")
                        df.iloc[posrow, poscol] = data_points
                posrow = posrow + 1
            poscol = poscol + 1

        return df

    def cx_to_pandas(self, nice_cx, outputstream):

        df = nice_cx.to_pandas_dataframe()
        df = df.replace({'source_cx node id': np.nan,
                         'target_cx node id': np.nan}, 0)
        edges_pandas = pd.DataFrame()
        nodes_pandas = pd.DataFrame()
        net_pandas = pd.DataFrame()
        final_nodes_pandas = pd.DataFrame()

        df = self.check_for_vert_bars(df)

        poscol = 0
        for name, values in df.iteritems():
            posrow = 0
            for data_points in values:
                if type(data_points) is str:
                    if data_points.find('"') != -1 and data_points.find(",") != -1:
                        data_points = data_points.replace(',', '|')
                        data_points = data_points.replace('"', "")
                        df.iloc[posrow, poscol] = data_points
                    elif data_points.find('"') != -1:
                        data_points = data_points.replace('"', "")
                        df.iloc[posrow, poscol] = data_points
                posrow = posrow + 1

            if name == "source" or name == "target":
                # edges_pandas[name] = values
                nodes_pandas[name] = values
            elif name == "source_cx node id":
                edges_pandas["source cx node id"] = values
                nodes_pandas[name] = values
            elif name == "target_cx node id":
                edges_pandas["target cx node id"] = values
                nodes_pandas[name] = values
            elif "source" in name or "target" in name:
                nodes_pandas[name] = values
            else:
                edges_pandas[name] = values
            poscol = poscol + 1

        # nodes_pandas = nodes_pandas.replace(np.nan, 0, regex=True)

        nodes_organized_s = {}
        nodes_organized_t = {}
        counter_s = 0
        counter_t = 0
        for source_n in nodes_pandas["source_cx node id"]:
            if source_n not in nodes_organized_s:
                nodes_organized_s[int(source_n)] = counter_s
            counter_s = counter_s + 1
        for target_n in nodes_pandas["target_cx node id"]:
            if nodes_organized_s.get(int(target_n)) == None:
                nodes_organized_t[int(target_n)] = counter_t
            counter_t = counter_t + 1

        source_cols = {}
        target_cols = {}
        counter_columns = 0
        for name, values in nodes_pandas.iteritems():
            if name == "source":
                source_cols["name"] = counter_columns
            elif name == "target":
                target_cols["name"] = counter_columns
            elif "source_" in name:
                source_cols[name.replace("source_", "")] = counter_columns
            elif "target_" in name:
                target_cols[name.replace("target_", "")] = counter_columns
            counter_columns = counter_columns + 1
        # print(source_cols)

        nodes_information = {}
        for columns, col_info in source_cols.items():
            column_info = []
            for node, node_info in nodes_organized_s.items():
                column_info.append(nodes_pandas.iloc[node_info, col_info])
            nodes_information[columns] = column_info
        for columns2, col2_info in target_cols.items():
            column_info2 = []
            for node2, node2_info in nodes_organized_t.items():
                column_info2.append(nodes_pandas.iloc[node2_info, col2_info])
            nodes_information[columns2].extend(column_info2)

        for final_name, final_value in nodes_information.items():
            final_nodes_pandas[final_name] = final_value

            # print(nodes_pandas.iloc[0,0])

        netnames = []
        netvalue = []
        for n_a in nice_cx.networkAttributes:
            dictna = str(n_a)
            netattr = json.loads(dictna)
            netnames.append(netattr.get("n"))
            temp = str(netattr.get("v"))
            if netattr.get("n") == "@context":
                if temp.find("'") != -1:
                    temp = temp.replace("'", "")
                    temp = temp.replace(",", "|")
                    temp = temp.replace("{", "")
                    temp = temp.replace("}", "")
            netvalue.append(temp)
        net_pandas["name"] = netnames
        net_pandas["value"] = netvalue

        self.reorder(final_nodes_pandas, edges_pandas, net_pandas)

    def reorder(self, nodes_pandas, edges_pandas, net_pandas, outputstream):

        if "interaction" in edges_pandas:
            order_edges = ['cx edge id', 'source cx node id', 'interaction', 'target cx node id']
        else:
            order_edges = ['cx edge id', 'source cx node id', 'target cx node id']

        edges_pandas = edges_pandas[order_edges + [c for c in edges_pandas if c not in order_edges]]

        if "cx node id" in nodes_pandas and "ID" in nodes_pandas:
            order_nodes = ["cx node id", "name", "ID"]
        elif "cx node id" in nodes_pandas:
            order_nodes = ["cx node id", "name"]
        elif "ID" in nodes_pandas:
            order_nodes = ["name", "ID"]

        nodes_pandas = nodes_pandas[order_nodes + [c for c in nodes_pandas if c not in order_nodes]]
        self.pandas_to_excel(nodes_pandas, edges_pandas, net_pandas, outputstream)

    def pandas_to_excel(self, nodes_pandas, edges_pandas, net_pandas, outputstream):
        writer = pd.ExcelWriter(outputstream, engine='xlsxwriter')
        nodes_pandas.to_excel(writer, sheet_name='Nodes')
        edges_pandas.to_excel(writer, sheet_name='Edges')
        net_pandas.to_excel(writer, sheet_name='Network Properties')
        writer.save()

    def export(self, inputstream, outputstream):
        """Implementing subclasses should consume the
           CX data coming from inputstream and export
           processed data to outputstream.
        Sub classes should implement this
        :param inputstream: Input stream containing CX data
        :param outputstream: Output stream to write results to
        :returns int: 0 upon success otherwise 1 or higher for failure
        """
        nice_cx = self.get_adjusted_cx(inputstream)
        self.cx_to_pandas(nice_cx, outputstream)
