# hydra

This repo hooks into Mythic's eventing system and allows you to dynamically upload new scripts and register eventing functions to call.

## Usage

Add any python file you want to execute to the Hydra folder either on disk or through the Mythic UI by clicking the paperclip icon next to the hydra consuming service.
These Python files should have any imports needed by your script and an `async` function (any name) that matches with the eventing function you're wanting to support.
The following sections have examples of functions and their function definitions you can include in your file. 
You can include as many functions as you want in a single file and call as many helper functions as you want.

### Scripting
Since you're already executing in Python and the `mythic` scripting PyPi package is already installed, you can freely call anything from Mythic's scripting as well.
There's no need to hardcode any credentials into your script though - you can get a per-step API token right from Mythic! Simply include in your `Inputs` an entry like:
```text
myToken: mythic.apitoken
```
and you can access it via `msg.Inputs["myToken"]` to get the `apitoken` to use in your `await mythic.login(apitoken=msg.Inputs["myToken"])` style call.

## Accessing Custom Functions

You can reference any of these specific functions as part of you eventing scripts by calling out the `custom_filename` and `custom_function` you want to execute as part of the `Input` field in a step.

### Custom Function

This action would allow you, as a step in your workflow, execute arbitrary python / scripting code before the next step runs. If you're wanting to use a `custom_function` script then your function should match:
```python
from mythic_container.EventingBase import *
async def some_name(self, msg: NewCustomEventingMessage) -> NewCustomEventingMessageResponse:
        return NewCustomEventingMessageResponse(Success=True)
```

To test this function in an eventing script, you can do this as follows (assuming you uploaded the python file as `testing.py`):
```yaml
name: testing hydra custom functions
description: testing hydra dynamic capabilities
trigger: manual
trigger_data: {}
environment: {}
keywords: []
run_as: bot
steps:
    - name: print hello
      description: execute testing.py to print hello
      depends_on: []
      action: custom_function
      action_data:
        container_name: hydra
        function_name: execute_script
      environment: {}
      inputs:
        custom_filename: testing.py
        custom_function: some_name
      outputs: {}
```

You will want to specify the `container_name` as `hydra` and the `function_name` (within hydra) as `execute_script`, then your `custom_filename` refers to the python file where your custom function lives and `custom_function` is the name of your function.

### Conditional Check

This action would allow you to programmatically determine if other steps should be skipped or not. If you're wanting to use a `conditional_check` script then your function should match:
```python
from mythic_container.EventingBase import *
async def some_name(msg: ConditionalCheckEventingMessage) -> ConditionalCheckEventingMessageResponse:
    return ConditionalCheckEventingMessageResponse(Success=True)
```

To test this function in an eventing script, you can do this as follows (assuming you uploaded the python file as `testing.py`):
```yaml
name: testing hydra conditionals
description: testing hydra dynamic capabilities
trigger: manual
trigger_data: {}
environment: {}
keywords: []
run_as: bot
steps:
  - name: skip me
    description: skip me bro, i dare you
    depends_on:
      - skip steps
    action: task_create
    action_data:
      callback_display_id: "1"
      command_name: shell
      params: whoami
      params_dictionary: {}
      payload_type: apollo
    environment: {}
    inputs: {}
    outputs: {}
  - name: skip steps
    description: should skip steps?
    depends_on: []
    action: conditional_check
    action_data:
      container_name: hydra
      function_name: conditional_check
      steps:
        - skip me
    environment: {}
    inputs:
      custom_filename: testing.py
      custom_function: some_name
    outputs: {}
```

You will want to specify the `container_name` as `hydra` and the `function_name` (within hydra) as `execute_script`, then your `custom_filename` refers to the python file where your custom function lives and `custom_function` is the name of your function.

### Task Intercept

This action would allow you to programmatically intercept _ALL_ tasking for the operation and optionally block it from executing. If you're wanting to use a `task_intercept` script then your function should match:
```python
from mythic_container.EventingBase import *
async def some_name(msg: TaskInterceptMessage) -> TaskInterceptMessageResponse:
    return TaskInterceptMessageResponse(Success=True, TaskID=msg.TaskID, BlockTask=False)
```
To test this function in an eventing script, you can do this as follows (assuming you uploaded the python file as `testing.py`):
```yaml
name: testing hydra task intercepts
description: testing hydra dynamic capabilities
trigger: task_intercept
trigger_data: {}
environment: {}
keywords: []
run_as: bot
steps:
  - name: intercepting
    description: ""
    depends_on: []
    action: task_intercept
    action_data:
      container_name: hydra
    environment: {}
    inputs:
      custom_filename: testing.py
      custom_function: some_name
```

You will want to specify the `container_name` as `hydra`, then your `custom_filename` refers to the python file where your custom function lives and `custom_function` is the name of your function.


### Response Intercept

This action would allow you to programmatically intercept _ALL_ output that the user would see from tasking and optionally modify it before saving it to the database. If you're wanting to use a `response_intercept` script then your function should match:
```python
from mythic_container.EventingBase import *
async def some_name(msg: ResponseInterceptMessage) -> ResponseInterceptMessageResponse:
    return ResponseInterceptMessageResponse(Response=msg.Environment["user_output"])
```

To test this function in an eventing script, you can do this as follows (assuming you uploaded the python file as `testing.py`):
```yaml
name: testing hydra response intercepts
description: testing hydra dynamic capabilities
trigger: response_intercept
trigger_data: {}
environment: {}
keywords: []
run_as: bot
steps:
  - name: intercepting
    description: ""
    depends_on: []
    action: response_intercept
    action_data:
      container_name: hydra
    environment: {}
    inputs:
      custom_filename: testing.py
      custom_function: some_name
```

You will want to specify the `container_name` as `hydra`, then your `custom_filename` refers to the python file where your custom function lives and `custom_function` is the name of your function.


## Installation
To install hydra, you'll need Mythic installed on a remote computer. You can find installation instructions for Mythic at the [Mythic project page](https://github.com/its-a-feature/Mythic/).

From the Mythic install directory, use the following command to install Apollo as the **root** user:

```
./mythic-cli install github https://github.com/MythicAgents/hydra
```

From the Mythic install directory, use the following command to install hydra as a **non-root** user:

```
sudo -E ./mythic-cli install github https://github.com/MythicAgents/hydra
```