import collections
import logging

from ckan.lib.base import (BaseController, c, g, render, request, response, abort)
import ckan.model as model
import ckan.lib.helpers as h
import ckan.new_authz as new_authz
import ckan.logic as logic
import ckan.lib.plugins

get_action = logic.get_action

lookup_group_plugin = ckan.lib.plugins.lookup_group_plugin

class GroupManager(BaseController):

    group_type = 'group'

    def _get_group_type(self, id):
        """
        Given the id of a group it determines the type of a group given
        a valid id/name for the group.
        """
        group = model.Group.get(id)
        if not group:
            return None
        return group.type

    def _db_to_form_schema(self, group_type=None):
        '''This is an interface to manipulate data from the database
        into a format suitable for the form (optional)'''
        return lookup_group_plugin(group_type).db_to_form_schema()

    def _action(self, action_name):
        ''' select the correct group/org action '''
        return get_action(self._replace_group_org(action_name))

    def _replace_group_org(self, string):
        ''' substitute organization for group if this is an org'''
        if self.group_type == 'organization':
            string = re.sub('^group', 'organization', string)
        return string

    def index(self, id):
        group_type = self._get_group_type(id.split('@')[0])
        if group_type != self.group_type:
            abort(404, _('Incorrect group type'))

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True}
        data_dict = {'id': id}

        # unicode format (decoded from utf8)
        q = c.q = request.params.get('q', '')

        try:
            # Do not query for the group datasets when dictizing, as they will
            # be ignored and get requested on the controller anyway
            data_dict['include_datasets'] = False
            c.group_dict = self._action('group_show')(context, data_dict)
            c.group = context['group']
        except NotFound:
            abort(404, _('Group not found'))
        except NotAuthorized:
            abort(401, _('Unauthorized to read group %s') % id)

        #self._read(id, limit)
        return render('group_manager/index.html')

    def _read(self, id, limit):
        ''' This is common code used by both read and bulk_process'''
        group_type = self._get_group_type(id.split('@')[0])
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type=group_type),
                   'for_view': True, 'extras_as_string': True}

        q = c.q = request.params.get('q', '')
        # Search within group
        if c.group_dict.get('is_organization'):
            q += ' owner_org:"%s"' % c.group_dict.get('id')
        else:
            q += ' groups:"%s"' % c.group_dict.get('name')

        c.description_formatted = h.render_markdown(c.group_dict.get('description'))

        context['return_query'] = True

        # c.group_admins is used by CKAN's legacy (Genshi) templates only,
        # if we drop support for those then we can delete this line.
        c.group_admins = new_authz.get_group_or_org_admin_ids(c.group.id)

        page = self._get_page_number(request.params)

        # most search operations should reset the page counter:
        params_nopage = [(k, v) for k, v in request.params.items()
                         if k != 'page']
        sort_by = request.params.get('sort', None)

