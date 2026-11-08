# Source - https://stackoverflow.com/a/42641792
# Posted by Anand Tripathi, modified by community. See post 'Timeline' for change history
# Retrieved 2026-11-08, License - CC BY-SA 4.0

# original code:
# #!/usr/bin/python
# import os

# myfile = "/tmp/foo.txt"
# # If file exists, delete it.
# if os.path.isfile(myfile):
#     os.remove(myfile)
# else:
#     # If it fails, inform the user.
#     print("Error: %s file not found" % myfile)

import os
import logging


def remove_file(file_path):

    if os.path.isfile(file_path):
        os.remove(file_path)
        logging.info("file %s deleted"% file_path)
    else:
        logging.info("Error: %s file not found" % file_path)