import aws_cdk as core
import aws_cdk.assertions as assertions

from qr_generator.qr_generator_stack import QrGeneratorStack


# example tests. To run these tests, uncomment this file along with the example
# resource in qr_generator/qr_generator_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = QrGeneratorStack(app, "qr-generator")
    assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
