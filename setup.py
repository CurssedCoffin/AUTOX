from setuptools import setup

setup(name='AUTOX',
    version='1',
    description='Auto extract compressed files under folder, with windows right context menu.',
    url='',
    author='CurssedCoffin',
    author_email='',
    license='',
    packages=['AUTOX', 'AUTOX/cmd'],
    entry_points={'console_scripts': [
        'autox_setup=AUTOX.cmd.register_windows:register_context_menu',
        'autox_show_pass_path=AUTOX.cmd.pass_manager:show_pass_path',
        'autox_show_pass=AUTOX.cmd.pass_manager:show_pass',
        'autox_add_pass=AUTOX.cmd.pass_manager:add_pass',
        'autox_empty_pass=AUTOX.cmd.pass_manager:empty_pass',
    ]},
    zip_safe=False,
    install_requires = [i for i in open("requirements.txt", "r").read().strip().splitlines() if i != ''],
    package_data={"": ["bin/windows/7z.dll", "bin/windows/7z.exe"]},
    include_package_data=True,
)
