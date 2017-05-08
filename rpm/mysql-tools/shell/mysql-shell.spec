# Copyright (c) 2016, Oracle and/or its affiliates. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

%{?with_static: %global static 1}
%{?with_ssl:  %global with_ssl_static %{with_ssl}}
%{!?with_ssl: %global with_ssl_static bundled}

%if 0%{?with_ssl:1}
%global with_ssl_static %{with_ssl}
%else
%global with_ssl_static bundled
%endif

#%define python2_version 2.7
#using python : /usr/bin/python2 : /usr/include/python%{python2_version} : : : : ;

# define v8_includedir and v8_libdir for rpmbuild when building static

Summary:        Command line shell and scripting environment for MySQL
Name:           mysql-shell
Version:        1.0.9
Release:        1%{?dist}
License:        GPLv2
URL:            http://dev.mysql.com/
Source0:        https://cdn.mysql.com/Downloads/%{name}-1.0.9-src.tar.gz
BuildRequires:  cmake
#%if 0%{!?with_boost:1}
BuildRequires:  boost-devel
#%endif
%if 0%{!?with_protobuf:1}
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
%endif
#BuildRequires:  libedit-devel  FIXME only if -DWITH_EDITLINE=system
BuildRequires:  python-devel
%if 0%{!?static}
BuildRequires:  mysql-devel
BuildRequires:  openssl-devel
#BuildRequires:  v8-devel
#BuildRequires:  v8-python
%endif
%description
MySQL query and administration shell client and framework.

%prep
%setup -q -n %{name}-1.0.9-src

%build
rm -rf build && mkdir build && cd build
cmake .. \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
%if "%{_lib}" == "lib64"
    -DLIB_SUFFIX=64 \
%endif
%if 0%{?static}
    -DWITH_SSL=%{with_ssl_static} \
    -DMYSQLCLIENT_STATIC_LINKING=ON \
    -DV8_INCLUDE_DIR=%{v8_includedir} \
    -DV8_LIB_DIR=%{v8_libdir} \
%else
    -DWITH_SSL=system \
    -DMYSQLCLIENT_STATIC_LINKING=ON \
%endif
%if 0%{?with_boost:1}
    -DBOOST_ROOT=%{with_boost} \
    -DBoost_NO_SYSTEM_PATHS:BOOL=TRUE \
%endif
%if 0%{?with_protobuf:1}
    -DWITH_PROTOBUF=%{with_protobuf} \
%endif
%if 0%{?with_gtest:1}
    -DWITH_TESTS=ON \
    -DWITH_GTEST=%{with_gtest} \
%endif
%if 0%{?with_connector_python:1}
    -DWITH_CONNECTOR_PYTHON="%{with_connector_python}" \
%endif
    -DHAVE_PYTHON=1 \

#-D_GLIBCXX_USE_CXX11_ABI=0\

# Supported V8 versions are limited, disable
# V8 in non static for now.
# -DV8_INCLUDE_DIR=%{_includedir}/v8 \
# -DV8_LIB_DIR=%{_libdir} \
# Shared linking don't work
# -DMYSQLCLIENT_STATIC_LINKING=ON \

make %{?_smp_mflags}

%install
cd build
make DESTDIR=%{buildroot} install
rm -rf %{buildroot}%{_includedir}
rm -f %{buildroot}%{_prefix}/lib/*.{so,a}
rm -f %{buildroot}%{_datadir}/mysqlsh/{COPYING.txt,README}

%files
# FIXME EL6 doesn't like 'license' macro here, so we use 'doc'
%doc COPYING.txt
%doc README
%{_bindir}/mysqlsh
%{_bindir}/mysqlprovision

%changelog
* Mon Mar 13 2017 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 1.0.8-1
- Updated for mysqlprovision build change

* Thu Sep 01 2016 Balasubramanian Kandasamy <balasubramanian.kandasamy@oracle.com> - 1.0.5-0.1
- Updated for 1.0.5 labs release

* Wed Mar 23 2016 Alfredo Kojima <alfredo.kengi.kojima@oracle.com> - 1.0.3-1
- updated for 1.0.3, bug fixes

* Mon Mar 14 2016 Kent Boortz <kent.boortz@oracle.com> - 1.0.2.8-1
- initial package
