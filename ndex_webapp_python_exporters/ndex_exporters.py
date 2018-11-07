#! /usr/bin/env python

import sys
import argparse
import logging
import ndex_webapp_python_exporters
from ndex_webapp_python_exporters.exporters import GraphMLExporter


logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)-15s %(levelname)s %(relativeCreated)dms " \
             "%(filename)s::%(funcName)s():%(lineno)d %(message)s"


def _parse_arguments(desc, args):
    """Parses command line arguments"""
    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument('exporter', help='Specifies exporter to run',
                        choices=['graphml'])
    parser.add_argument('--verbose', '-v', action='count',
                        help='Increases logging verbosity, max is 4')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + ndex_webapp_python_exporters.__version__))
    return parser.parse_args(args)


def _setuplogging(theargs):
    """Sets up logging"""
    level = (50 - (10 * theargs.verbose))
    logging.basicConfig(format=LOG_FORMAT,
                        stream=sys.stderr,
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
    desc = """Put description here
    """
    theargs = _parse_arguments(desc, args[1:])
    theargs.program = args[0]
    theargs.version = ndex_webapp_python_exporters.__version__

    try:
        _setuplogging(theargs)

        logger.debug(theargs.exporter + ' selected')
        exporter = None
        if 'graphml' in theargs.exporter:
            exporter = GraphMLExporter()

        if exporter is None:
            raise NotImplementedError('Unable to construct Exporter object')
        return exporter.export(sys.stdin, sys.stdout)
    except Exception:
        logger.exception("Error caught exception")
        return 2
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
