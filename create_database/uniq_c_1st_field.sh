#!/bin/bash

# Count lines (as uniq -c) based on the first field (TAB separated) and print only groups larger than
# the specified limit ($1)

uniq_c_1st_field="mawk -v limit=$1 -F\$'\t' -v OFS=\$'\t' 'BEGIN {gl=getline; prev_field=\$1; prev_line[1]=\$0; count=1}
                                                           { if (prev_field != \$1) {
                                                                 if (count >= limit) {
                                                                     for (i in prev_line) {
                                                                         print prev_line[i];
                                                                         delete prev_line[i];
                                                                     }
                                                                 } else {
                                                                     for (i in prev_line)
                                                                         delete prev_line[i];
                                                                 }
                                                                 prev_field=\$1;
                                                                 count=0;
                                                             }
                                                             count=count+1;
                                                             if (count < limit) {
                                                                 prev_line[count]=\$0;
                                                             } else {
                                                                 if (count == limit) {
                                                                     for (i in prev_line) {
                                                                         print prev_line[i];
                                                                         delete prev_line[i];
                                                                     }
                                                                 }
                                                                 print \$0;
                                                             }
                                                           }
                                                           END {
                                                               if (count >= limit) {
                                                                   for (i in prev_line) {
                                                                       print prev_line[i];
                                                                   }
                                                               }
                                                           }'"

eval $uniq_c_1st_field
