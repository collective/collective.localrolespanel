# -*- coding: utf-8 -*-
#
# File: test_setup.py
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


import unittest

from zope import interface
from zope import component

from Products.CMFCore.utils import getToolByName

from collective.localrolespanel.tests.base import TestCase


from collective.localrolespanel.interfaces import IStdLocalRoles
from collective.localrolespanel.interfaces import StdLocalRolesError

class TestStdLocalRoles(TestCase):

    def afterSetUp(self):
        self.folder.invokeFactory("Document", "testcontext")
        self.testcontext = self.folder.testcontext
        self.portal.acl_users._doAddUser('testuser', 'secret', [], [])

    def test_utility_registered(self):
        rolesapi = component.getUtility(IStdLocalRoles)
        self.failUnless(IStdLocalRoles.providedBy(rolesapi))

    def test_addRole(self):
        rolesapi = component.getUtility(IStdLocalRoles)
        rolesapi.addRole(self.testcontext, 'testuser', 'Reader')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Reader',))
        rolesapi.addRole(self.testcontext, 'testuser', 'Member')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Reader', 'Member'))
        rolesapi.addRole(self.testcontext, 'testuser', 'Reader')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Reader', 'Member'))

    def test_addRole_unknown_principal(self):
        rolesapi = component.getUtility(IStdLocalRoles)
        self.failUnlessRaises(StdLocalRolesError, rolesapi.addRole, self.testcontext, 'unknownuser', 'Reader')

    def test_addRole_unknown_role(self):
        rolesapi = component.getUtility(IStdLocalRoles)
        self.failUnlessRaises(StdLocalRolesError, rolesapi.addRole, self.testcontext, 'testuser', 'unknownrole')

    def test_removeRole(self):
        rolesapi = component.getUtility(IStdLocalRoles)
        rolesapi.addRole(self.testcontext, 'testuser', 'Reader')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Reader',))
        rolesapi.addRole(self.testcontext, 'testuser', 'Member')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Reader', 'Member'))
        rolesapi.removeRole(self.testcontext, 'testuser', 'Reader')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ('Member',))
        rolesapi.removeRole(self.testcontext, 'testuser', 'Member')
        self.assertEquals(self.testcontext.get_local_roles_for_userid(userid='testuser'), ())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestStdLocalRoles))
    return suite

# vim: set ft=python ts=4 sw=4 expandtab :
