# -*- coding: utf-8 -*-
#
# File: localroles_controlpanel.py
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

__author__ = 'Ramon Bartl <ramon.bartl@inquant.de>'
__docformat__ = 'plaintext'

import csv
import logging
from StringIO import StringIO

from zope import schema
from zope import component
from zope import interface
from zope.formlib import form as formlib

from plone.protect import CheckAuthenticator
from plone.app.form.validators import null_validator
from Products.Five.formlib.formbase import PageForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from collective.localrolespanel.interfaces import IStdLocalRoles
from collective.localrolespanel.interfaces import StdLocalRolesError

from collective.localrolespanel import localrolespanelMessageFactory as _

DELIMITER = ","
logger = logging.getLogger("localroles_controlpanel")


class ILocalRoleSettings(interface.Interface):
    """ Local Roles Bulk Settings
    """

    csv_file = schema.Bytes(title=_(u'label_csv_file',
                                    default=_(u'Select CSV file')),
                        description=_(u'help_csv_file',
                                      default=u'Select a CSV File'),
                        required=True)


class LocalRolesControlPanel(PageForm):
    """ Local roles control panel for bulk settings
    """

    template = ViewPageTemplateFile('localroles_controlpanel_form.pt')

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.utility = component.getUtility(IStdLocalRoles)


    def validate_csv(self, action, data):
        """ csv validation
        """
        # CSRF protection
        CheckAuthenticator(self.request)


    @property
    def form_fields(self):
        """ Form Fields
            see: ILocalRoleSettings
        """
        return formlib.Fields(ILocalRoleSettings)


    @formlib.action(_(u'label_add_roles', default=u'Add Roles'),
                 validator='validate_csv', name=u'Add Roles')
    def action_add_roles(self, action, data):
        """ handle add roles
        """
        errors = []
        success = 0

        csv_file = StringIO(data["csv_file"])
        reader = csv.reader(csv_file, delimiter=DELIMITER)

        for num, row in enumerate(reader):
            if len(row) != 3:
                errors.append("Line %(num)s, %(row)s, Invalid line" % locals())
                continue

            try:
                content_item = self.context.unrestrictedTraverse(row[0])
            except KeyError, e:
                errors.append("Line %(num)s, %(row)s, Object not found" % locals())
                continue

            try:
                self.utility.addRole(content_item, row[1], row[2])
                success += 1
            except StdLocalRolesError, e:
                errors.append("Line %(num)s, %(row)s, %(e)s" % locals())

        msg = "Successfully added Roles for %s Lines" % str(success)
        if errors:
            self._add_status_message(msg)

            for e in errors:
                self._add_status_message(str(e), severity="error")
        else:
            self._add_status_message(msg)

        self._redirect_back_to(url="/@@localroles-controlpanel")


    @formlib.action(_(u'label_remove_roles', default=u'Remove Roles'),
                 validator='validate_csv', name=u'Remove Roles')
    def action_remove_roles(self, action, data):
        """ handle remove roles
        """
        errors = []
        success = 0

        csv_file = StringIO(data["csv_file"])
        reader = csv.reader(csv_file, delimiter=DELIMITER)

        for num, row in enumerate(reader):
            if len(row) != 3:
                errors.append("Line %(num)s, %(row)s, Invalid line" % locals())
                continue

            try:
                content_item = self.context.unrestrictedTraverse(row[0])
            except KeyError, e:
                errors.append("Line %(num)s, %(row)s, Object not found" % locals())
                continue

            try:
                self.utility.removeRole(content_item, row[1], row[2])
                success += 1
            except StdLocalRolesError, e:
                errors.append("Line %(num)s, %(row)s, %(e)s" % locals())

        msg = "Successfully removed Roles for %s Lines" % str(success)

        if errors:
            self._add_status_message(msg)
            for e in errors:
                self._add_status_message(str(e), severity="error")
        else:
            self._add_status_message(msg)

        self._redirect_back_to(url="/@@localroles-controlpanel")


    @formlib.action(_(u'label_cancel', default=u'Cancel'),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        """ Cancel Action
            -> redirects to plone_control_panel
        """
        self._add_status_message("No Changes made")
        self._redirect_back_to(url="/plone_control_panel")


    def _add_status_message(self, msg, severity="info"):
        """ append a status message
        """
        IStatusMessage(self.request).addStatusMessage(msg, severity)


    def _redirect_back_to(self, url=""):
        """ redirect to url
        """
        context_url = component.getMultiAdapter((self.context, self.request),
                name='absolute_url')()
        self.request.response.redirect(context_url + url)

# vim: set ft=python ts=4 sw=4 expandtab :
