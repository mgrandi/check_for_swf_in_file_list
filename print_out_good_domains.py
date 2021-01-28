
import argparse
import json
import logging

logging.basicConfig(level="INFO")

logger = logging.getLogger("app")

parser = argparse.ArgumentParser()
parser.add_argument("input", help="results file as generated by check_for_swf_in_file_list")
parser.add_argument("good_domain_output", help="results file to write the good domains")
parser.add_argument("bad_domain_output", help="results file to write the bad domains")
parser.add_argument("--verbose", action="store_true", help="increase logging verbosity")

args = parser.parse_args()

if args.verbose:
    logger.setLevel("DEBUG")

if __name__ == "__main__":

    good_domains_list = []
    bad_domains_list = []

    with open(args.input, "r", encoding="utf-8") as f:
        input_dict = json.load(f)


        for iter_result in input_dict["results"]:
            domain = iter_result["domain"]

            logger.debug("domain is `%s`", domain)

            running_boolean = None

            for iter_test_result in iter_result["test_results"]:

                if running_boolean is None:
                    running_boolean =  iter_test_result["is_swf"]
                    logger.debug("first run, running_boolean is `%s`", running_boolean)

                else:
                    running_boolean = running_boolean or iter_test_result["is_swf"]
                    logger.debug("running boolean is `%s` after doing an `or` with `%s`", running_boolean, iter_test_result["is_swf"])

            if running_boolean:

                logger.debug("domain `%s` is going in the good domain list", domain)

                good_domains_list.append(domain)
            else:
                logger.debug("domain `%s` is going in the bad domain list", domain)

                bad_domains_list.append(domain)



        with open(args.good_domain_output, "w", encoding="utf-8") as f:

            for iter_domain in good_domains_list:
                f.write(f"{iter_domain}\n")

        with open(args.bad_domain_output, "w", encoding="utf-8") as f:

            for iter_domain in bad_domains_list:
                f.write(f"{iter_domain}\n")

        logger.info("done")