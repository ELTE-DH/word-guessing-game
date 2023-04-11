# Extra letters: íűáéúőóüö and ÍŰÁÉÚŐÓÜÖ
LC_ALL="C.UTF-8" awk '{$1=$1;print $0}' | \
 grep -E "^([^ ]+ ){10}" | grep -Ev "([^ ]+ ){50,}" | \
 grep -Ev "[^ ]{26,}" | \
 grep -Ev "(^| )([A-ZÍŰÁÉÚŐÓÜÖ][^ ]* ){2}[A-ZÍŰÁÉÚŐÓÜÖ][^ ]*" | \
 grep -Ev "(^| )[A-ZÍŰÁÉÚŐÓÜÖ]{4,}.* [A-ZÍŰÁÉÚŐÓÜÖ]{4,}( |$)" | \
 grep -Ev "(^| )([^a-zíűáéúőóüöA-ZÍŰÁÉÚŐÓÜÖ ]+ ){2}[^a-zíűáéúőóüöA-ZÍŰÁÉÚŐÓÜÖ ]+( |$)" | \
 grep -Ev "(^| )([^ ] ){2}[^ ]( |$)" |
 grep -Ev "(\\\\[^\\\\]*){3,}" | grep -v "�" | \
 grep -Ev "[õû]" | \
 grep -Ev "&[a-z#0-9]{2,8};" | \
 sort --parallel="$(nproc)" -T ~/tmp -S10% --compress-program=pigz -u
