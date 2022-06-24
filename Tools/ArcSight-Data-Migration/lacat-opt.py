#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  MODIFIED VERSION FOR ACHMEA ArcSight Migration to MicroSoft Sentinel
#  ABLE TO READ AND CONVERT MORE MODERN LOGGER .dat FORMATS
#  Performace Optimized
#
#  TODO:
#    What is the meaning/significance of the skipped data?  Search for "## SKIP:"  in this file
#    Is it ok to skip syslog header
#    Verify input and output (i.e. bring logger archive online and compare to json files; count events etc) 
#    Record types? (ChunkVersion, SourceType, Flags):  ('6', '0', '5') is processed, ('100', '0', '1') and ('5', '0', '5') are skipped.
#	100=ROS - Read Optimized Search (some indexing data?) 
#         5=Internal logger events, not of interestt (?)
#       . 6=CEF records we can process 
#    ...
#
#
# (c) Copyright 2014 Hewlett-Packard Development Company, L.P.
# (c) Copyright 2022 Achmea Interne Diensten NV
#
# Licensed under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the
# following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# originally written jan23,2014
# version 20140128 - code stable, repo created -jk
# version 20161021 - fixed archive parsing, port to python 3 -jm
# version 20161024 - write to kafka, add back support for python 2 -jm
# version 20220211 - Removed Python2, stripped unnecessary stuff, fixed new meta and logger format
# version 20220310 - Performance optimized

from csv import DictReader
from glob import glob
from json import dumps
import optparse
import gzip
import re
from struct import unpack
from os import path, ttyname
from sys import stdout, stderr
from time import ctime, gmtime, asctime


# We could use the six library for this, but I would rather not have any deps.
iteritems = dict.items
text_read_mode = 'rt'

from io import BytesIO

cef_key_re = re.compile(r" ([\w.-]+?)=")
cef_first_key_re = re.compile(r"([\w.-]+?)=")
cef_pipe_re = re.compile(r"\\*?\|")


def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)

def parse_cef(s):
    d = dict()
    fields = []
    field_start = 0
    num_fields = 0
    for match in cef_pipe_re.finditer(s):
        start, end = match.span()
        if (end-start)%2==0:
            # There are an odd number of backslashes, so the pipe is escaped.
            # A negative lookbehind may be a better way to do this.
            continue
        field = s[field_start:end-1]
        num_fields += 1
        #fields.append(field)
        #if (len(field) != len(field.replace("\\|","|").replace("\\\\","\\"))):
            #pdb.set_trace()
        fields.append(field.replace("\\|","|").replace("\\\\","\\"))
        field_start = end
        if num_fields == 7: #len(fields)==7:
            break
    else:
        raise ValueError("CEF string does not have enough pipe characters")

    #if 'CEF:' not in fields[0]:
    #    raise ValueError("CEF string is missing CEF:0 or CEF:1 header")

    d["devicevendor"], d["deviceproduct"], d["deviceversion"], d["signatureid"], d["name"], d["severity"] = fields[1], fields[2], fields[3], fields[4], fields[5], fields[6]
    
    s = s[field_start:]
    last_start = len(s)
    matches = cef_key_re.finditer(s)
    # Look at the key value pairs from the end to the beginning because the
    # only way to find the end of a value is to find the start of the next key.
    for match in reversed(list(matches)):
        start, end = match.span()
        #d[match.group(1)] = unescape_cef_value(s[end:last_start])
        d[match.group(1)] = s[end:last_start].replace("\\\\\\\\","\\\\").replace("\\\\","\\").replace("\\=","=").replace("\\r","\r").replace("\\n", "\n")
        last_start = start

    # The first key-value pair may be preceded by a space. If it is not, add
    # it to d .
    if last_start:
        leftover = s[:last_start]
        match = cef_first_key_re.match(leftover)
        if match:
            #d[match.group(1)] = s[match.end():last_start]
            #d[match.group(1)] = unescape_cef_value(s[match.end():last_start])
            d[match.group(1)] = s[match.end():last_start].replace("\\\\\\\\","\\\\").replace("\\\\","\\").replace("\\=","=").replace("\\r","\r").replace("\\n", "\n")
    return d


