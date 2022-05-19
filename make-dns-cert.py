#! /usr/bin/env python3

# GPG-->DNS CERT/TXT tool.
# Dan Mahoney (danm@prime.gushi.org) and Evan Hunt (each@isc.org)
# ISC License Applies
# $Id: make-dns-cert.sh,v 1.4 2009/10/30 19:20:18 danm Exp $

# python conversion by Chris Kobayashi <software-gpgdnscert@disavowed.jp
# original from https://gushi.org/make-dns-cert/HOWTO.html

import base64
import gnupg
import getopt
import re
import sys

def split_input(string, chunk_size):
  num_chunks = int(len(string)/chunk_size)
  if (len(string) % chunk_size != 0):
    num_chunks += 1
  output = []
  for i in range(0, num_chunks):
    output.append(string[chunk_size*i:chunk_size*(i+1)])
  return output

def print_key(key, length):
  for line in split_input(key, length):
    print ('\t\t\t\t\t{}'.format(line.decode('utf-8')))
  print ('\t\t\t\t\t)\n' )

def main(argv):
  email = ''
  keyid = ''
  url = ''
  pkaemail = ''
  certmail = ''
  small_key = ''
  ttl = 30
  nsupdate = False
  small = False

  try:
    opts, args = getopt.getopt(argv,"he:k:u:ns",["email=", "keyid=", "url=", 'nsupdate', 'small'])
  except getopt.GetoptError:
    print ('make-dns-cert.py -e <email> -k <keyid> -u <url>\n')
    sys.exit(2)
  for opt, arg in opts:
    if opt == '-h':
      print ('make-dns-cert.py -e <email> -k <keyid> -u <url>\n')
      sys.exit()
    elif opt in ("-e", "--email"):
      email = arg
    elif opt in ("-k", "--keyid"):
      keyid = arg
    elif opt in ("-u", "--url"):
      url = arg
    elif opt in ('-n', '--nsupdate'):
      nsupdate = True
    elif opt in ('-s', '--small'):
      small = True

  if not keyid:
    print ('make-dns-cert.py: keyid must be specified')
    sys.exit(1)

  gpg = gnupg.GPG()

  cert = gpg.list_keys(keys=keyid)
  if not cert:
    print ('make-dns-cert.py: invalid keyid')
    sys.exit(3)

  # if email address not specified, grab the first one from the key
  if not email:
    result = re.search('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', cert[0]['uids'][0])
    if not result:
      print('make-dns-cert.py: no email specified and key has no uid')
      sys.exit(4)
    email = result.group(1)

  pkaemail = re.sub(r'@', '._pka.', email)
  certmail = re.sub(r'@', '.', email)

  fingerprint = cert[0]['fingerprint']
  small_key_bytes = str(hex(len(fingerprint)))[2:] + fingerprint

  small_key = base64.b64encode(bytes.fromhex(small_key) + bytes(url, 'utf-8'))
  big_key = base64.b64encode(gpg.export_keys(keyids=keyid, armor=False, minimal=True))

  if nsupdate is True:
    if url:
      print ('update add {}. {} TXT v=pka1\\;fpr={}\\;uri={}'.format(pkaemail, ttl, fingerprint, url) )
    if small is True:
      print ('update add {}. {} CERT IPGP 0 0 {}'.format(certmail, ttl, small_key.decode('utf-8')) )
    else:
      print ('update add {}. {} CERT PGP 0 0 {}'.format(certmail, ttl, big_key.decode('utf-8')) )
  else: # nsupdate strings:
    if url:
      print ('; Publish your keys at', url)
      print ('; gpg --export --armor --export-options export-minimal', keyid )
      print ('; PKA record for keyid', keyid)
      print ('{}. {} IN\tTXT\t"v=pka1\\;fpr={}\\;uri={}"\n'.format(pkaemail, ttl, fingerprint, url) )
    if small is True:
      print ('; Short CERT Record for keyid', keyid )
      print ('{}.\t{}\t{}'.format(certmail, ttl, "IN CERT 6 0 0 ("))
      print_key(small_key, 36)
    else:
      print ('; Long CERT Record for keyid', keyid)
      print ('{}.\t{}\t{}'.format(certmail, ttl, "IN CERT 3 0 0 (") )
      print_key(big_key, 36)

if __name__ == "__main__":
  main(sys.argv[1:])
