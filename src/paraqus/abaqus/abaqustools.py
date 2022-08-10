# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan and Stollberg
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
Helper functions/types to read results from abaqus odbs.

All of these can only be executed in abaqus python.

"""
import os.path
from abaqus import session

class ODBObject(object):
    """
    Context manager for Abaqus odb objects.

    Opens an odb and closes it after we are done with it. If any exceptions
    are raised while the odb is open, it is still closed afterwards.

    The optional argument `readonly` can be set to ``False`` to be able to
    write to the odb.

    """

    def __init__(self, file_name, readonly=True):
        self.file_path = os.path.abspath(file_name)
        self.readonly = readonly
        self.already_open = False

    def __enter__(self):

        # make sure to compare with absolute paths
        keys = [os.path.abspath(k) for k in session.odbs.keys()]

        # if the odb is already open, just return the odb object
        if self.file_path in keys:
            # odb is already open
            self.already_open = True
            return session.odbs[self.file_path]

        # otherwise, open it and return the object
        upgrade_odb(self.file_path)
        odb = session.openOdb(name=self.file_path, readOnly=self.readonly)

        # deal with silent errors in the readonly status, this happens e.g.
        # when a lock file prevents write access
        assert odb.isReadOnly == self.readonly, \
            "The odb could not be opened with option readonly=%s" % self.readonly

        self.odb = odb

        return odb

    def __exit__(self, type, value, traceback):
        # only close the odb if it was not open before we "opened" it
        if not self.already_open:
            self.odb.close()


def upgrade_odb(odb_file):
    """
    Upgrade an odb if necessary.

    A subfolder is created for the original odb files if an upgrade is
    performed.

    Parameters
    ----------
    odb_file : str
        Path to the Abaqus .odb

    Returns
    -------
    bool
        Whether the odb was updated.

    """
    import os
    import shutil
    from abaqus import session

    upgrade_required = session.isUpgradeRequiredForOdb(odb_file)

    if upgrade_required:
        # make sure we work with absolute paths
        odb_file = os.path.abspath(odb_file)

        # create new directory for upgraded files
        new_directory = os.path.join(os.path.dirname(odb_file),
                                    "odbs_before_upgrades")

        if not os.path.isdir(new_directory):
            os.mkdir(new_directory)

        backup_file_name = os.path.basename(odb_file)

        backup_file_path = os.path.join(new_directory, backup_file_name)

        # move the original odb to the backup folder
        shutil.move(odb_file, backup_file_path)

        # upgrade the odb file
        session.upgradeOdb(existingOdbPath=backup_file_path,
                           upgradedOdbPath=odb_file)

        print("The odb file '%s' has been updated." % odb_file)
        print("The original file has been stored in the path '%s'"
              % backup_file_path)

        return True

    else:
        return False

