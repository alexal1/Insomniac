from collections import namedtuple

CloneCreationAction = namedtuple('CloneCreationAction', 'user appcloner_host_device')
CloneInstallationAction = namedtuple('CloneCreationAction', 'user target_device profile_status')
CloneRemovalAction = namedtuple('CloneCreationAction', 'user target_device')
AppDataCleanupAction = namedtuple('CloneCreationAction', 'user target_device')
ProfileRegistrationAction = namedtuple('CloneCreationAction', 'user target_device')
