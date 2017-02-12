filebot -script fn:amc \
-non-strict "/etc/sabnzbd/Downloads/complete/movies" \
-no-xattr \
--output "/nfs/diskstation/movies" \
--action move \
--conflict auto \
--log-file /etc/filebot/amc.log \
--def excludeList=/etc/filebot/amc.txt \
--def plex=127.0.0.1:UGsPcVjH8fwDVkPRB8Sq \
--def clean=y \
--def movieFormat="{n} ({y})/{n} ({y}){' CD'+pi}" \
--def ut_label=movie \
--def "ignore=_UNPACK"