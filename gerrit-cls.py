import json
import logging
import re
import requests

BASE_URL = "https://chromium-review.googlesource.com/"
OWNER = "emiliapaz@chromium.org"
AGE = "6days"
GERRIT_MAGIC_JSON_PREFIX = ")]}'\n"

def decode_response(response):
  """ Returns a decoded JSON as a dict from a Gerrit API REST request. """

  content = response.content.strip().decode(response.encoding)
  if not content:
    logging.error('Invalid http response')
    return content

  if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
    index = len(GERRIT_MAGIC_JSON_PREFIX)
    content = content[index:]

  try:
    return json.loads(content)
  except ValueError:
    logging.error("Invalid json content: %s", content)


def print_landed_cls():
  """ Prints CLs landed in the last week in markdown format. """

  URL = "{}changes/?q=is:merged+owner:{}+-age:{}".format(BASE_URL, OWNER, AGE)
  CLs = decode_response(requests.get(URL))

  for cl in CLs:
    cl_subject = re.sub("\[.*?\]", "", cl['subject']) 
    cl_markdown = '* Landed [cl](crrev.com/c/' + cl['submission_id'] + '):' + cl_subject
    print(cl_markdown)


def print_reviewed_cls():
  """ Prints the number of CLs reviewed in the last week. """

  URL = "{}changes/?q=reviewer:{}+-owner:{}+-age:{}".format(BASE_URL, OWNER, OWNER, AGE)
  CLs = decode_response(requests.get(URL))

  print('CLs reviewed: ' , len(CLs))


if __name__ == "__main__":
  print_landed_cls()
  print_reviewed_cls();
