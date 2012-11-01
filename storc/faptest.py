#!/bin/python

from libfap import *

strings= ["\xc0\x00\x82\xa0\xa8fbb`\xa6\xa8\x9e\xa4\x86@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0/063648h4038.37N/11153.92WO313/000/A=004379/KE7SWA\xc0",
  "\xc0\x00\x82\xa0\xa8fbb`\xa6\xa8\x9e\xa4\x86@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0/063653h4038.37N/11153.92WO313/000/A=004379\xc0",
  "\xc0\x00\x82\xa0\xa8fbb`\xa6\xa8\x9e\xa4\x86@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0/063715h4038.37N/11153.92WO313/000/A=004379\xc0",
  "\xc0\x00\x82\xa0\xa8fbb`\xa6\xa8\x9e\xa4\x86@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0/063725h4038.37N/11153.92WO313/000/A=004379\xc0",]

libfap.fap_init()
for s in strings:
  packet = libfap.fap_parseaprs(s,len(s),0)
  print "CALLSIGN:%s\tBODY: %s" % (packet[0].src_callsign, packet[0].body)
 ### for p in packet:
  #  print p
#  print "packet whole: %s" % packet
  libfap.fap_free(packet)
   
libfap.fap_cleanup()
