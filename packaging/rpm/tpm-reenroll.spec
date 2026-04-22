Name:           tpm-reenroll
Version:        0.1.0
Release:        1%{?dist}
Summary:        Auto re-enroll TPM2 for LUKS after PCR policy changes
License:        MIT
URL:            https://github.com/thekoma/tpm-reenroll
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       systemd >= 250
Requires:       cryptsetup
Requires:       coreutils
Requires:       util-linux
Requires:       grep

%description
A systemd service that automatically re-enrolls TPM2 for LUKS
when PCR policy changes, e.g. after a Secure Boot dbx update.
Prompts for the LUKS password when re-enrollment is needed.

%prep
%setup -q

%install
make DESTDIR=%{buildroot} PREFIX=/usr install

%post
systemctl daemon-reload
systemctl enable tpm-reenroll.service
echo ""
echo "NOTE: Run 'sudo tpm-reenroll-setup' to configure the service."
echo "The service is enabled but will not run until setup is complete."
echo ""

%preun
systemctl disable tpm-reenroll.service 2>/dev/null || true

%files
%license LICENSE
%{_bindir}/tpm-reenroll
%{_bindir}/tpm-reenroll-setup
%{_unitdir}/tpm-reenroll.service
%config %{_sysconfdir}/tpm-reenroll.conf.example
