import logging
import os
import yaml

from galaxy.tools import GALAXY_LIB_TOOLS_UNVERSIONED
from galaxy.jobs import JobDestination

log = logging.getLogger(__name__)

CONTAINER_RULE_MAPPER_FILE = os.path.join(
    os.path.dirname(__file__), 'container-mapper-rules.yml')


def _load_container_mappings():
    if os.path.exists(CONTAINER_RULE_MAPPER_FILE):
        with open(CONTAINER_RULE_MAPPER_FILE) as f:
            return yaml.load(f)
    else:
        return {}


CONTAINER_RULE_MAP = _load_container_mappings()


def _apply_rule_mappings(tool, params):
    if CONTAINER_RULE_MAP:
        for mapping in CONTAINER_RULE_MAP.get('mappings', {}):
            if tool.id in mapping.get('tool_ids'):
                params.update(mapping.get('container'))
                return True
    return False


def k8s_container_mapper(tool, referrer, k8s_runner_id="k8s"):
    params = dict(referrer.params)
    params['docker_enabled'] = True
    if not _apply_rule_mappings(tool, params):
        if tool.id in GALAXY_LIB_TOOLS_UNVERSIONED:
            default_container = params.get('docker_default_container_id')
            if default_container:
                params['docker_container_id_override'] = default_container
    log.debug("[k8s_container_mapper] Dispatching to %s with params %s" % (k8s_runner_id, params))
    return JobDestination(runner=k8s_runner_id, params=params)
