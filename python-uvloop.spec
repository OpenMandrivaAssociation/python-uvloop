%define module uvloop
%bcond test 0
# NOTE Tests are flaky, disabled for abf

Name:		python-uvloop
Version:	0.22.1
Release:	1
Summary:	Fast implementation of asyncio event loop on top of libuv
License:	MIT AND Apache-2.0
Group:		Development/Python
URL:		https://pypi.org/project/uvloop/
Source0:	https://files.pythonhosted.org/packages/source/u/%{module}/%{module}-%{version}.tar.gz

BuildSystem:	python
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(libuv)
BuildRequires:	python%{pyver}dist(aiohttp)
BuildRequires:	python%{pyver}dist(cython)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(pyopenssl)
BuildRequires:	python%{pyver}dist(psutil)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(wheel)
%if %{with tests}
BuildRequires:	python%{pyver}dist(pluggy)
BuildRequires:	python%{pyver}dist(pytest)
BuildRequires:	python%{pyver}dist(sniffio)
%endif

%description
Fast implementation of asyncio event loop on top of libuv

########################
%prep
%autosetup -n %{module}-%{version} -p1
# Remove bundled egg-info
rm -rf %{module}.egg-info

# always use cython to generate code (and generate a build dependency on it)
sed -i -e "/self.cython_always/s/False/True/" setup.py
# use system libuv
sed -i -e "/self.use_system_libuv/s/False/True/" setup.py
# no 3rd-party stuff
rm -vrf vendor/
# remove linter from deps
sed -r -i \
    -e "s/^([[:blank:]]*)([\"'](flake8|pycodestyle|mypy)\b)/\\1# \\2/" \
    -e 's/~=/>=/' \
    pyproject.toml

########################
%build
export LDFLAGS="%{ldflags} -lpython%{py_ver}"
%py_build

########################
%install
%py_install

# remove sources and headers, we dont need those
find '%{buildroot}%{python_sitearch}' -type f -name '*.[ch]' -print -delete

########################
%if %{with test}
%check
export CI=true
export PYTHONPATH="%{buildroot}%{python_sitearch}:${PWD}"
ignore="${ignore-} --ignore=tests/test_sourcecode.py"

# Don’t import the “un-built” uvloop from build dir
mkdir -p _empty
cd _empty
ln -s ../tests/ .

# run tests, disable broken tests.
# https://github.com/MagicStack/uvloop/issues/596
# https://github.com/MagicStack/uvloop/pull/604
pytest -v ${ignore-} -k "not test_getaddrinfo_1 and not test_getaddrinfo_2 and not test_getaddrinfo_5 and not test_getaddrinfo_6 and not test_getaddrinfo_8 and not test_getaddrinfo_9 and not test_getaddrinfo_11 and not test_create_unix_server_1"
%endif

########################
%files
%{python_sitearch}/uvloop
%{python_sitearch}/uvloop-*.*-info
%doc README.rst
%license LICENSE-APACHE LICENSE-MIT
