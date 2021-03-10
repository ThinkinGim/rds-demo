from aws_cdk import (
    core,
    aws_ec2,
    aws_iam,
    aws_lambda as _lambda,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    pipelines,
)

from .stages import InfraStage

class CdkPipelineStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, params: dict, **kwargs):
        super().__init__(scope, id, **kwargs)

        source_artifact = codepipeline.Artifact()
        cloud_assembly_artifact = codepipeline.Artifact()

        pipeline = pipelines.CdkPipeline(self, 'CdkPipeline', 
            cloud_assembly_artifact=cloud_assembly_artifact,
            pipeline_name=params['pipeline_name'],            
            source_action=cpactions.BitBucketSourceAction(
                action_name='GithubAction',
                output=source_artifact,
                connection_arn=params['connection_arn'],
                owner=params['github_owner'],
                repo=params['github_repo'],
                branch=params['github_branch']
            ),
            synth_action=pipelines.SimpleSynthAction(
                source_artifact=source_artifact,
                cloud_assembly_artifact=cloud_assembly_artifact,
                role_policy_statements=[
                    aws_iam.PolicyStatement(
                        actions=["secretsmanager:GetSecretValue"],
                        resources=[params['secret_arn']]
                    )
                ],
                install_command='npm install -g aws-cdk && pip install --upgrade pip && pip install -r requirements.txt',
                synth_command="cdk synth -v -c region=%s -c secret_name=%s"%(params['region'],params['secret_name']),
            )
        )

        stage_deploy = pipeline.add_application_stage(InfraStage(self, 'rds-demo'))

        # stage_deploy.add_actions(
        #     pipelines.ShellScriptAction(
        #         action_name='InitDatabase',
        #         run_order=stage_deploy.next_sequential_run_order(),
        #         additional_artifacts=[source_artifact],
        #         commands=[
        #             "aws lambda invoke --function-name demo-rds_func_init_db --log-type Tail --query 'StatusCode' --output json out.json",
        #         ],
        #     )
        # )
