from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = "2.3.9"

install_requires = [
    "psutil",
    "pycryptodomex",
    "pywin32",
    "pymem",
    "silk-python",
    "pyaudio",
    "requests",
    "pillow",
    "pyahocorasick",
    "flask",
    "lz4",
    "blackboxprotobuf",
    "lxml"
]

setup(
    name="pywxdump",
    author="xaoyaoo",
    version=version,
    author_email="xaoyaoo@gmail.com",
    description="微信信息获取工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xaoyaoo/PyWxDump",
    license='MIT',

    packages=['pywxdump', 'pywxdump.ui', 'pywxdump.wx_info', 'pywxdump.analyzer'],
    package_dir={'pywxdump': 'pywxdump',
                 'pywxdump.wx_info': 'pywxdump/wx_info',
                 'pywxdump.analyzer': 'pywxdump/analyzer',
                 'pywxdump.ui': 'pywxdump/ui',
                 },

    package_data={
        'pywxdump': ['version_list.json', 'ui/templates/*']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6, <4',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'wxdump = pywxdump.cli:console_run',
        ],
    },
    setup_requires=['wheel']
)
