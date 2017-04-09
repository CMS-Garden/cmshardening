# noinspection PyPackageRequirements
from astroid import MANAGER
# noinspection PyPackageRequirements
from astroid import scoped_nodes
from hardening import utils


def register(_):
    pass


def transform(cls):
    if cls.name == 'HardeningUtil':
        settings = utils.ModuleSettings()
        cls = settings(cls)
    return cls


MANAGER.register_transform(scoped_nodes.Class, transform)
