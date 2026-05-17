from setuptools import setup, find_packages


with open('requirements.txt') as req:
    requirements = req.read().splitlines()


with open('README.md', encoding='utf-8') as f:
    readme = f.read()


setup(name='prom2notify',
      version='0.2.0',
      description='Multi-backend alert relay for Prometheus Alertmanager (Teams, Slack, Discord, Telegram, Generic Webhooks)',
      long_description=readme,
      long_description_content_type='text/markdown',
      python_requires='>=3.9',
      install_requires=requirements,
      extras_require={
          'dev': [
              'pytest',
              'pytest-cov',
          ],
      },
      scripts=[
          'bin/prom2notify',
          'bin/prom2notify_uwsgi'
      ],
      package_data={
          '': ['*.ini', '*.j2', '*.ico', '*.yml'],
      },
      include_package_data=True,
      data_files=[
          ('/usr/local/etc/prom2notify', ['bin/wsgi.py'])
      ],
      url='https://github.com/zyqtron/prom2notify',
      author='zyqtron',
      author_email='webmasteur1334@gmail.com',
      license='MIT',
      packages=find_packages(exclude=('tests', 'docs')),
      keywords='prometheus alertmanager teams slack discord telegram webhook',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Communications :: Chat',
          'Topic :: System :: Monitoring',
          'Topic :: Utilities',
      ],
      zip_safe=False)
