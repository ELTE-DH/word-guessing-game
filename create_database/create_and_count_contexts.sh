LC_ALL="C.UTF-8" parallel --pipe "python3 create_word_contexts.py -l $1 -r $2 -s $3 -m $4 -e $6 -n $7" | \
 sort --parallel="$(nproc)" -T ~/tmp -S10% --compress-program=pigz | ./uniq_2nd_field.sh | ./uniq_3rd_field.sh | \
 ./uniq_c_1st_field.sh "$5"
