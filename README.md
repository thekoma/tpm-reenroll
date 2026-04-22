# tpm-reenroll

Auto re-enroll TPM2 for LUKS when PCR policy changes.

PCR 7 (Secure Boot policy) can change when the Secure Boot database is updated, for example after a Windows Update that modifies the dbx revocation list, a firmware update, or a `fwupdmgr update` on Linux. When this happens, the TPM refuses to unseal the LUKS key and you get a password prompt.

**tpm-reenroll** is a systemd service that detects this mismatch and asks for your LUKS password once to re-enroll the TPM. Next boot, auto-unlock works again. No key files stored on disk.

## How it works

1. At every boot, the systemd service checks if TPM unlock failed
2. If it did, it prompts for your LUKS password via `systemd-ask-password`
3. It wipes the old TPM enrollment and re-enrolls with current PCR values
4. Next boot unlocks automatically again

This typically happens 1-2 times per year (dbx updates, firmware updates), not on every reboot.

## Requirements

- Linux with systemd >= 250
- TPM 2.0
- LUKS2-encrypted root
- Secure Boot (recommended, required for meaningful PCR 7)

## Install

### Arch Linux (AUR)

The PKGBUILD is in `packaging/aur/`. To install from a local build:

```bash
cd packaging/aur
makepkg -si
sudo tpm-reenroll-setup
```

### From source

```bash
git clone https://github.com/thekoma/tpm-reenroll.git
cd tpm-reenroll
make check       # verify dependencies
sudo make install
sudo tpm-reenroll-setup
```

### DEB / RPM

See `packaging/deb/` and `packaging/rpm/` for build files.

## Configuration

After running `tpm-reenroll-setup`, the config lives at `/etc/tpm-reenroll.conf`:

```bash
DEVICE=/dev/disk/by-uuid/your-uuid-here
PCRS=7
```

### PCR reference

| PCR | Measures | Changes when | Notes |
|-----|----------|-------------|-------|
| 0 | Firmware code | Firmware update | Stable, good baseline |
| 1 | Firmware config | BIOS settings, hardware changes | eGPU breaks this |
| 2 | Option ROM code | Add/remove GPU with option ROM | Rarely useful |
| 3 | Option ROM config | Option ROM settings | Rarely useful |
| 4 | Boot loader code | Kernel/bootloader update | Breaks often on rolling distros |
| 5 | Boot loader config | GPT/EFI variable changes | Fragile |
| 7 | Secure Boot policy | SB on/off, key db/dbx changes | Best baseline |
| 11 | Unified Kernel Image | UKI update | UKI setups only |

### When does PCR 7 actually change?

| Event | Changes PCR 7? | Frequency |
|-------|---------------|-----------|
| Normal Linux ↔ Windows reboot | **No** | Never |
| Windows Update modifies dbx | **Yes** | ~1-2x/year (automatic from Jan 2026) |
| `fwupdmgr update` modifies dbx | **Yes** | When you update firmware from Linux |
| UEFI firmware update | **Possible** | Depends on vendor |
| `sbctl enroll-keys` | **Yes** | Only if you recreate keys |
| Toggle Secure Boot on/off | **Yes** | Manual only |
| SBAT update | **No** | N/A (separate mechanism) |

### Recommended PCR sets

- **Dual-boot**: `PCRS=7` with tpm-reenroll (this tool)
- **Single-boot, no eGPU**: `PCRS=0+7`
- **Single-boot, with eGPU**: `PCRS=7`
- **Maximum convenience**: `PCRS=` (empty, TPM-presence only)

## Security

This tool stores **no key material on disk**. When re-enrollment is needed, it prompts for your LUKS password via `systemd-ask-password` (the same mechanism used by systemd at boot).

**What this protects against:**
- Disk removed and read on another machine (LUKS encryption)
- Secure Boot bypass (PCR 7 changes, TPM refuses to unseal)
- Casual physical access

**What this does NOT protect against:**
- Root attacker on the running system (they already have all your data via the mounted filesystem)
- Sophisticated evil maid with extended physical access

**For stronger protection**, consider adding a TPM PIN (`systemd-cryptenroll --tpm2-with-pin=yes`) or a FIDO2 key as a complementary LUKS slot (`systemd-cryptenroll --fido2-device=auto`).

## Complementary: FIDO2 / YubiKey

You can add a hardware key as an additional LUKS unlock method alongside TPM:

```bash
sudo systemd-cryptenroll /dev/your-device --fido2-device=auto
```

This gives you three unlock methods:
- **Slot 0**: Password (emergency fallback)
- **Slot 1**: TPM2 (automatic, managed by tpm-reenroll)
- **Slot 2**: FIDO2 key (physical touch, always works regardless of PCR state)

## Testing

To verify the service works, wipe the TPM slot before rebooting:

```bash
# Remove the TPM enrollment (will ask for LUKS password)
sudo systemd-cryptenroll /dev/your-device --wipe-slot=tpm2

# Reboot — you'll get a password prompt since there's no TPM token
sudo reboot
```

After boot:
1. Type your LUKS password at the boot prompt (TPM slot is gone, so this is expected)
2. The `tpm-reenroll` service detects the missing token and asks for your password a second time
3. It re-enrolls the TPM with your configured PCRs
4. Next reboot should unlock automatically without a password

You can verify the enrollment worked:

```bash
sudo cryptsetup luksDump /dev/your-device | grep tpm2-hash-pcrs
```

## Uninstall

If installed via AUR/package manager:

```bash
paru -R tpm-reenroll
```

If installed from source:

```bash
sudo make uninstall
```

## License

MIT
