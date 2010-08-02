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

    label = _(u'heading_local_roles_settings',
              default=u'Local Roles Settings')
    description = _(u'help_local_roles_settings',
            default=u"""<p>Set or Remove local roles for objects using csv. 
                        The format of the csv file should be:</p>
                        <pre>path,user-/group-id,role</pre>
                        <p>The data gets processed line by line. At the end, 
                        you'll get a notification on the number of successfully processed lines 
                        as well as verbose error notifications for each unsuccessful
                        line. Be patient! The duration of the process depends on the number of lines of your csv 
                        and may take up to several minutes.</p>
                        <p>Example csv:</p>
                        <pre>
                        /plone/front-page,Reviewers,Editor
                        /plone/front-page,usera,Contributor
                        /plone/news,userb,Reviewer
                        /plone/news,userb,Editor
                        </pre>
                     """)
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


    @formlib.action(_(u'label_set_roles', default=u'Set Roles'),
                 validator='validate_csv', name=u'Set Roles')
    def action_set_roles(self, action, data):
        """ handle set roles
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

        msg = "Successfully set Roles for %s Lines" % str(success)
        if errors:
            self._add_status_message(msg)

            for e in errors:
                self._add_status_message(str(e), severity="error")
        else:
            self._add_status_message(msg)

        self._redirect_back_to(url="/@@localroles-controlpanel")


    @formlib.action(_(u'label_delete_roles', default=u'Delete Roles'),
                 validator='validate_csv', name=u'Delete Roles')
    def action_delete_roles(self, action, data):
        """ handle delete roles
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
