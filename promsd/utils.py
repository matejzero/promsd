import config as config
from promsd.models import Target
from promsd.log import logger
from flask import abort
from yaml import dump
import os


def generate_targets_yaml():
    """ Generate and write YAML files for ingestion by Prometheus file SD. """
    targets = {}

    yaml_dir = os.path.join(config.PROMETHEUS_YAML_DIR)

    if not os.path.isdir(yaml_dir):
        try:
            os.makedirs(yaml_dir, 0o755)
        except os.error:
            logger.critical("Prometheus YAML directory can't be created.")


    for target in Target.select():
        # Create required label
        labels = {"job": target.job.name}

        # Add other labels if present
        for label in target.labels:
            labels[label.label] = label.value
            # labels.append({label.label: label.value})

        # Generate configuration for single target
        single_target = {
            "targets": [target.host + ":" + str(target.job.port)],
            "labels": labels}

        # Append target to job's array, so we can dump same jobs to same file: {"job": [target1, target2,...]...}
        targets.setdefault(target.job.name, []).append(single_target)


    # Get a list of all YAML files, so we can remove unchanged ones.
    f_to_delete = [f for f in os.listdir(yaml_dir) if os.path.isfile(os.path.join(yaml_dir, f))]

    # Create YAML files for prometheus file SD
    for k, v in targets.items():
        file_path = os.path.join(yaml_dir, k + ".yaml")
        try:
            file = open(file_path, "w")
        except FileNotFoundError:
            logger.error("Could not save YAML files. Folder '{}' doesn't exists.".format(config.PROMETHEUS_YAML_DIR))
            abort(500)
        except PermissionError:
            logger.error("Could not write to file '{}'.".format(file_path))
            abort(500)
        except:
            logger.info("Unexpected error:", exc_info=True)
            abort(500)
        file.write(dump(v, default_flow_style=False))
        file.close()

        # If file was modified, remove it from array. Pass if file is not in array (new file).
        try:
            f_to_delete.remove(k + ".yaml")
        except ValueError:
            pass

    # If we still have files in array, remove them because they are empty
    if len(f_to_delete) > 0:
        for f_delete in f_to_delete:
            os.remove(os.path.join(yaml_dir, f_delete))

    logger.info("YAML files generated in '{}'".format(os.path.abspath(config.PROMETHEUS_YAML_DIR)))


def create_labels_hash(labels):
    """Merge all labels into a hash."""
    lh = {}
    for label in labels:
        lh[label.label] = label.value
    return lh

def validate_document(document):
    """Check if received document is valid for ingestion."""

    # Fail if not sent in JSON format
    if not document:
        logger.debug("Received document was invalid.")
        abort(400)

    # Fail if missing required fields
    if 'target' not in document:
        logger.debug("Request is missing a target field.")
        abort(422, 'Request is missing a target field.')
    if 'job' not in document:
        logger.debug("Request is missing a job field.")
        abort(422, 'Request is missing a job field.')

    # Fail if labels not dict
    if 'labels' in document:
        if not isinstance(document['labels'], dict):
            logger.debug("Request doesn't have labels in array.")
            abort(422, 'Labels should be passed as an array.')
