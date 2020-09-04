from setuptools import setup

setup(
    name='cloudify-plugins-tools',
    version='0.1.3',
    author='Krzysztof Bijakowski',
    author_email='krzysztof.bijakowski@cloudify.co',
    description='(Dependency injection) framework and tools simplifying '
                'cloudify plugin development and reducing number '
                'of boilerplate code lines ',
    packages=[
        'cloudify_plugin_tools',
        'cloudify_sdk_tools',
    ],
    license='proprietary',
    zip_safe=False,
    install_requires=[
        'cloudify-common>=4.6',
        'cloudify-utilities-plugins-sdk==0.0.27'
    ]
)