def unescape_cef_value(s):
    #  replace \\r by \r
    #  replace \\n by \n
    #  replace \\= by =
    #  replace \\ by \   (slash in string literal must be escaped with slash)
    ###s = s.replace("\\r","\r").replace("\\n", "\n")
    #return s.replace("\\=","=").replace("\\\\", "\\").replace("\\r","\r").replace("\\n", "\n")
    #return re.sub("\\\\+","\\\\", s.replace("\\=","=").replace("\\r","\r").replace("\\n", "\n"))
    return s.replace("\\\\\\\\","\\\\").replace("\\\\","\\").replace("\\=","=").replace("\\r","\r").replace("\\n", "\n")

def get_metadata(f):
    rows = list(f)
    # Why is the first row space separated, instead of comma separated? And no space between these 2?
    rows[0] = rows[0].replace("MinEventEndTimeMaxEventEndTime","MinEventEndTime MaxEventEndTime")
    rows[0] = rows[0].replace(" ",",")
    return list(DictReader(rows))


def read_chunk(f, start, count):
    """ move around inside gigantor file and return the gzip'd embed """
    #print("read_chunk start,count= ",start,count)
    f.seek(start+256)  # offset plus header   ## SKIP: nothing of value in header?
    chunk = BytesIO(f.read(count-256))
    return gzip.GzipFile(fileobj=chunk)


def parse_chunk(ck, event_count, ck_id):
    # We have to read some bytes from a tiny header, but we don't do anything
    # with those bytes.
    # print("parse_chunk event_count: ",event_count)
    zero, length = unpack(">hh", ck.read(4)) # '>'=big-endian; h=short = 2 bytes
    # skip the receiver name and an int32 after it.
    ck.read(length + 4)  # just skip 4 bytes  ## SKIP: no significance? or alignment bytes?

    for _ in range(event_count):
        #unpacked = unpack(">qllqq", ck.read(32))   # q=8bytes, l=4
        #(time, length, recv_id, dvc_ip, zero) = unpacked
        ck.read(8) # skip time, not used        
        (length,) = unpack(">l", ck.read(4))   # q=8bytes, l=4
        ck.read(20)  # skip 4=recv_id 8=dvc_ip 8=zero
        #print("time: ", ctime(time/1000))
        #event = f.read(length).decode('utf-8')
        #if length > 5000:
        #  eprint("eventLength is wel heel groot :",length)
        yy=bytearray(ck.read(length))
        #print(ck.tell())
# Next statement fails on syslog header - can't always decode to utf-8
# so first drop syslog header, then decode
#        yy=yy[yy.index(b"CEF"):len(yy)]
        # del yy[0:yy.index(b"CEF")]
        # always read next 8 trailing bytes, dunno what that is
        ck.read(8)   ## SKIP: ???         
        try: 
            # strip off syslog header, if present
            event = yy[yy.index(b"CEF:"):].decode('utf-8')
        except ValueError:
            eprint("No 'CEF:' header present in event ", _, "in Chunk ", ck_id)
        else:
            yield event #[event.index(u"CEF:"):]    # u"..."  means Unicode string
        #xx2=ck.read(8)  ## SKIP: another 8 bytes, values like  ( b'Gbdg\\=\\=' , b'4Rog\\=\\=' , b'CBSA\\=\\=', b'JZdg\\=\\=', b'PZ2w\\=\\=',b'E0HA\\=\\=',b'Fz9Q\\=\\=',b'+1bA\\=\\=',b'tXkQ\\=\\=')
        #if  xx2 not inset(( b'Gbdg\\=\\=' , b'4Rog\\=\\=' , b'CBSA\\=\\=', b'JZdg\\=\\=', b'PZ2w\\=\\=',b'E0HA\\=\\=',b'Fz9Q\\=\\=',b'+1bA\\=\\=',b'tXkQ\\=\\=')): 
        #  eprint("STOP Reading funny bytes: ", xx2)
        #yield event #[event.index(u"CEF:"):]    # u"..."  means Unicode string

def dump_cef(cef_recs, f):
    for cr in cef_recs:
        #cr = cr.strip()  no leading or trailing whitespace to strip()
        #print(dumps(p_c, separators=(",", ":")))  # no whitespace, no indent = 1 record per line
        print(dumps(parse_cef(cr), separators=(",", ":")), file=f)  # no whitespace, no indent = 1 record per line

