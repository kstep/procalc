
DESTDIR ?= 
PYMODULES ?= $(DESTDIR)/usr/lib/pymodules/python2.5
PREFIX ?= $(DESTDIR)/usr/bin
PYVERSION ?= 2.5

compile:
	python$(PYVERSION) -O -m compileall ./procalc

install: compile
	install -o root -g root -m 0755 ./procalc.py $(PREFIX)/procalc
	install -o root -g root -m 0755 -d $(PYMODULES)/procalc
	for f in `find ./procalc -name "*.pyo"`; do \
		install -o root -g root -m 0644 $$f $(PYMODULES)/$$f; done

uninstall:
	rm -rf $(PYMODULES)/procalc
	rm -f $(PREFIX)/procalc

clean:
	find . -name "*.py[co]" | xargs rm -f 

.PHONY: compile install clean uninstall
