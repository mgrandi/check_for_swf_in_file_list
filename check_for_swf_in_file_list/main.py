import argparse
import logging
import pathlib
import logging
import sys

import logging_tree

from check_for_swf_in_file_list import app
from check_for_swf_in_file_list import utils


def main():
    # if we are being run as a real program

    parser = argparse.ArgumentParser(
        description="check a file list to see if they are actually swf files or just fake pages",
        epilog="Copyright 2021-01-24 - Mark Grandi",
        fromfile_prefix_chars="@")



    # optional arguments, if specified these are the input and output files, if not specified, it uses stdin and stdout
    parser.add_argument("--file-list",
        dest="file_list",
        type=utils.isFileType(True),
        required=True,
        help="the url file list")
    parser.add_argument("--number-of-tests-per-domain",
        dest="number_of_tests_per_domain",
        type=int,
        required=False,
        default=5,
        help="the number of tests we do per domain to see if the url actually leads to a SWF or not")
    parser.add_argument("--results-file",
        dest="results_file",
        type=utils.isFileType(False),
        required=True,
        help="where to save the results as a jsonl file")
    parser.add_argument("--log-to-file",
        dest="log_to_file",
        type=utils.isFileType(False),
        help="save the application log to a file as well as print to stdout")
    parser.add_argument("--verbose", action="store_true", help="Increase logging verbosity")



    try:
        root_logger = logging.getLogger()

        parsed_args = parser.parse_args()


        # set up logging stuff
        logging.captureWarnings(True) # capture warnings with the logging infrastructure
        logging_formatter = utils.ArrowLoggingFormatter("%(asctime)s %(threadName)-10s %(name)-40s %(levelname)-8s: %(message)s")
        logging_handler = logging.StreamHandler(sys.stdout)
        logging_handler.setFormatter(logging_formatter)
        root_logger.addHandler(logging_handler)


        # silence urllib3 (requests) logger because its noisy
        # requests_packages_urllib_logger = logging.getLogger("requests.packages.urllib3")
        # requests_packages_urllib_logger.setLevel("INFO")
        # urllib_logger = logging.getLogger("urllib3")
        # urllib_logger.setLevel("INFO")

        # set logging level based on arguments
        if parsed_args.verbose:
            root_logger.setLevel("DEBUG")
        else:
            root_logger.setLevel("INFO")

        if parsed_args.log_to_file:
            file_handler = logging.FileHandler(parsed_args.log_to_file, mode='a', encoding="utf-8")
            file_handler.setFormatter(logging_formatter)
            root_logger.addHandler(file_handler)

        root_logger.debug("argv: `%s`", sys.argv)
        root_logger.debug("Parsed arguments: %s", parsed_args)
        root_logger.debug("Logger hierarchy:\n%s", logging_tree.format.build_description(node=None))

        # run the application
        appref = app.Application(parsed_args)
        appref.run()

        root_logger.info("Done!")

    except Exception as e:
        root_logger.exception("Something went wrong!")
        sys.exit(1)



