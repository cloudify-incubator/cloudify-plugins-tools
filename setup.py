from setuptools import setup

# TODO use cloudify-utilities-plugin-sdk when it will be released
REST_PLUGIN_URL = 'https://github.com/cloudify-incubator/' \
                  'cloudify-utilities-plugin/archive/1.10.0.tar.gz' \
                  '#egg=cloudify-utilities-plugin-1.10.0'

try:
    import cloudify_rest  # noqa
except ImportError:
    import pip
    if hasattr(pip, 'main'):
        pip.main(['install', '"{}"'.format(REST_PLUGIN_URL)])
    else:
        from pip._internal import main as _main
        _main(['install', '"{}"'.format(REST_PLUGIN_URL)])

setup(
    name='cloudify-plugins-tools',
    version='0.1.0',
    author='Krzysztof Bijakowski',
    author_email='krzysztof.bijakowski@cloudify.co',
    description='(Dependency injection) framework and tools simplifying '
                'cloudify plugin develpment and reducing number '
                'of boilerplate code lines ',
    packages=[
        'cloudify_plugin_tools',
        'cloudify_sdk_tools',
    ],
    license='proprietary',
    zip_safe=False,
    install_requires=[
        'cloudify-plugins-common>=4.2',
        'cloudify-utilities-plugin==1.10.0'
    ],
    dependency_links=[REST_PLUGIN_URL]
)
