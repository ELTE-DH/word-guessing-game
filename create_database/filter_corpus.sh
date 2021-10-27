LC_ALL="C.UTF-8" awk '{$1=$1;print $0}' | \
 egrep "^([^ ]+ ){10}" | egrep -v "([^ ]+ ){50,}" | \
 egrep -v "[^ ]{26,}" | \
 egrep -v "(^| )([A-ZÍŰÁÉÚŐÓÜÖ][^ ]* ){2}[A-ZÍŰÁÉÚŐÓÜÖ][^ ]*" | \
 egrep -v "(^| )[A-ZÍŰÁÉÚŐÓÜÖ]{4,}.* [A-ZÍŰÁÉÚŐÓÜÖ]{4,}( |$)" | \
 egrep -v "(^| )([^a-zíűáéúőóüöA-ZÍŰÁÉÚŐÓÜÖ ]+ ){2}[^a-zíűáéúőóüöA-ZÍŰÁÉÚŐÓÜÖ ]+( |$)" | \
 egrep -v "(^| )([^ ] ){2}[^ ]( |$)" |
 egrep -v "(\\\\[^\\\\]*){3,}" | grep -v "�" | \
 grep -v "[õû]" | \
 egrep -v "&[a-z#0-9]{2,8};" | \
 sort --parallel=$(nproc) -T ~/tmp -S10% --compress-program=pigz -u
