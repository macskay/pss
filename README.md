# Part-Structured Spotting

[![Python Versions](https://img.shields.io/badge/python-3.5-blue.svg)](https://github.com/mkli90/pss/)

# Instructions

Query and Target Files need to be placed into the resources folder.
Be aware that the parameters -t and -q are mandatory.

"-v", "--verbose", Activates verbose mode (DEBUG-logging)
"-s", "--scale", "Determines the Scale of the Query and Target (default=1)", type=float
"-l", "--limit", "This gives the top n results (default=10)", type=int
"-i", "--index", "This uses the i-th symbol of the query set (Must be given, if the query is an SVG)", type=int)
"-q", "--query", "Path to the query file", type=str
"-t", "--target", "Path to the target file", type=str