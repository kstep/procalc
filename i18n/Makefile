
DESTDIR ?= 
I18N ?= $(DESTDIR)/usr/share/locale

compile: en/LC_MESSAGES/procalc.mo ru/LC_MESSAGES/procalc.mo

procalc.pot: ../procalc/*.py
	pygettext -p . -d procalc ../procalc

ru/LC_MESSAGES/procalc.po en/LC_MESSAGES/procalc.po: procalc.pot
	test -e $@ && msgmerge -U $@ procalc.pot || msginit -i procalc.pot -l $(subst /LC_MESSAGES/procalc.po,,$@) -o $@

en/LC_MESSAGES/procalc.mo: en/LC_MESSAGES/procalc.po
	msgfmt -o $@ $<

ru/LC_MESSAGES/procalc.mo: ru/LC_MESSAGES/procalc.po
	msgfmt -o $@ $<

install: compile
	for f in `find . -name procalc.mo`; do \
		install -o root -g root -m 0644 $$f $(I18N)/$$f; done

clean:
	rm -f ./procalc.pot ./ru/LC_MESSAGES/procalc.mo ./en/LC_MESSAGES/procalc.mo

.PHONY: compile clean install
