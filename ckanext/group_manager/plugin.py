import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckanext.group_manager.controller as controller

class GroupManagerPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)
    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'group-manager')

    def get_auth_functions(self):
        return

    def after_map(self, map):
        #GroupManager
        map.connect(
            '/group/{id}/tag',
            controller='ckanext.group_manager.controller:GroupManager',
            action='index'
        )
        map.connect(
            '/group/tag/{group_id}/{package_id}',
            controller='ckanext.group_manager.controller:GroupManager',
            action='tagPackage'
        )
        return map 
