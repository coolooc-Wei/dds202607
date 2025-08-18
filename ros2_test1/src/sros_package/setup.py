from setuptools import find_packages, setup

package_name = 'sros_package'

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
    maintainer='cislab',
    maintainer_email='567andrew567@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sros_package = sros_package.sros_package:main',
            'kyber_server = sros_package.kyber_server:main',
            'kyber_client_subscriber = sros_package.kyber_client_subscriber:main',
            'kyber = sros_package.kyber:main',
            'Aes = Aes.kyber:main',
        ],
    },
)
