from setuptools import find_packages, setup

package_name = 'test_1_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='andrew567',
    maintainer_email='andrew567@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'test = test_1_py.test:main',
            'talker = test_1_py.publisher_test:main',
            'listener = test_1_py.subscriber_test:main',
            'service_member_function = test_1_py.service_member_function:main',
            'client_member_function = test_1_py.client_member_function:main',
        ],
    },
)
