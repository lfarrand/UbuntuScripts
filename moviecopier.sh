filebot -script fn:amc \
-non-strict "/etc/sabnzbd/Downloads/complete/movies" \
-no-xattr \
--output "/mnt/nfs/diskstation/movies" \
--action move \
--conflict auto \
--def excludeList=/etc/filebot/amc.txt \
--def plex=127.0.0.1:zqtrKvEQunUnyr5vHn36 \
--def clean=y \
--def movieFormat="{n} ({y})/{n} ({y}){' CD'+pi}" \
--def ut_label=movie \
--def "ignore=_UNPACK"
