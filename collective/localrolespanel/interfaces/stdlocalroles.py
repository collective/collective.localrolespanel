# -*- coding: utf-8 -*-
#
# File: .py
#
# Copyright (c) InQuant GmbH
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

__author__ = """Hans-Peter Locher <hans-peter.locher@inquant.de>"""
__docformat__ = 'plaintext'


from zope.interface import Interface

class StdLocalRolesError(Exception):
    __doc__ = """Error in IStdLocalRoles utility"""

class IStdLocalRoles(Interface):
    """ API for Plone std local roles
    """

    def validate_parameters(self, context, principal_id, role):
        """validates given parameters, raises an StdLocalRolesError
           with msg if not valid, otherwise returns True
        """

    def addRole(context, principal_id, role):
        """Adds the specified role to the context for principal_id
           returns True or raises an StdLocalRolesError
        """

    def removeRole(context, principal_id, role):
        """Removes the specified role from the context for principal_id
           returns True or raises an StdLocalRolesError
        """

# vim: set ft=python ts=4 sw=4 expandtab :
