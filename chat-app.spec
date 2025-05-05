Name:           chat-app
Version:        1.0
Release:        1%{?dist}
Summary:        Simple Python chat application

License:        MIT
URL:            https://example.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3
Requires:       python3

%description
A simple Python-based chat application with client-server architecture.

%prep
%setup -q

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/lib/%{name}

# Corrected paths - use the unpacked source directory
install -m 755 %{_builddir}/%{name}-%{version}/src/chat_client.py %{buildroot}/usr/bin/chat-client
install -m 755 %{_builddir}/%{name}-%{version}/src/chat_server.py %{buildroot}/usr/bin/chat-server
install -m 644 %{_builddir}/%{name}-%{version}/src/__init__.py %{buildroot}/usr/lib/%{name}/

%files
/usr/bin/chat-client
/usr/bin/chat-server
/usr/lib/%{name}/__init__.py

%changelog
* Tue May 07 2024 Your Name <your.email@example.com> - 1.0-1
- Initial package