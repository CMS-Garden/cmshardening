#!/usr/bin/env bash
shopt -s globstar

MESSAGES_FILE=messages.po
#LOCALES="en_US de_DE"
LOCALES=en_US

xgettext -d hardening -o locale/$MESSAGES_FILE -kT_ -D . **/*.py *.py
for L in $LOCALES; do
  mv locale/$L/LC_MESSAGES/hardening_messages.po locale/$L/LC_MESSAGES/hardening_messages_old.po
  msginit --no-translator --locale=$L -i locale/$MESSAGES_FILE -o locale/$L/LC_MESSAGES/hardening_messages_new.po
  msgmerge locale/$L/LC_MESSAGES/hardening_messages_old.po locale/$L/LC_MESSAGES/hardening_messages_new.po >locale/$L/LC_MESSAGES/hardening_messages.po
  rm locale/$L/LC_MESSAGES/hardening_messages_old.po
  rm locale/$L/LC_MESSAGES/hardening_messages_new.po
done
