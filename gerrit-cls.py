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

  # Check for a valid HTTP response.
  if response.status_code != 200:
      logging.error(f"HTTP Error {response.status_code}: {response.text}")
      return None

  # Decode the content, handling potential encoding issues.
  content = response.content.strip().decode(response.encoding or 'utf-8')
  if not content:
    logging.error('Invalid http response: empty content')
    return None

 # Gerrit adds a magic prefix to prevent JSON hijacking. It must be stripped.
  if content.startswith(GERRIT_MAGIC_JSON_PREFIX):
    index = len(GERRIT_MAGIC_JSON_PREFIX)
    content = content[index:]

  # Parse the JSON string into a Python dictionary.
  try:
    return json.loads(content)
  except ValueError:
    logging.error("Invalid json content: %s", content)


def print_landed_cls():
  """
  Fetches and prints CLs landed by the owner in the last week.
  The output is in markdown format, sorted from oldest to newest.
  """
  # Construct the URL to query for merged changes by the owner within the age limit.
  url = f"{BASE_URL}changes/?q=is:merged+owner:{OWNER}+-age:{AGE}"
  response = requests.get(url)
  cls = decode_response(response)

  # Verify that we received a valid list of CLs.
  if not isinstance(cls, list):
      print("Could not retrieve landed CLs.")
      return

  # Gerrit returns CLs sorted by most recently updated first.
  # We reverse the list to print from oldest to newest.
  print("\n## Landed")
  for cl in reversed(cls):
    cl_subject = cl['subject'].strip()
    cl_link = f"{BASE_URL}c/{cl['project']}/+/{cl['_number']}"
    cl_markdown = f"* [{cl_subject}]({cl_link})"
    print(cl_markdown)

def print_reviewed_cls():
  """
  Fetches and prints statistics for CLs reviewed by the owner in the last week.
  """
  # Construct the URL to query for changes reviewed by the owner, excluding their own CLs.
  url = f"{BASE_URL}changes/?q=reviewer:{OWNER}+-owner:{OWNER}+-age:{AGE}"
  response = requests.get(url)
  cls = decode_response(response)

  # Verify that we received a valid list of CLs.
  if not isinstance(cls, list):
      print("Could not retrieve reviewed CLs.")
      return

  # Count the number of reviewed CLs that are now merged.
  lgtms_count = 0
  for cl in cls:
    if cl['status'] == 'MERGED':
      lgtms_count += 1

  print("\n## Reviews")
  print(f"* {lgtms_count} LGTMs")
  print(f"* {len(cls)} CLs")

if __name__ == "__main__":
  print_landed_cls()
  print_reviewed_cls()
