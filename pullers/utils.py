from csv import reader
import requests
import time
import sys, os
from datetime import date
import logging


class OpenFormat:

    def __init__(self,  header, example, separator=",",  comment="#"):

        if separator:

            example_read = [x for x in reader([example], delimiter=separator)]
            header_read = [x for x in reader([header], delimiter=separator)]
            if (len(example_read[0]) != len(header_read[0])):
                raise Exception("Headers do not match example")
            self.headers = header_read[0]
        else:
            self.headers = [header]

        self.separator = separator
        self.comment = comment


class OpenSource:

    def __init__(self, url, alias=None):

        self.url = url
        self.format = None
        self.alias = alias if alias else url

    def __str__(self):

        if self.alias:
            return self.alias
        else:
            return self.url

    def add_format(self, header, example, separator=",",  comment="#"):

        try:
            self.format = OpenFormat(header, example, separator=separator,  comment=comment)

        except Exception as exc:

            raise exc

    def pull_records(self, proxies=None):

        records = list()

        if not self.format:

            return "No format added yet"

        try:

            r = requests.get(self.url, proxies=proxies)
            while r.status_code != 200:
                time.sleep(60)
                r = requests.get(self.url, proxies=proxies)

            for line in r.text.split("\n"):

                if self.format.comment in line:

                    line = line.split(self.format.comment)[0]

                if line:

                    if self.format.separator:

                        keys = self.format.headers
                        values = line.split(self.format.separator)
                        if len(keys) == len(values):

                            tmp_record = (dict(zip(keys, values)))

                        else:

                            pass

                    else:

                        tmp_record = ({self.format.headers[0]: line})

                    records.append(tmp_record)

            return records

        except:
            pass


def pull_config():

    config_file = "../configs/open.conf"
    file_lines = open(config_file, "r").readlines()

    block_spots = []
    s_e = (None, None)
    for i, line in enumerate(file_lines):

        if "START" == line.strip().upper():

            s_e = (i, None)

        elif "END" == line.strip().upper():

            s_e = (s_e[0], i)

        if s_e[0] and s_e[1]:

            block_spots.append(s_e)
            s_e = (None, None)

    open_sources = list()
    for pair in block_spots:

        url, alias = None, None
        header, example, separator, comment = None, None, ",", "#"

        for line in file_lines[pair[0]:pair[1]]:

            if line.count("=") == 0:
                continue

            else:

                line = line.strip()
                key, val = line.split("=", 1)

                if key == "url":
                    url = val

                elif key == "alias":
                    alias = val

                elif key == "header":
                    header = val

                elif key == "example":
                    example = val

                elif key == "separator":
                    separator = val if val.lower() != "none" else None

                elif key == "comment":
                    comment = val

        if (not url) or (not header) or (not example):

            print("bad format")

        else:

            temp_source = OpenSource(url, alias=alias)
            temp_source.add_format(header, example, separator=separator, comment=comment)

            open_sources.append(temp_source)

    return open_sources
