# cloudify-plugins-tools
(Dependency injection) framework and tools simplifying cloudify plugin development and reducing number of boilerplate code lines

## Example usages

* https://github.com/Cloudify-PS/cloudify-opencontrail-plugin
* https://github.com/Cloudify-PS/cloudify-idirect-plugin

## Common TOSCA model related part (cloudify_plugin_tools)

To develop a plugin it is (often) needed to write many lines of boilerplate code to e.g. merge input arguments from few sources, resolve some arguments using relationships, perform exception handling etc.
Purpose of introducing **cloudify_plugin_tools** package was to implement such *TOSCA-model-related* operations one time and then reuse them for each of *subplugins* making development faster and simpler. 

Main features of framework implemented in **cloudify_plugin_tools** are:
* Merging of input arguments for given operation from few sources like:
    * *properties*
    * *runtime_properties*
    * operation *input arguments*
    * *runtime_properties* of node connected by relationship
* Resolving input arguments using *runtime_properties* (looking for given  *runtime_property* of node having given type connected by relationship with given type)
* Top level exception handling
* Indroducing possibility of doing custom actions with operation method (e.g. calling it many times with different sets of credentials).
* Injecting clients etc. to interact with given API 

#### run_with decorator

Main class exposed by *plugins_common* package is **run_with** decorator class.
It has been designed as a decorator to be used with plugin operations methods.
Example usage is:

```python
@operation
@run_with(
    runner_class=ContrailInstanceTaskRunner,
    input_arguments_sources_order=SOURCES_DEFAULT_ORDER,
    api_ctx_provider_cls=ContrailContextProvider,
    recoverable_exceptions=RECOVERABLE_EXCEPTIONS,
    non_recoverable_exceptions=NON_RECOVERABLE_EXCEPTIONS,
    input_arguments_resolve_rules=[
        InputArgumentResolvingRule(
            argument_name='vn_ref',
            node_type=constants.TYPE_SERVICE,
            runtime_properties_path=[
                constants.RUNTIME_PROPERTY_OBJECT_REFERENCES,
                constants.VIRTUAL_NETWORK_KEYWORD
            ]
        ),
        InputArgumentResolvingRule(
            argument_name='lif_ref',
            node_type=constants.TYPE_SERVICE,
            runtime_properties_path=[
                constants.RUNTIME_PROPERTY_OBJECT_REFERENCES,
                constants.LOGICAL_INTERFACE_KEYWORD
            ]
        )
    ]
)
def create(ctx, api_ctx, vn_ref, lif_ref, some_arg, **kwargs):
    pass  # DO SOMETHING
``` 

Input parameters and their meaning are:
* ***runner_class*** (*mandatory*) - *Runner* class which should be used to execute decorated method
* ***input_arguments_sources_order*** (*optional*) - order of input argument sources, where framework should look for.
* ***api_ctx_provider_cls*** (*optional*) - ApiContextProvider class which should be used to inject ApiContext
* ***recoverable_exceptions*** (*optional*) - list / tuple of exceptions classes which occured during method execution should be treated as recoverable
* ***nonrecoverable_exceptions*** (*optional*) - list / tuple of exceptions classes which occured during method execution should be treated as non-recoverable
* ***input_arguments_resolve_rules*** (*optional*) - list of rules describing which input arguments should be resolved from runtime_properties of other node and how this process should be done 

Basically ***run_with*** decorator uses ***Runner*** class to prepare and execute operation method and parforms top-level exception handling by itself.

***run_with*** class may (should !) be subclassed in each ***xxxxxx_plugin*** package to adjust default decrator arguments to given *subplugin*.

***run_with*** decorator concept can be treated like some kind of **dependency injection framework** dedicated for Cloudify plugin operations methods.


#### InputArgumentResolver

Purpose of introducing ***InputArgumentResolver*** is to enable getting some value as operation method input argument from *runtime_properties* of other node connected by relationship.
Resolver class takes list of ***InputArgumentResolvingRules*** as input argument for constructor.
It exposes ***resolve*** method - which will try to find proper values described by list of rules using ***CloudifyContext*** object as input.

There are two resolvers:
* **InstanceInputArgumentResolver** - it should be used for operations run from ***node instance*** lifecycle interfaces. 
It will try to iterate through all relationships associated with given node instance and check all of them to find proper values descibed by rules.
* **RelationshipInputArgumentResolver** - it should be used for operations run from ***relationship*** lifecycle interfaces. 
It will try to get described by rules values from source and target node instances.  

***InputArgumentResolver*** is used by ***InputArgumentsProvider*** as one of input arguments sources. 

#### InputArgumentResolvingRule

Class dedicated to describe variable which value should be resolved (see above).
It constructor takes 4 arguments:
* **argument_name** - name of variable which value should be resolved
* **node_type** (*optional*) - type of node, which should be check to find value of variable
* **relationship_type** (*optional*) -  type of relationship connecting with node, which should be check to find value of variable
* **runtime_properties_path** - list of keys in *runtime_property* dictionary poining to value

**node_type** and **relationship_type** will be checked only when are specified.
In case of e.g. lack of ***node_type*** - resolver will check all nodes connected by relationships.  

#### InputArgumentProvider

