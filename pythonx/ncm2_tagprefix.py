# -*- coding: utf-8 -*-

import vim
from ncm2 import Ncm2Source, getLogger
import re
from os import path

logger = getLogger(__name__)

class Source(Ncm2Source):

    def on_complete(self, ctx, cwd, tagfiles):

        base = ctx['base']
        tags = {}

        for name in tagfiles:
            try:
                p = path.join(cwd, name)
                for line in binary_search_lines_by_prefix(base, p):
                    fields = line.split("\t")

                    if len(fields)<2:
                        continue

                    tags[fields[0]] = dict(word=fields[0], menu=fields[1])
            except Exception as ex:
                logger.exception('failed searching %s', name)

        # unique
        matches = list(tags.values())

        # there are huge tag files sometimes, be careful here. it's meaningless
        # to have huge amout of results.
        refresh = False
        if len(matches)>100:
            matches = matches[0:100]
            refresh = True

        self.complete(ctx, ctx['startccol'], matches, refresh)


def binary_search_lines_by_prefix(prefix, filename):

    with open(filename, 'r') as f:

        def yield_results():
            while True:
                line = f.readline()
                if not line:
                    return
                if line[:len(prefix)] == prefix:
                    yield line
                else:
                    return

        begin = 0
        f.seek(0, 2)
        end = f.tell()

        while begin < end:

            middle_cursor = int((begin+end)/2)

            f.seek(middle_cursor, 0)
            f.readline()

            line1pos = f.tell()
            line1 = f.readline()

            line2pos = f.tell()
            line2 = f.readline()

            line2end = f.tell()

            key1 = '~~'
            # if f.readline() returns an empty string, the end of the file has
            # been reached
            if line1 != '':
                key1 = line1[:len(prefix)]

            key2 = '~~'
            if line2 != '':
                key2 = line2[:len(prefix)]

            if key1 >= prefix:
                if line2pos < end:
                    end = line2pos
                else:
                    # (begin) ... | line0 int((begin+end)/2) | line1 (end) | line2 |
                    #
                    # this assignment push the middle_cursor forward, it may
                    # also result in a case where begin==end
                    #
                    # do not use end = line1pos, may results in infinite loop
                    end = int((begin+end)/2)
                    if end == begin:
                        if key1 == prefix:
                            # find success
                            f.seek(line2pos, 0)
                            yield from yield_results()
                        return
            elif key2 == prefix:
                # find success
                # key1 < prefix  && next line key2 == prefix
                f.seek(line2pos, 0)
                yield from yield_results()
                return
            elif key2 < prefix:
                begin = line2end
                # if begin==end, then exit the loop
            else:
                # key1 < prefix &&  next line key2 > prefix here, not found
                return


source = Source(vim)

on_complete = source.on_complete
