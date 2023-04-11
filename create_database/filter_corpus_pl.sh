# Extra letters: ąćęłńóśźż and ĄĆĘŁŃÓŚŹŻ
LC_ALL="C.UTF-8" awk '{$1=$1;print $0}' | \
 grep -E "^([^ ]+ ){10}" | grep -Ev "([^ ]+ ){50,}" | \
 grep -Ev "[^ ]{26,}" | \
 grep -Ev "(^| )([A-ZĄĆĘŁŃÓŚŹŻ][^ ]* ){2}[A-ZĄĆĘŁŃÓŚŹŻ][^ ]*" | \
 grep -Ev "(^| )[A-ZĄĆĘŁŃÓŚŹŻ]{4,}.* [A-ZĄĆĘŁŃÓŚŹŻ]{4,}( |$)" | \
 grep -Ev "(^| )([^a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ ]+ ){2}[^a-ząćęłńóśźżA-ZĄĆĘŁŃÓŚŹŻ ]+( |$)" | \
 grep -Ev "(^| )([^ ] ){2}[^ ]( |$)" |
 grep -Ev "(\\\\[^\\\\]*){3,}" | grep -v "�" | \
 grep -v "[õû]" | \
 grep -Ev "&[a-z#0-9]{2,8};" | \
 sort --parallel="$(nproc)" -T ~/tmp -S10% --compress-program=pigz -u
