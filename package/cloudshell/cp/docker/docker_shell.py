import jsonpickle

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.cp.docker.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.docker.domain.context.docker_shell_context import DockerShellContext
from cloudshell.cp.docker.domain.services.parsers.command_results_parser import CommandResultsParser
from cloudshell.cp.docker.domain.services.parsers.docker_models_parser import DockerModelsParser
from cloudshell.cp.docker.domain.services.session_providers.docker_session_provider import DockerSessionProvider
from cloudshell.cp.docker.models.deploy_result import DeployResult
from cloudshell.cp.docker.models.prepare_connectivity_action_result import PrepareConnectivityActionResult
from docker.errors import NotFound as DockerNotFoundException


class DockerShell:
    def __init__(self):
        self.command_result_parser = CommandResultsParser()
        self.docker_session_manager = DockerSessionProvider()
        self.model_parser = DockerModelsParser()

        return

    def get_inventory(self, context):
        return

    def container_rm(self, command_context):
        with DockerShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                shell_context.logger.info('Removing Container - %s' % data_holder.vmdetails.uid)

                try:
                    container = shell_context.docker_api.dockerd_client.containers.get(container_id=data_holder.vmdetails.uid)
                    container.remove(force=True)
                except DockerNotFoundException as e:
                    shell_context.logger.warn("Attempting to remove container '%s' that does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

        return True

    def deploy_container(self, command_context, deployment_request, cancellation_context, something_else):
        with DockerShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Deploying Container')

                reservation_id = command_context.reservation.reservation_id[-12:]

                container_run_args = {'detach': True}

                docker_container_deployment_model = self.model_parser.convert_to_deployment_resource_model(deployment_request)
                container_name = "cs_%s.%s" % (reservation_id, docker_container_deployment_model.app_name)
                container_run_args['name'] = container_name

                image = docker_container_deployment_model.docker_image
                if docker_container_deployment_model.docker_image_tag:
                    image += ":%s" % docker_container_deployment_model.docker_image_tag
                container_run_args['image'] = image

                command = docker_container_deployment_model.docker_image_command
                if command:
                    container_run_args['command'] = command

                shell_context.logger.debug('Container Run Args: %s' % container_run_args)
                container = shell_context.docker_api.dockerd_client.containers.run(**container_run_args)

                # TODO: Determine if sending back container.attrs is possible
                return DeployResult(vm_name=docker_container_deployment_model.app_name,
                                    vm_uuid=container.id,
                                    cloud_provider_resource_name=docker_container_deployment_model.cloud_provider,
                                    auto_power_off=True,
                                    wait_for_ip=False,
                                    auto_delete=True,
                                    autoload=False,
                                    deployed_app_attributes={},
                                    deployed_app_address=command_context.resource.address)

    def power_off(self, command_context):
        with DockerShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Power Off')

                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                try:
                    container = shell_context.docker_api.dockerd_client.containers.get(container_id=data_holder.vmdetails.uid)
                    container.stop()
                except DockerNotFoundException as e:
                    shell_context.logger.warn("Attempting to stop container '%s' that does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

                shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Offline", "Powered Off")

    def power_on(self, command_context):
        with DockerShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Power On')

                resource = command_context.remote_endpoints[0]

                shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Online", "Active")

    def prepare_connectivity(self, command_context, request, cancellation_context):
        with DockerShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Prepare Connectivity')

                decoded_request = DeployDataHolder(jsonpickle.decode(request))
                prepare_connectivity_request = None
                if hasattr(decoded_request, 'driverRequest'):
                    prepare_connectivity_request = decoded_request.driverRequest
                if not prepare_connectivity_request:
                    raise ValueError('Invalid prepare connectivity request')

                results = []

                result = PrepareConnectivityActionResult()
                result.infoMessage = 'PrepareConnectivity finished successfully'

                results.append(result)

                return self.command_result_parser.set_command_result({'driverResponse': {'actionResults': results}})
        return
