import logging
import pathlib
import urllib.parse
import random
import json

import requests
import attr

from check_for_swf_in_file_list import model
from check_for_swf_in_file_list import constants
from check_for_swf_in_file_list import utils


logger = logging.getLogger(__name__)


class Application():

    def __init__(self, parsed_args):
        self.args = parsed_args
        # key is domain netloc , value is a list
        self.domain_dict = {}
        self.all_results = model.AllResults(results=[])


    def run(self):


        logger.info("loading file list")

        total_url_count = 0
        domain_count = 0
        num_global_matches = 0
        num_globl_failures = 0
        with open(self.args.file_list, "r", encoding="utf-8") as f:

            while True:
                iter_line = None
                try:

                    iter_line = f.readline().strip()
                    if not iter_line:
                        break

                    final_url = iter_line
                    was_fixed = False
                    # some urls have slashes in front which isn't valid, put http infront
                    if iter_line.startswith("//"):
                        final_url = f"http:{iter_line}"
                        was_fixed = True

                    url_parts = urllib.parse.urlparse(iter_line)
                    domain = url_parts.netloc

                    url_list_entry = model.UrlListEntry(full_url=final_url, was_fixed=was_fixed)

                    # if we don't have this domain yet, add it to our dictionary and create a list value
                    if domain not in self.domain_dict.keys():

                        self.domain_dict[domain] = []
                        domain_count += 1

                    # add the url entry to the list in the dictionary
                    self.domain_dict[domain].append(url_list_entry)

                    total_url_count += 1
                except Exception as e:
                    logger.error("unhandled exception on line `%s`: `%s`, skipping", iter_line, e)
                    continue

        logging.info("file list loaded successfully with `%s` entries and `%s` domains",
            total_url_count, domain_count)


        # now go through each of the domains, pick out the configured amount of them, and then test them

        for idx, iter_domain in enumerate(self.domain_dict.keys(), start=1):
            logger.info("[%s/%s] - on domain `%s`", idx, domain_count, iter_domain)

            url_entry_list = self.domain_dict[iter_domain]

            number_of_samples = self.args.number_of_tests_per_domain

            # random.sample will throw an exception if k > population, so lower the k value if we don't have
            # enough domains
            number_of_domain_entries = len(url_entry_list)
            if number_of_domain_entries < number_of_samples:
                logger.info("only have `%s` domain entries, lowering the `k` value to match", number_of_domain_entries)
                number_of_samples = number_of_domain_entries

            url_sample_list = random.sample(url_entry_list, number_of_samples)

            iter_domain_results_list = []
            num_matches = 0
            num_failures = 0
            for iter_url_entry in url_sample_list:

                # see:
                # https://requests.readthedocs.io/en/latest/user/advanced/#body-content-workflow
                # and
                # https://requests.readthedocs.io/en/latest/api/#requests.Response.iter_content
                logger.debug("making request to `%s`", iter_url_entry.full_url)
                headers = {"User-Agent": constants.USER_AGENT}

                try:
                    with requests.get(iter_url_entry.full_url, stream=True, headers=headers, timeout=(5,30)) as r:

                        data = bytearray()
                        for iter_bytes in r.iter_content(chunk_size=constants.REQUESTS_ITER_CONTENT_CHUNK_SIZE):

                            # bytearray.append() only takes a integer, not a bytes or another bytearray object, why???
                            # use the `+=` operator
                            data += iter_bytes

                            # only want 1 chunk
                            break

                        logger.debug("data recieved: `%s`", data)

                        individual_test_result = None
                        if data not in constants.ACCEPTABLE_SWF_MAGIC_NUMBERS:

                            # not a match
                            individual_test_result = model.IndividualTestResult(
                                url_tested=iter_url_entry,
                                first_three_bytes=data,
                                is_swf=False,
                                requests_error=False,
                                error_str=None)
                            num_failures += 1

                        else:

                            # it is a match
                            individual_test_result = model.IndividualTestResult(
                                url_tested=iter_url_entry,
                                first_three_bytes=data,
                                is_swf=True,
                                requests_error=False,
                                error_str=None)
                            num_matches += 1

                        iter_domain_results_list.append(individual_test_result)
                except Exception as e:
                    logger.error("failed to get url `%s`: `%s`", iter_url_entry, e)

                    individual_test_result = model.IndividualTestResult(
                                url_tested=iter_url_entry,
                                first_three_bytes=data,
                                is_swf=False,
                                requests_error=True,
                                error_str=str(e))

                    iter_domain_results_list.append(individual_test_result)


            domain_test_results = model.DomainTestResults(
                domain=iter_domain,
                test_results=iter_domain_results_list,
                total=num_matches + num_failures,
                num_matches=num_matches,
                num_failures=num_failures)

            self.all_results.results.append(domain_test_results)

            num_global_matches += num_matches
            num_globl_failures += num_failures

        # now write the results
        logger.info("done, did `%s` tests, `%s` were SWF files and `%s` were not",
            num_global_matches + num_globl_failures, num_global_matches, num_globl_failures)

        logger.info("writing results to file `%s`", self.args.results_file)

        with open(self.args.results_file, "w", encoding="utf-8") as f:

            result_as_dict = attr.asdict(self.all_results)
            json_str = json.dumps(result_as_dict, indent=4, cls=utils.CustomEncoder)
            f.write(json_str)










