import json
import logging
import requests
import argparse

BASE_URL = "https://chromium-review.googlesource.com/"
OWNER = "emiliapaz@chromium.org"
AGE = "6days"
GERRIT_MAGIC_JSON_PREFIX = ")]}'\n"

def decode_response(response):
    """Returns a decoded JSON as a dict from a Gerrit API REST request."""
    try:
        content = response.content.strip().decode(response.encoding)
        if not content:
            logging.error('Invalid http response')
            return None

        if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
            index = len(GERRIT_MAGIC_JSON_PREFIX)
            content = content[index:]

        return json.loads(content)
    except json.JSONDecodeError as e:
        logging.error("Failed to decode JSON: %s", str(e))
        return None
    except requests.RequestException as e:
        logging.error("HTTP request failed: %s", str(e))
        return None

def print_landed_cls(owner, age):
    """Prints CLs landed in the last week in markdown format."""
    URL = "{}changes/?q=is:merged+owner:{}+-age:{}".format(BASE_URL, owner, age)
    CLs = decode_response(requests.get(URL))

    if CLs:
        for cl in CLs:
            cl_markdown = 'Landed [cl](crrev.com/c/' + cl['submission_id'] + '): ' + cl['subject']
            print(cl_markdown)
    else:
        print("No CLs landed or error occurred.")

def print_reviewed_cls(owner, age):
    """Prints the number of CLs reviewed in the last week."""
    URL = "{}changes/?q=reviewer:{}+-owner:{}+-age:{}".format(BASE_URL, owner, owner, age)
    CLs = decode_response(requests.get(URL))

    if CLs:
        print('CLs reviewed: ', len(CLs))
    else:
        print("No CLs reviewed or error occurred.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch and display CL information.')
    parser.add_argument('--owner', type=str, default=OWNER, help='Owner email for CLs (default: {})'.format(OWNER))
    parser.add_argument('--age', type=str, default=AGE, help='Age of CLs to consider (default: {})'.format(AGE))
    args = parser.parse_args()

    try:
        print("CLs landed in the last week:")
        print_landed_cls(args.owner, args.age)

        print("\nCLs reviewed in the last week:")
        print_reviewed_cls(args.owner, args.age)
    except Exception as e:
        logging.error("An unexpected error occurred: %s", str(e))
