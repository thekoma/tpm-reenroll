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
_root_dm=$(findmnt -n -o SOURCE / | cut -d'[' -f1)
_device=$(cryptsetup status "$_root_dm" 2>/dev/null | awk '/device:/{print $2}')
if [ -n "$_device" ] && cryptsetup luksDump "$_device" 2>/dev/null | grep -q "tpm2"; then
    echo ""
    echo "TPM2 enrollment detected on $_device."
    echo "The service is enabled and will handle re-enrollment automatically."
    echo "To customize, create /etc/tpm-reenroll.conf with DEVICE and PCRS."
    echo ""
else
    echo ""
    echo "No TPM2 enrollment found. To enable TPM auto-unlock:"
    echo "  sudo systemd-cryptenroll /dev/YOUR_LUKS_DEVICE --tpm2-device=auto --tpm2-pcrs=7"
    echo "Then create /etc/tpm-reenroll.conf with DEVICE and PCRS."
    echo ""
fi

%preun
systemctl disable tpm-reenroll.service 2>/dev/null || true

%files
%license LICENSE
%{_bindir}/tpm-reenroll
%{_unitdir}/tpm-reenroll.service
%config %{_sysconfdir}/tpm-reenroll.conf.example
