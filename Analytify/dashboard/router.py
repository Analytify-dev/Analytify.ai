class DatabaseRouter:
    """
    A router to control all database operations on models in the
    dashboard, quickbooks, and sample applications.
    """

    def db_for_read(self, model, **hints):
        """Direct read operations to the appropriate database."""
        if model._meta.app_label in ['dashboard', 'quickbooks']:
            return 'default'
        elif model._meta.app_label == 'sample':
            return 'example'
        return None

    def db_for_write(self, model, **hints):
        """Direct write operations to the appropriate database."""
        if model._meta.app_label in ['dashboard', 'quickbooks']:
            return 'default'
        elif model._meta.app_label == 'sample':
            return 'example'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in one of the apps is involved."""
        if (
            obj1._meta.app_label in ['dashboard', 'quickbooks', 'sample'] or
            obj2._meta.app_label in ['dashboard', 'quickbooks', 'sample']
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the dashboard and quickbooks apps only appear in the 'default' database."""
        if app_label in ['dashboard', 'quickbooks']:
            return db == 'default'
        elif app_label == 'sample':
            return db == 'example'
        return None
