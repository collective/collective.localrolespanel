# -*- coding: utf-8 -*-
#
# File: stdlocalroles.py
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


import logging

from zope import interface
from zope.app.component.hooks import getSite

from interfaces.stdlocalroles import IStdLocalRoles
from interfaces.stdlocalroles import StdLocalRolesError
from Products.CMFCore.utils import getToolByName

LOGGER = logging.getLogger("collective.localrolespanel")

class StdLocalRoles(object):
    """ API for Plone std local roles
    """
    interface.implements(IStdLocalRoles)

    def validate_parameters(self, context, principal_id, role):
        """validates given parameters, raises an StdLocalRolesError
           with msg if not valid, otherwise returns True
        """
        groups = getToolByName(context, "portal_groups")
        users = getToolByName(context, "portal_membership")
        valid_principal_id = groups.getGroupById(principal_id) or users.getMemberById(principal_id)
        if not valid_principal_id:
            msg = "Unknown user/group id: %s" % principal_id
            raise StdLocalRolesError, msg
        valid_roles = context.valid_roles()
        if not role in valid_roles:
            msg = "Unknown role: %s, valid roles are: %s" % (role, valid_roles)
            raise StdLocalRolesError, msg
        return True

    def addRole(self, context, principal_id, role):
        """Adds the specified role to the context for principal_id
           returns True or raises an StdLocalRolesError
        """
        valid = self.validate_parameters(context, principal_id, role)
        if role not in context.get_local_roles_for_userid(userid=principal_id):
            context.manage_addLocalRoles(principal_id, [role])
            context.reindexObjectSecurity()
        return True

    def removeRole(self, context, principal_id, role):
        """Removes the specified role from the context for principal_id
           returns True or raises an StdLocalRolesError
        """
        valid = self.validate_parameters(context, principal_id, role)
        existing = context.get_local_roles_for_userid(userid=principal_id)
        if role in existing:
            kept_roles = [kept_role for kept_role in existing if kept_role != role]
            context.manage_delLocalRoles(userids=[principal_id])
            if len(kept_roles):
                context.manage_addLocalRoles(principal_id, kept_roles)
            context.reindexObjectSecurity()
        return True


# vim: set ft=python ts=4 sw=4 expandtab :
