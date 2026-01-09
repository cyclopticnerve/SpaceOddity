
import argparse

parser = argparse.ArgumentParser()


# get a mutually exclusive group
group = parser.add_mutually_exclusive_group()

# add debug option
group.add_argument(
    "--enable",
    action="store_true",
    dest="ENABLE_DEST",
    help="",
)

# add debug option
group.add_argument(
    "--disable",
    action="store_true",
    dest="DISABLE_DEST",
    help="",
)

# run the parser
args = parser.parse_args()

# convert namespace to dict
dict_args = vars(args)

print(dict_args)
