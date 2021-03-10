from aws_cdk import (
    core,
)

from app_stack.infra_stack import InfraStack

class InfraStage(core.Stage):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        infra_stack = InfraStack(self, 'infra')