Class dedicated to provide input arguments for operation method execution.
In Cloudify environment - we have few sources of data e.g. *properties*, *runtime_properties*, interface operation *input arguments*.
In many plugins some custom code is needed to merge and provide input arguments from few sources.
This is responsibility of ***InputArgumentProvider***.
Class takes ***InputArgumentResolver*** and list representing order of data sources to be checked as constructor parameters.
For each source in order provider class will try to obtain values from this source (e.g. *properties*) and then merge them to dictionary containing current values.
Class has one public mathod ***get_input_arguments*** takes ***CloudifyContext*** and dict of keyword arguments containing inputs for operation defined in TOSCA.
This method will try to get data from each of data sources defined in *sources_order* constructor parameter, merge all dictionaries and return result.

Currently supportes sources of input parameters are (presented in default order):
* *properties* of *node* currently set in ***CloudifyContext***
* *runtime_properties* of *node instance* currently set in ***CloudifyContext***
* *inputs* for *operation* defined in some *interface* in TOSCA model
* *resolved values* - some key got from *runtime_properties* of other *node instance* connected by *relationship*
 
Methods dedicated to obtain data from each source are defined as lambdas inside ***InputArgumentProvider*** class definition, so it is simple to add new source in the future.

***InputArgumentProvider*** is used by ***Runner*** class to prepare input arguments and inject them to the task method. 

#### ApiContext and ApiContextProvider

Often plugins are dedicated to communicate with one specific system.
They need to interact with come API.
To make it posible it is needed to have either some specific API client or generic (e.g. REST) client injected into operation method arguments.
In many implementation it had been achieved by introducing many lines of biolerplate code.
To optimize and make generic descibed above actions two classes: ***ApiContext*** and ***ApiContextProvider*** have been interoduced.

**ApiContext** - is a simple class containing all objects related to current session with the API.
By default it contains: ***client*** object and ***credentials*** dictionary.
It should be subclasses and adjusted to store all objetct related to single connection to specific API. 
    
**ApiContextProvider** - role of this class is to return proper ***ApiContext*** object based on input parameters.
It can be done using ***get_api_ctx*** method.
***ApiContextProvider*** object is created and used by ***Runner*** to inject proper ***ApiContext*** into operation method arguments.
***Runner*** gets all input parameters for operation method using ***InputArgumentProvider*** and then runs ***get_api_ctx*** method from ***ApiContextProvider*** (only if this class has been specified) passing obtained arguments.
This invocation should return proper ***ApiContext*** object and ***Runner*** will inject it to operation method.

Of course ***ApiContextProvider*** should be subclassed for each specific API and proper subclass should be specified with ***run_with*** usage. 

#### Runner

Main class enables customization of operation method execution process and dependency injection for it.
***Runner*** is used directly by ***run_with*** decorator to execute decorated method.
***Runner*** uses ***InputArgumentProvider*** and ***ApiContextProvider*** to prepare proper input parameters for operation method invocation.
It has also assigned proper ***InputArgumentResolver*** class (then used by ***InputArgumentProvider***).

Main features of ***Runner*** class are:
* preparation and injection of operation method input parameters
* control of operation method execution

Construction of ***Runner*** takes 4 arguments:
* **ctx** - instance of ***CloudifyContext***
* **resolving_rules** - list of rules describing variable for which values should be resolved using relationships
* **sources_order** - order of input arguments sources 
* **api_ctx_provider_cls** (*optional*) - subclass of ***ApiContextProvider*** (in case when interaction with external API is needed).

***Runner*** class has 2 most important methods:
* **run** - performs all preparation steps (preparation of input arguments, preparation of ***ApiContext*** if needed) and executes operation method calling ***do_run***.   
* **do_run** - only executes operation method assuming that all preparation steps are completed (in fact it is called by ***run*** method).

This kind of separation has been introduced to enable implementation of custom features related to running operation method by subclassing.

Each runner class should also have 2 constants defining which input provider and input resolver classes should be used:
* **RESOLVER_CLASS**
* **INPUTS_PROVIDER_CLASS**

Also ***Runner*** class should be subclasses. In ***cloudify_plugin_tools*** we have 2 default implementations:
* **RelationshipTaskRunner** - should be used for operations assigned to one of relationship interfaces
* **InstanceTaskRunner** - should be used for operations assigned to one of node interfaces

## Common API related part (cloudify_sdk_tools)

**cloudify_sdk_tools** package contains common classes and methods useful for comminucation with (REST) APIs.
There are:

* **RestSDKClient** (implemented in ***rest*** module) - generic REST client.
It uses REST requests templates and ***rest_sdk*** library from ***cloudify-utilities-plugin*** to render and send them.
It constructor takes API credentials and requests common parameters (parameters which will be used to render all requests) as input arguments.
Public method is ***call*** responsible for sending REST request. It takes 3 input parameters:
    * ***object_name*** - name of resource (name of subdirectory in main *templates* directory)
    * ***method_name*** - name of method / request which should be sent for given kind of resource (name YAML file in given of subdirectory of main *templates* directory)
    * ***params*** - dictionary of parameters which (merged with common parameters passed to constructor) will be used to render REST request template before sending 
* **with_arguments** decorator (implemented in ***utils*** module) - decorator checking if all variables names (passed as list in parameter) has been passed for method invocation.
It has been designed to be used by resource API classes and subclasses in packages related to given API, to simplify parameters processing.   
