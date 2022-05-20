Usage:

for i in dane pka; do
	gpg --export --export-options export-${i},export-minimal $KEY | \
	zonetonsupdate.py | \
	nsupdate -k ${PATH_TO_KEY}
done
