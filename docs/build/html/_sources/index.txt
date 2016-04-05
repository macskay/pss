.. Part-Structured Spotting of Cuneiform Characters documentation master file, created by
   sphinx-quickstart on Tue Apr  5 09:36:17 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Part-Structured Spotting of Cuneiform Characters's documentation!
============================================================================


# Instructions
--------------

Query and Target Files need to be placed into the resources folder.
Be aware that the parameters -t and -q are mandatory.

# Parameters
------------

================= ============================================================================================== ======
    Parameter           Description                                                                               Type
================= ============================================================================================== ======
"-v/--verbose"    Activates verbose mode (DEBUG-logging)                                                           --
"-s/--scale"      "Determines the Scale of the Query and Target (default=1)"                                      float
"-l/--limit"      "This gives the top n results (default=10)"                                                     int
"-i/--index"      "This uses the i-th symbol of the query set (Must be given, if the query is an SVG)"            int
"-q/--query"      "Path to the query file"                                                                        str
"-t/--target"     "Path to the target file"                                                                       str
================= ============================================================================================== ======

# API Documentation
-------------------

.. toctree::
   :maxdepth: 2

   pss