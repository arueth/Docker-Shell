from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.cp.docker.docker_shell import DockerShell

class DockerShellDriver(ResourceDriverInterface):
    def __init__(self):
        self.docker_shell = DockerShell()
        return

    def initialize(self, context):
        """
        Initialize the driver session, this function is called everytime a new instance of the driver is created
        This is a good place to load and cache the driver configuration, initiate sessions etc.
        :param InitCommandContext context: the context the command runs on
        """
        return

    def cleanup(self):
        """
        Destroy the driver session, this function is called everytime a driver instance is destroyed
        This is a good place to close any open sessions, finish writing to log files
        """
        return

    def deploy_container(self, context, request, cancellation_context, something_else):
        return self.docker_shell.deploy_container(context, request, cancellation_context, something_else)

    def destroy_vm_only(self, context, ports):
        return self.docker_shell.container_rm(context)

    def get_inventory(self, context):
        return AutoLoadDetails([], [])

    def PowerCycle(self, context, ports, delay):
        pass

    def PowerOff(self, context, ports):
        return self.docker_shell.power_off(context)

    def PowerOn(self, context, ports):
        return self.docker_shell.power_on(context)
