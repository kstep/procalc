
DESTDIR ?= 
PYMODULES ?= $(DESTDIR)/usr/lib/pymodules/python2.5
DESKTOP ?= $(DESTDIR)/usr/share/applications/hildon
PREFIX ?= $(DESTDIR)/usr/bin
PYVERSION ?= 2.5

compile:
	python$(PYVERSION) -O -m compileall ./procalc

install: compile
	install -o root -g root -m 0755 ./procalc.py $(PREFIX)/procalc
	install -o root -g root -m 0755 -d $(PYMODULES)/procalc
	for f in `find ./procalc -name "*.pyo"`; do \
		install -o root -g root -m 0644 $$f $(PYMODULES)/$$f; done
	install -o root -g root -m 0644 ./menu/procalc.desktop $(DESKTOP)/procalc.desktop

uninstall:
	rm -rf $(PYMODULES)/procalc
	rm -f $(PREFIX)/procalc
	rm -f $(DESKTOP)/procalc.desktop

clean:
	find . -name "*.py[co]" | xargs rm -f 

.PHONY: compile install clean uninstall
