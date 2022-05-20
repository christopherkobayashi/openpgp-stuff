#! /usr/bin/env python3

import re
import getopt
import sys

def main(argv):
  zone_data = []
  origin = ''
  data = ''
  record = ''
  payload = ''
  server = ''
  port = ''

  try:
    opts, args = getopt.getopt(argv,"s:p:",["server=", "port="])
  except getopt.GetoptError:
    print ('zonetonsupdate.py [-s <server>] [-p <port>')
    sys.exit(-1)
  for opt, arg in opts:
    if opt in ("-s", "--server"):
      server = arg
    elif opt in ("-p", "--port"):
      port = arg

  for line in sys.stdin:
    zone_data += [ line ]

  for line in zone_data:
    line_cooked = re.sub(r';.*', '', line).rstrip('\n').lstrip(' ').lstrip('\t')
    if line_cooked.startswith('$ORIGIN'):
      result = re.search('\$ORIGIN (.*)', line_cooked)
      origin = result.group(1)
    elif len(line_cooked) == 0:
      continue
    else:
      data += line_cooked

  # we could do this as just two matches, but we might want to do length
  # sanity checks at some point
  result = re.search('(.*?) (.*) \(?([a-zA-Z0-9]*)\)?', data)

  if result.group(1) and result.group(2) and result.group(3):
    record = '{}.{}'.format(result.group(1), origin) #.replace('\\', '')
    type = result.group(2) #.replace('\\', '')
    payload = result.group(3) #.replace('\\', '')

    if server:
      print("server {} {}".format(server, port))
    print("update del {}".format(record))
    print("update add {} 600 {} {}".format(record, type, payload))
    print("send")

if __name__ == "__main__":
  main(sys.argv[1:])
