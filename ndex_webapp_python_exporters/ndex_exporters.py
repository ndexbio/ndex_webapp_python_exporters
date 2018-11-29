#! /usr/bin/env python

import sys
import argparse
import logging
import ndex_webapp_python_exporters
from ndex_webapp_python_exporters.exporters import GraphMLExporter


logger = logging.getLogger('ndex_exporters')

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"

GRAPHML_MODE = 'graphml'
FILE_FLAG = 'file'
OUT_FLAG = 'out'


def _parse_arguments(desc, args):
    """Parses command line arguments"""
    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument('exporter', help='Specifies exporter to run',
                        choices=[GRAPHML_MODE])
    parser.add_argument('--' + FILE_FLAG, '-f', default=None,
                        help='Read from this file instead of standard in')
    parser.add_argument('--' + OUT_FLAG, '-o', default=None,
                        help='Write to this file instead of standard out')
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increases logging verbosity, max is 4',
                        default=1)
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' +
                                 ndex_webapp_python_exporters.__version__))
    return parser.parse_args(args)


def _setuplogging(theargs):
    """Sets up logging"""
    level = (50 - (10 * theargs.verbose))
    logging.basicConfig(format=LOG_FORMAT,
                        level=level)
    for k in logging.Logger.manager.loggerDict.keys():
        thelog = logging.Logger.manager.loggerDict[k]

        # not sure if this is the cleanest way to do this
        # but the dictionary of Loggers has a PlaceHolder
        # object which tosses an exception if setLevel()
        # is called so I'm checking the class names
        try:
            thelog.setLevel(level)
        except AttributeError:
            pass


def main(args):
    """Main entry point"""
    desc = """
    Version {version}

    This tool is used by NDex website to convert network files in NDEx CX
    format to other formats.

    This tool expects the network files to be piped in via standard in and
    writes output to standard out.

    If export is successful an exit code of 0 is written otherwise a non-zero
    exit code is returned for failure. Errors as well as debug logging
    (see -v flag) are written to standard error.

    The sole required argument defines which exporter is run.

    Currently supported exporters

    graphml
      -- http://graphml.graphdrawing.org/

    For information on NDex CX format see: http://www.ndexbio.org/

    """.format(version=ndex_webapp_python_exporters.__version__)
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = ndex_webapp_python_exporters.__version__
    _setuplogging(theargs)
    try:
        logger.debug(theargs.exporter + ' selected')
        exporter = None
        if GRAPHML_MODE in theargs.exporter:
            exporter = GraphMLExporter()

        if exporter is None:
            raise NotImplementedError('Unable to construct Exporter object')

        input_stream = sys.stdin
        if theargs.file is not None:
            input_stream = theargs.file

        output_stream = sys.stdout
        if theargs.out is not None:
            output_stream = theargs.out

        return exporter.export(input_stream, output_stream)
    except Exception:
        logger.exception("Error caught exception")
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
