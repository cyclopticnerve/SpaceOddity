# ------------------------------------------------------------------------------
# Project : SpaceOddity                                            /          \
# Filename: post_install.py                                       |     ()     |
# Date    : 09/23/2022                                            |            |
# Author  : cyclopticnerve                                        |   \____/   |
# License : WTFPLv2                                                \          /
# ------------------------------------------------------------------------------

"""
The post-install script for this project

This module does some stuff after install
"""

# ------------------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------------------

# system imports
import gettext
import locale
from pathlib import Path
import subprocess

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# gettext stuff for CLI and GUI
# NB: keep global
# to test translations, run as foo@bar:$ LANGUAGE=xx ./spaceoddity.py

# path to project dir
T_DIR_PRJ = Path(__file__).parents[1].resolve()

# init gettext
T_DOMAIN = "spaceoddity"
T_DIR_LOCALE = T_DIR_PRJ / "i18n/locale"
T_TRANSLATION = gettext.translation(T_DOMAIN, T_DIR_LOCALE, fallback=True)
_ = T_TRANSLATION.gettext

# fix locale (different than gettext stuff, mostly fixes GUI issues, but ok to
# use for CLI in the interest of common code)
locale.bindtextdomain(T_DOMAIN, T_DIR_LOCALE)


# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# The class to use for installing/uninstalling
# ------------------------------------------------------------------------------
class CNPostInstall:
    """
    The class to use for installing a PyPlate program

    This class performs the install operation.
    """

    # --------------------------------------------------------------------------
    # Class constants
    # --------------------------------------------------------------------------

    # NB: format param is prog name
    # I18N: install cron job
    S_MSG_RUN = _("Running {}... ")
    # I18N: success
    S_MSG_DONE = _("Done")
    # I18N: fail
    S_MSG_FAIL = _("Failed")

    # get prog name
    S_PRG_NAME = "spaceoddity"

    # --------------------------------------------------------------------------
    # Class methods
    # --------------------------------------------------------------------------

    # # --------------------------------------------------------------------------
    # # Initialize the new object
    # # --------------------------------------------------------------------------
    # def __init__(self):
    #     """
    #     Initialize the new object

    #     Initializes a new instance of the class, setting the default values
    #     of its properties, and any other code that needs to run to create a
    #     new object.
    #     """

    #     # always call super
    #     super().__init__()

    # --------------------------------------------------------------------------
    # Public methods
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # Install the program
    # --------------------------------------------------------------------------
    def main(self):
        """
        Install the program

        Runs the install operation.
        """

        # do setup
        # self._setup()

        # run program
        self._do_run()

        # wind down
        # self._teardown()

    # --------------------------------------------------------------------------
    # Private methods
    # --------------------------------------------------------------------------

    # NB: these are the main steps, called in order from main()

    # # --------------------------------------------------------------------------
    # # Boilerplate to use at the start of main
    # # --------------------------------------------------------------------------
    # def _setup(self):
    #     """
    #     Boilerplate to use at the start of main

    #     Perform some mundane stuff like running the arg parser and loading
    #     config files.
    #     """

    # # --------------------------------------------------------------------------
    # # Boilerplate to use at the end of main
    # # --------------------------------------------------------------------------
    # def _teardown(self):
    #     """
    #     Boilerplate to use at the end of main

    #     Perform some mundane stuff like saving config files.
    #     """

    # --------------------------------------------------------------------------
    # Run the program after installing
    # --------------------------------------------------------------------------
    def _do_run(self):
        """
        Run the program after installing
        """

        # show some text
        print(self.S_MSG_RUN.format(self.S_PRG_NAME), end="", flush=True)

        # run program
        try:
            cp = subprocess.run(
                self.S_PRG_NAME,
                check=True,
                shell=True,
                capture_output=True,
                text=True,
            )

            # show some text
            print(cp.stdout)
            print(cp.stderr)

            print(self.S_MSG_DONE, end="", flush=True)

        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            print(self.S_MSG_FAIL, end="", flush=True)
            print(e)


# ------------------------------------------------------------------------------
# Code to run when called from command line
# ------------------------------------------------------------------------------
if __name__ == "__main__":

    # Code to run when called from command line

    # This is the top level code of the program, called when the Python file is
    # invoked from the command line.

    # create a new instance of the main class
    inst = CNPostInstall()

    # run the instance
    inst.main()


# -)
