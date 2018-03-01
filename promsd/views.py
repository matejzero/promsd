import logging
from promsd.log import logger
from promsd.models import Target, Job, Label, db
from promsd.utils import generate_targets_yaml, create_labels_hash, validate_document
from flask import jsonify, Blueprint, request, abort
from peewee import IntegrityError

target_blueprint = Blueprint('target', __name__)


@target_blueprint.route('/api/v1/targets/', methods=['GET'])
def get_targets():
    """Returns all targets."""

    logger.info("GET: path={}, client={}".format(request.path, request.remote_addr))

    targets = []
    for target in Target.select():

        # Add target to array, so we can return an array of all targets.
        targets.append({
            "id": target.id,
            "target": target.host,
            "job": target.job.name,
            "labels": create_labels_hash(target.labels)
        })

    logger.debug("Showing all targets.")
    return jsonify(targets), 200


@target_blueprint.route('/api/v1/targets/<int:target_id>/', methods=['GET'])
def get_single_targets(target_id):
    """Returns a single target."""

    logger.info("GET: path={}, client={}, target_id={}".format(request.path, request.remote_addr, target_id))

    try:
        tg_entry = Target.get(Target.id == target_id)
    except Target.DoesNotExist:
        abort(404, "Target with this ID doesn't exists.")

    target = {"id": tg_entry.id,
              "target": tg_entry.host,
              "job": tg_entry.job.name,
              "labels": create_labels_hash(tg_entry.labels)
              }

    logger.debug("Showing target ID {}.".format(tg_entry.id))
    return jsonify(target)


@target_blueprint.route('/api/v1/targets/', methods=['POST'])
def create_target():
    """
    Creates a new target.
    ---
    tags:
      - targets
    definitions:
      - schema:
          id: Target
          properties:
            target:
             type: string
            job:
             type: string
            labels:
              type: hash
              items:
                $ref: "#/definitions/Label"
          id: Label
          properties:
            target_id:
              type: integer
            label:
              type: string
            value:
              type: string

    # parameters:
    #   - in: body
    #     name: body
    #     schema:
    #       id: Target
    #       required:
    #         - target
    #         - job
    #       properties:
    #         target:
    #           type: string
    #           description: target's fqdn
    #         job:
    #           type: string
    #           description: exporter's name
    #         labels:
    #           type: object
    #           properties:
    #             label_name:
    #               type: string
    #           description: list of labels
    responses:
      201:
        description: Target created
      400:
        description: Mailformed JSON, labels not array or missing field.
    """

    document = request.json

    logger.info("POST: path={}, client={}".format(request.path, request.remote_addr))
    logger.debug("POST: document={}".format(document))

    # Check if we received a valid document and fail with error message.
    validate_document(document)

    # Check if this target/job pair already exists
    target_exists = Target.select().where(
        Target.host == document['target'],
        Target.job == Job.select().where(Job.name == document['job'])
    ).exists()
    if target_exists:
        logger.debug("Target {} exists.".format(document['target']))
        abort(409, 'This target already exists. If you want to modify it, use PUT request.')

    # Get job object
    job = Job.get(Job.name == document['job'])

    # Create target
    target = Target.create(host=document['target'], job=job)

    # Create labels if they are passed in document
    if 'labels' in document:
        for label, value in document['labels'].items():
            Label.create(target=target, label=label, value=value)

    # Generate YAML files
    generate_targets_yaml()

    # Add ID field in returned document.
    document['id'] = target.id

    logger.info("Target '{}' added.".format(target.host))
    return jsonify(document), 201


@target_blueprint.route('/api/v1/targets/<int:target_id>/', methods=['PUT'])
def update_target(target_id):
    """Creates or updates an existing target."""

    document = request.json

    logger.info("PUT: path={}, client={}, ID={}".format(request.path, request.remote_addr, target_id))
    logger.debug("PUT: document={}".format(document))

    # Check if we received a valid document and fail with error message.
    validate_document(document)

    # Update target if it exists, else create it
    if Target.get_or_none(Target.id == target_id):
        logger.debug("Updating record with ID {}".format(target_id))

        # Get target
        target = Target.get(Target.id == target_id)

        # Remove existing labels, will readd them later
        Label.delete().where(Label.target == target_id).execute()

        # Update target
        target.host = document['target']
        target.job = Job.get(Job.name == document['job'])
        target.save()

        # Create labels if they are passed in document
        if 'labels' in document:
            for label, value in document['labels'].items():
                Label.create(target=target, label=label, value=value)

        return_code = 200
        logger.info("Target '{}' updated.".format(target.host))

    else:
        logger.debug("Creating record with ID {}".format(target_id))

        # Create new target
        target = Target.create( id=target_id,
                                host=document['target'],
                                job=Job.get(Job.name == document['job']))

        # Create labels if they are passed in document
        if 'labels' in document:
            for label, value in document['labels'].items():
                Label.create(target=target, label=label, value=value)

        return_code = 201
        logger.info("Target '{}' created.".format(target.host))

    # Generate YAML files
    generate_targets_yaml()

    # Add ID field in returned document.
    document['id'] = target.id

    # Return document with correct return code based on event (update or create)
    return jsonify(document), return_code


@target_blueprint.route('/api/v1/targets/<int:target_id>/', methods=['DELETE'])
def delete_target(target_id):
    """Removes a target."""

    logger.info("DELETE: path={}, client={}, ID={}".format(request.path, request.remote_addr, target_id))

    try:
        target = Target.get(Target.id == target_id)
    except Target.DoesNotExist:
        abort(404, "Target with this ID doesn't exists.")

    target.delete_instance(recursive=True)

    # Generate YAML files
    generate_targets_yaml()

    logger.info("Target ID {} deleted.".format(target.id))
    return '', 204
