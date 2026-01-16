#! /usr/bin/env python
# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: spaceoddity.py                                        |     ()     |
# Date    : 12/29/2025                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

"""
The main file that runs the program

This file is executable and can be called from the terminal like:

foo@bar:~$ cd [path to directory of this file]
foo@bar:~[path to directory of this file] ./spaceoddity.py [cmd line]

or if installed in a global location:

foo@bar:~$ spaceoddity [cmd line]

Typical usage is show in the main() method.
"""

# TODO: ok the problem here is that cron jobs run as soon as the computer
# boots, but before a user logs in.
# if you leave the comp on the login screen, the cron job will run, delete the
# old file, download the new one, but has no screen (the env stuff in the cron
# jpb) and also has no user to run the dconf settings.
# so once you DO log in, you end up with the dconf settings (for that
# user) still pointing to a file that has since been deleted.
# if we could eliminate renaming the actual image file, then not being able to
# change the settings shouldn't be an issue.
# BUT in my experience, setting the desktop image to a file w/ the same name as
# the previous one does not change the background (caching and whatnot).
# so we need to find a happy medium here (BCS wrap set background in a
# try..except)

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# system imports
from datetime import datetime
import json
import os
from pathlib import Path
import sys
from urllib import request

# third party imports
import cnlib.cnfunctions as F
from crontab import CronTab
import spaceoddity_base as B
from spaceoddity_base import _
from spaceoddity_base import SpaceoddityBase

# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# The main class, responsible for the operation of the program
# ------------------------------------------------------------------------------
class Spaceoddity(SpaceoddityBase):
    """
    The main class, responsible for the operation of the program

    Public methods:
        main: The main method of the program

    This class does the most of the work of a typical CLI program. It parses
    command line options, loads/saves config files, and performs the operations
    required for the program.
    """

    # --------------------------------------------------------------------------
    # Class constants
    # --------------------------------------------------------------------------

    # NB: used in _enable
    S_PRG_NAME = "SpaceOddity"

    # dict keys
    S_KEY_APOD = "apod"
    S_KEY_APOD_DATE = "date"
    S_KEY_APOD_EXP = "explanation"
    S_KEY_APOD_HDURL = "hdurl"
    S_KEY_APOD_TYPE = "media_type"
    S_KEY_APOD_VER = "service version"
    S_KEY_APOD_TITLE = "title"
    S_KEY_APOD_URL = "url"
    S_KEY_FILE_OLD = "file_old"

    # the url to load json from
    S_APOD_URL = (
        "https://api.nasa.gov/planetary/apod?"
        "api_key=K0sNPQo8Dn9f8kaO35hzs8kUnU9bHwhTtazybTbr"
    )

    # acceptable types
    S_MEDIA_TYPES = ["image"]

    # format the current time in a manner that can be syntactically compared
    S_TIME_FMT = "%Y%m%d%H%M%S"
    # NB: format params are now and file ext
    S_FILE_FMT = "wallpaper_{}.{}"

    # cmd line options

    # enable option strings
    S_ARG_ENABLE_OPTION = "--enable"
    S_ARG_ENABLE_ACTION = "store_true"
    S_ARG_ENABLE_DEST = "ENABLE_DEST"
    S_ARG_DISABLE_DEST = "DISABLE_DEST"
    # I18N: enable mode help
    S_ARG_ENABLE_HELP = _("enable the program")

    # disable option strings
    S_ARG_DISABLE_OPTION = "--disable"
    S_ARG_DISABLE_ACTION = "store_true"
    # I18N: disable mode help
    S_ARG_DISABLE_HELP = _("disable the program")

    # messages

    # TODO: make all msg in color and have start/done/fail
    # I18N: install cron job
    S_MSG_CRON_ADD = _("Adding cron job... ")
    # I18N: Uninstall cron job
    S_MSG_CRON_DEL = _("Removing cron job... ")
    # I18N: Done with cron job
    S_MSG_DONE = _("Done")
    # I18N: get initial apod dict
    # NB: param is dict
    S_MSG_GET = _("Get data from server")
    # I18N: no change, exit
    S_MSG_SAME_URL = _("The APOD picture has not changed")
    # I18N: new download is not image
    S_MSG_NOT_IMG = _("The new APOD is not an image")
    # I18N: download succeeded
    S_MSG_DL = _("Downloaded image")
    # I18N: set image as background
    S_MSG_SET = _("Set image as background")
    # I18N: delete old image
    S_MSG_DEL = _("Deleted old image")

    # errors
    # I18N: error on initial get
    # NB: param is error msg
    S_ERR_GET = _("Could not get data from server: {}")
    # I18N: could not download new image
    # NB: param is error
    S_ERR_DL = _("Could not download image: {}")
    # I18N: could not set new image
    # NB: param is error
    S_ERR_SET = _("Could not set new image: {}")
    # I18N: could not delete old image
    # NB: param is error
    S_ERR_DEL = _("Could not delete old image: {}")

    # commands
    S_CMD_LIGHT = (
        "gsettings set org.gnome.desktop.background picture-uri file://{}"
    )
    S_CMD_DARK = (
        "gsettings set org.gnome.desktop.background picture-uri-dark file://{}"
    )
    # NB: the env stuff is required to futz w/ the screen from cron (which
    # technically runs headless)
    # NB: format params are uid and prg name
    S_CMD_CRON = (
        "env "
        "DISPLAY=:0 "
        "DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/{}/bus "
        # TODO: need this?
        # "/usr/bin/python3 "
        "{}"
    )

    # --------------------------------------------------------------------------
    # Initialize the new object
    # --------------------------------------------------------------------------
    def __init__(self):
        """
        Initialize the new object

        Initializes a new instance of the class, setting the default values
        of its properties, and any other code that needs to run to create a
        new object.
        """

        # do super init
        super().__init__()

        # set default config dict
        self._dict_cfg = {
            self.S_KEY_APOD: {},
            self.S_KEY_FILE_OLD: "",
        }

        # location of new file (soon to be old file)
        self._new_file = ""

    # --------------------------------------------------------------------------
    # Public methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # The main method of the program
    # --------------------------------------------------------------------------
    def main(self):
        """
        The main method of the program

        This method is the main entry point for the program, initializing the
        program, and performing its steps.
        """

        # call boilerplate code
        self._setup()

        # remove cron job (or skip if not exists)
        if self._dict_args[self.S_ARG_DISABLE_DEST]:
            self._disable()
            self._teardown()
            sys.exit(0)

        # check if we are being enabled
        if self._dict_args[self.S_ARG_ENABLE_DEST]:
            self._enable()

        # ----------------------------------------------------------------------
        # main stuff

        # do the thing with the thing
        res = self._get_apod_dict()

        self._new_file = self._dict_cfg.get(self.S_KEY_FILE_OLD, "")
        if res:
            self._get_apod_image()

        self._do_text()

        self._set_image()

        if res:
            self._delete_old_image()

        # ----------------------------------------------------------------------
        # teardown

        # call boilerplate code
        self._teardown()

    # --------------------------------------------------------------------------
    # Private methods
    # --------------------------------------------------------------------------

    # NB: these are the main steps, called in order from main

    # --------------------------------------------------------------------------
    # Boilerplate to use at the start of main
    # --------------------------------------------------------------------------
    def _setup(self):
        """
        Boilerplate to use at the start of main

        Perform some mundane stuff like setting properties.
        If you implement this function. make sure to call super() LAST!!!
        """

        # get a mutually exclusive group
        group = self._parser.add_mutually_exclusive_group()

        # add debug option
        group.add_argument(
            self.S_ARG_ENABLE_OPTION,
            action=self.S_ARG_ENABLE_ACTION,
            dest=self.S_ARG_ENABLE_DEST,
            help=self.S_ARG_ENABLE_HELP,
        )

        # add debug option
        group.add_argument(
            self.S_ARG_DISABLE_OPTION,
            action=self.S_ARG_DISABLE_ACTION,
            dest=self.S_ARG_DISABLE_DEST,
            help=self.S_ARG_DISABLE_HELP,
        )

        # do setup
        super()._setup()

    # --------------------------------------------------------------------------
    # Enable cron job
    # --------------------------------------------------------------------------
    def _enable(self):
        """
        Enable cron job
        """

        # debug foo
        if self._cmd_debug:
            print("_enable")
            return

        # show some text
        print(self.S_MSG_CRON_ADD, end="", flush=True)

        # */10 * * * * env DISPLAY=:0
        # DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /usr/bin/python3
        # /home/dana/.local/spaceoddity/src/spaceoddity.py # spaceoddity

        # ----------------------------------------------------------------------
        # get cron command

        # set the job command
        uid = os.getuid()
        cron_cmd = self.S_CMD_CRON.format(uid, self.S_PRG_NAME)

        # ----------------------------------------------------------------------
        # create cron object

        # get current user's crontab
        my_cron = CronTab(user=True)

        # find 'every' job
        my_job = None
        for job in my_cron:

            # find our job
            if job.comment == self.S_PRG_NAME:
                my_job = job
                break

        # create new job if necessary
        if not my_job:
            my_job = my_cron.new(command=cron_cmd, comment=self.S_PRG_NAME)

        # set job time
        my_job.enable()
        my_job.minute.every(10) # type: ignore

        # save job parameters
        my_cron.write()

        # show some text
        print(self.S_MSG_DONE)

    # --------------------------------------------------------------------------
    # Disable cron job
    # --------------------------------------------------------------------------
    def _disable(self):
        """
        Disable cron job
        """

        # debug foo
        if self._cmd_debug:
            print("_disable")
            return

        # show some text
        print(self.S_MSG_CRON_DEL, end="", flush=True)

        # get current user's crontab
        my_cron = CronTab(user=True)

        # remove our job
        for job in my_cron:
            if job.comment == self.S_PRG_NAME:
                my_cron.remove(job)

        # save job parameters
        my_cron.write()

        # show some text
        print(self.S_MSG_DONE)

    # --------------------------------------------------------------------------
    # Get json from api.nasa.gov
    # --------------------------------------------------------------------------
    def _get_apod_dict(self):
        """
        Description
        """

        # debug_foo
        if self._cmd_debug:
            print("_get_apod_dict")
            return True

        # get the nasa json
        try:

            # get json from url
            response = request.urlopen(self.S_APOD_URL)
            response_text = response.read()

        except OSError as error:

            # prob no internet
            print(self.S_ERR_GET.format(error))
            sys.exit(-1)

        print(self.S_MSG_GET)

        # ----------------------------------------------------------------------

        # get the old and new apod dicts
        apod_dict_old = self._dict_cfg[self.S_KEY_APOD]
        apod_dict_new = json.loads(response_text)

        # check if url is the same
        if self._check_same_url(apod_dict_old, apod_dict_new):
            print(self.S_MSG_SAME_URL)
            return False

        # check if today's apod is an image (sometimes it's a video)
        media_type = apod_dict_new[self.S_KEY_APOD_TYPE]
        if media_type not in self.S_MEDIA_TYPES:
            print(self.S_MSG_NOT_IMG)
            return False

        # apply new dict to config
        self._dict_cfg[self.S_KEY_APOD] = apod_dict_new

        return True

    # --------------------------------------------------------------------------
    # Get image from api.nasa.gov
    # --------------------------------------------------------------------------
    def _get_apod_image(self):
        """
        Description
        """

        # debug_foo
        if self._cmd_debug:
            print("_get_apod_image")
            return

        # get current apod dict
        apod_dict = self._dict_cfg[self.S_KEY_APOD]

        # get most appropriate URL
        src_url = ""
        if self.S_KEY_APOD_HDURL in apod_dict:
            src_url = apod_dict[self.S_KEY_APOD_HDURL]
        elif self.S_KEY_APOD_URL in apod_dict:
            src_url = apod_dict[self.S_KEY_APOD_URL]

        # create a download path
        now = datetime.now()
        str_now = now.strftime(self.S_TIME_FMT)
        file_ext = src_url.split(".")[-1]

        # get new pic name
        pic_name = self.S_FILE_FMT.format(str_now, file_ext)
        pic_path = B.P_DIR_CONF / pic_name

        # try to download image
        try:

            # download the image
            request.urlretrieve(src_url, pic_path)

            # store new file
            self._new_file = str(pic_path)

        except OSError as error:
            # this is a fatal error
            print(self.S_ERR_DL.format(error))
            sys.exit(-1)

        print(self.S_MSG_DL)

    # --------------------------------------------------------------------------
    # Do text overlay
    # --------------------------------------------------------------------------
    def _do_text(self):
        """
        Description
        """

    # --------------------------------------------------------------------------
    # Set the wallpaper
    # --------------------------------------------------------------------------
    def _set_image(self):
        """
        Description
        """

        # debug_foo
        if self._cmd_debug:
            print("_set_image")
            return

        try:
            F.run(self.S_CMD_LIGHT.format(self._new_file))
        except F.CNRunError as error:
            print(self.S_ERR_SET.format(error))
            sys.exit(-1)

        try:
            F.run(self.S_CMD_DARK.format(self._new_file))
        except F.CNRunError as error:
            print(self.S_ERR_SET.format(error))
            sys.exit(-1)

        print(self.S_MSG_SET)

    # --------------------------------------------------------------------------
    # Delete old image
    # --------------------------------------------------------------------------
    def _delete_old_image(self):
        """
        Description
        """

        # debug_foo
        if self._cmd_debug:
            print("_delete_old_image")
            return

        # get previous path name
        file_old = self._dict_cfg[self.S_KEY_FILE_OLD]
        path_old = Path(file_old)

        # if it exists, delete it
        if path_old.exists():
            try:
                path_old.unlink()

            except OSError as error:

                # log error
                print(self.S_ERR_DEL.format(error))

        self._dict_cfg[self.S_KEY_FILE_OLD] = self._new_file

        print(self.S_MSG_DEL)

    # --------------------------------------------------------------------------
    # Check if new URL is same as old URL
    # --------------------------------------------------------------------------
    def _check_same_url(self, old_dict, new_dict):
        """
        Description
        """

        # default return result
        same_url = False

        # check if the url is the same
        if (
            self.S_KEY_APOD_HDURL in old_dict.keys()
            and self.S_KEY_APOD_HDURL in new_dict.keys()
        ):
            if (
                old_dict[self.S_KEY_APOD_HDURL]
                == new_dict[self.S_KEY_APOD_HDURL]
            ):
                same_url = True
        elif (
            self.S_KEY_APOD_URL in old_dict.keys()
            and self.S_KEY_APOD_URL in new_dict.keys()
        ):
            if old_dict[self.S_KEY_APOD_URL] == new_dict[self.S_KEY_APOD_URL]:
                same_url = True

        # return the result
        return same_url


# ------------------------------------------------------------------------------
# Code to run when called from command line
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Code to run when called from command line

    # This is the top level code of the program, called when the Python file is
    # invoked from the command line.

    # create a new instance of the main class
    obj = Spaceoddity()

    # run the instance
    obj.main()

# -)