def read_cef(file_list):
    for fdat, fcsv in file_list:
        if fcsv.endswith('.gz'):
            with gzip.open(fcsv, text_read_mode) as f:
                metadata = get_metadata(f)
        else:
            with open(fcsv, text_read_mode) as f:
                metadata = get_metadata(f)
        ck_count=0
        num_chunks = len(metadata)
        with open(fdat,'rb') as fdata:
            for chunk_md in metadata:
                #print(chunk_md)
                ck_count += 1
                start, event_count, chunk_length, chunk_id  = int(chunk_md['BeginOffset']), int(chunk_md['EventCount']), int(chunk_md['Length']), chunk_md['ChunkId'] 

                if int(chunk_md['ChunkVersion']) == 100:   # Read Optimized Search data
                  eprint("ROS - ChunkId ", chunk_id, " - skip ", event_count, " data bytes.")
                  continue
                if int(chunk_md['ChunkVersion']) == 5:     # Internal Event Data, ArcSight health data etc.
                  eprint("Int - ChunkId ", chunk_id, " - skip ", event_count, " data bytes.")
                  continue
                #print(asctime(gmtime(int(chunk_md['StartET']) / 1000)))
                #print(asctime(gmtime(int(chunk_md['EndET']) / 1000)))
                #print(asctime(gmtime(int(chunk_md['MinEventEndTime']) / 1000)))
                #print(asctime(gmtime(int(chunk_md['MaxEventEndTime']) / 1000)))
                #print(asctime(gmtime(int(chunk_md['ReceiptTime']) / 1000)))
                
                if options.term:
                  print("CHUNK:", ck_count," van ", num_chunks, " Ofs:",start," Len:", chunk_length," #Evt:", event_count, file=tty, end='\r')

                with read_chunk(fdata, start, chunk_length) as chunk:
                    for event in parse_chunk(chunk, event_count, chunk_id):
                        yield event


if __name__ == '__main__':
    usage = """%prog [options] path_to_dat path_to_meta

Extracts cef events from Logger Archive files to stdout of specified output file

Modified to support newer logger data format
Skips Read Optimized Search (ROS) records (ChunkVersion 100)

(c) Achmea Strategie & Transformatie | IT Operations 2022

"""
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "-j", "--json", dest="json", action="store_true",
        default=False, help="export as json instead of raw cef")
    parser.add_option(
        "-d", "--directory", dest="directory", action="append", default=[],
        help="specify a directory full of dat and csv files")
    parser.add_option(
        "-o", "--output", dest="outfile", action="store", default="",
        help="specify an output file. If omitted output goes to stdout")
    parser.add_option(
        "-t", "--terminal", dest="term", action="store_true",
        default=False,
        help="Write progress information to the terminal, regardless of redirection of stdout and stderr")
    options, args = parser.parse_args()

    # ArcSight_Data_46_0504403158265495552.dat
    # ArcSight_Metadata_46_504403158265495552.csv
    if options.directory:
        # user wants to scan through an entire directory
        csvFiles = (
            glob(options.directory[0] + '*.csv') +
            glob(options.directory[0] + '*.csv.gz')
        )
        file_list = []
        for csvFile in csvFiles:
            csv_path = csvFile.rstrip('.gz').rstrip('.csv')
            datFinder = path.basename(csv_path)[18:].split('_')  # returns list of significant digits
            # ArcSight_Metadata_46_504403158265495552.csv = ['46', '504403158265495552']
            # we need the significant digits because the archive loggers sometimes pad with extra zero
            datFile = (glob(options.directory[0] + '*_' + datFinder[0] + '_*' + datFinder[1] + '*.dat'))
            # datFile returns list of single file matching the csv significant digits
            file_list.append((datFile[0], csvFile))  # nice list of (CSV,DAT) tuples
        if not file_list:
            raise ValueError("No files found in directory.")

    elif len(args) == 2:
        # user manually specifies the dat and csv files
        f_dat = args[0]
        f_csv = args[1]
        file_list = [(args[0], args[1])]

    elif len(args) < 2:
        parser.print_help()
        raise SystemExit

    if options.outfile:
        fout = gzip.open(options.outfile, 'wt')
    else:
        fout = stdout

    if options.term:
      tty = open(ttyname(0), 'wt')

    events = read_cef(file_list)

    dump_cef(events, fout)
    fout.close()

    if options.term:
      print("", file=tty)
      tty.close()
######## ~- EOF -~ ########
