# Try to import setuptools (if it fails, the user needs that package)
try: 
    from setuptools import setup, find_packages
except:
    # Custom error (in case user does not have setuptools)
    class DependencyError(Exception): pass
    raise(DependencyError("Missing python package 'setuptools'.\n  pip install --user setuptools"))

import os
# Go to the "about" directory in the package directory
package_name = "txt_to_html"
package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),package_name,"about")
# Convenience function for reading information files
def read(f_name):
    text = []
    with open(os.path.join(package_dir, f_name)) as f:
        for line in f:
            line = line.strip("\n")
            if (len(line.strip()) > 0) and (line[0] != "%"):
                text.append(line)
    return text

if __name__ == "__main__":
    #      Read in the package description files     
    # ===============================================
    package = package_name
    version =read("version.txt")[0]
    description = read("description.txt")[0]
    requirements = read("requirements.txt")
    keywords = read("keywords.txt")
    classifiers = read("classifiers.txt")
    name, email, git_username = read("author.txt")

    # Translate the git requirements to proper requirements.
    dependency_links = [r for r in requirements if "github.com" in r]
    for r in dependency_links:
        try:    pkg_name = r.split("egg=")[1]
        except: raise(DependencyError("GitHub repositories must specify '#egg=<package-name>' at the end."))
        requirements[requirements.index(r)] = pkg_name + " @ git+https://" + r.split("://")[1]

    setup(
        author = name,
        author_email = email,
        name=package,
        packages=find_packages(exclude=[]),
        include_package_data=True,
        install_requires=requirements,
        version=version,
        url = 'https://github.com/{git_username}/{package}'.format(
            git_username=git_username, package=package),
        download_url = 'https://github.com/{git_username}/{package}/archive/{version}.tar.gz'.format(
            git_username=git_username, package=package, version=version),
        description = description,
        keywords = keywords,
        python_requires = '>=2.7',
        license='MIT',
        classifiers=classifiers
    )
