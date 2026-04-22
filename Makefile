PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
UNITDIR ?= /usr/lib/systemd/system
CONFDIR ?= /etc

.PHONY: install uninstall check

check:
	@echo "Checking dependencies..."
	@command -v systemd-cryptenroll >/dev/null || (echo "MISSING: systemd-cryptenroll" && exit 1)
	@command -v cryptsetup >/dev/null || (echo "MISSING: cryptsetup" && exit 1)
	@command -v logger >/dev/null || (echo "MISSING: logger (util-linux)" && exit 1)
	@command -v findmnt >/dev/null || (echo "MISSING: findmnt (util-linux)" && exit 1)
	@echo "All dependencies found."

install:
	install -Dm755 tpm-reenroll $(DESTDIR)$(BINDIR)/tpm-reenroll
	install -Dm755 tpm-reenroll-setup $(DESTDIR)$(BINDIR)/tpm-reenroll-setup
	install -Dm644 tpm-reenroll.service $(DESTDIR)$(UNITDIR)/tpm-reenroll.service
	install -Dm644 tpm-reenroll.conf.example $(DESTDIR)$(CONFDIR)/tpm-reenroll.conf.example

uninstall:
	-systemctl disable tpm-reenroll.service 2>/dev/null
	rm -f $(DESTDIR)$(BINDIR)/tpm-reenroll
	rm -f $(DESTDIR)$(BINDIR)/tpm-reenroll-setup
	rm -f $(DESTDIR)$(UNITDIR)/tpm-reenroll.service
	rm -f $(DESTDIR)$(CONFDIR)/tpm-reenroll.conf.example
	@echo "NOTE: /etc/tpm-reenroll.conf not removed. Delete manually if desired."
