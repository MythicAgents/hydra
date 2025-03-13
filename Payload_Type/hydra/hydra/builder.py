from mythic_container.EventingBase import *
import importlib.util


async def task_intercept(msg: TaskInterceptMessage) -> TaskInterceptMessageResponse:
    logger.info("called task_intercept")
    funcResponse = TaskInterceptMessageResponse(Success=True, TaskID=msg.TaskID, BlockTask=False)
    func = await get_file_and_function(filename=msg.Inputs["filename"], function_name=msg.Inputs["function"])
    if func:
        funcResponse.StdOut = "found the function"
        funcResponse = await func(msg)
    else:
        funcResponse.StdErr = "failed to find the function"
    funcResponse.EventStepInstanceID = msg.EventStepInstanceID
    logger.info("returning from task_intercept")
    return funcResponse


async def response_intercept(msg: ResponseInterceptMessage) -> ResponseInterceptMessageResponse:
    logger.info("called response_intercept")
    funcResponse = ResponseInterceptMessageResponse(Response=msg.Environment["user_output"])
    func = await get_file_and_function(filename=msg.Inputs["filename"], function_name=msg.Inputs["function"])
    if func:
        funcResponse.StdOut = "found the function"
        funcResponse = await func(msg)
    else:
        funcResponse.StdErr = "failed to find the function"
    funcResponse.EventStepInstanceID = msg.EventStepInstanceID
    logger.info("returning from response_intercept")
    return funcResponse


class Hydra(Eventing):
    task_intercept_function = task_intercept
    response_intercept_function = response_intercept

    def __init__(self, **kwargs):
        self.name = "hydra"
        self.description = "Dynamically execute scripts for use with Eventing"
        self.custom_functions = [
            CustomFunctionDefinition(
                Name="execute_script",
                Description="Execute an arbitrary python script as a custom function",
                Function=self.execute_script
            )
        ]
        self.conditional_checks = [
            ConditionalCheckDefinition(
                Name="conditional_check",
                Description="Execute an arbitrary python script for a conditional check",
                Function=self.conditional_check
            )
        ]

    async def on_container_start(self, message: ContainerOnStartMessage) -> ContainerOnStartMessageResponse:
        return ContainerOnStartMessageResponse()

    async def conditional_check(self, msg: ConditionalCheckEventingMessage) -> ConditionalCheckEventingMessageResponse:
        logger.info("called conditional_check")
        funcResponse = ConditionalCheckEventingMessageResponse(Success=False)
        func = await get_file_and_function(filename=msg.Inputs["filename"], function_name=msg.Inputs["function"])
        if func:
            funcResponse.StdOut = "found the function"
            funcResponse = await func(msg)
        else:
            funcResponse.StdErr = "failed to find the function"
        funcResponse.EventStepInstanceID = msg.EventStepInstanceID
        logger.info("returning from conditional_check")
        return funcResponse

    async def execute_script(self, msg: NewCustomEventingMessage) -> NewCustomEventingMessageResponse:
        logger.info("called execute_script")
        funcResponse = NewCustomEventingMessageResponse(Success=False)
        func = await get_file_and_function(filename=msg.Inputs["filename"], function_name=msg.Inputs["function"])
        if func:
            funcResponse.StdOut = "found the function"
            funcResponse = await func(msg)
        else:
            funcResponse.StdErr = "failed to find the function"
        funcResponse.EventStepInstanceID = msg.EventStepInstanceID
        logger.info("returning from execute_script")
        return funcResponse


async def get_file_and_function(filename: str, function_name: str):
    try:
        module_name = filename[:-3]
        file_spec = importlib.util.spec_from_file_location(module_name, filename)
        module = importlib.util.module_from_spec(file_spec)
        file_spec.loader.exec_module(module)
        if function_name in dir(module):
            return getattr(module, function_name)
        else:
            logger.error("found module, but not function")
    except Exception as e:
        logger.error(e)
    return None
